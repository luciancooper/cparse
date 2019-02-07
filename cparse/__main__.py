import sys,os,argparse
from .util import cli_warning,cli_color,reduce

def path_arg(path):
    path = os.path.normcase(path)
    if not os.path.isabs(path):
        path = os.path.normpath(os.path.join(os.getcwd(),path))
    if not os.path.exists(path):
        cli_warning("path '{}' does not exist".format(path))
        exit(1)
    return path


# ============================================ Tree ============================================ #

def _tree(args):
    # path, format, (pattern | regexp | filetype)
    path = path_arg(args.path)
    print(cli_color(path,36),file=sys.stderr)
    from .fpath import File,splitpath
    from .tree import maketree,fileiter
    files = sorted([File(f,os.path.join(path,f)) for f in fileiter(path)])
    if args.hidden == False:
        files = [f for f in files if not f.hidden]
    if args.pattern is not None:
        files = [f for f in files if f.is_match(args.pattern)]
    elif args.regexp is not None:
        files = [f for f in files if f.is_regexp(args.regexp)]
    elif args.filetype is not None:
        files = [f for f in files if f.is_ftype(args.filetype)]
    if args.include != None:
        include = [splitpath(p) for p in args.include]
        files = [f for f in files if any(f.inpath(x) for x in include)]
    if args.exclude != None:
        exclude = [splitpath(p) for p in args.exclude]
        files = [f for f in files if not any(f.inpath(x) for x in exclude)]
    isatty = sys.stdout.isatty()
    ftree = maketree(files,fmt=(lambda f: f.fmt(args.format,cli=isatty)))
    print('\n'.join(['.']+ftree),file=sys.stdout)


# ============================================ ls ============================================ #

def _ls(args):
    # path, recursive, format
    path = path_arg(args.path)
    print(cli_color(path,36),file=sys.stderr)
    from .fpath import File
    from .tree import ls
    flist = sorted([File(f,os.path.join(path,f)) for f in ls(path,args.recursive)])
    if args.hidden == False:
        flist = [f for f in flist if not f.hidden]
    isatty = sys.stdout.isatty()
    for f in flist:
        print(f.fmt(args.format,cli=isatty),file=sys.stdout)

# ============================================ Py ============================================ #

def _py(args):
    path = path_arg(args.path)
    from .tree import fileiter,filter_ftypes
    from .pyparse import parse_pyfile
    if os.path.isdir(path):
        files = [os.path.join(path,f) for f in filter_ftypes(fileiter(path),['py'])]
        print("{} python files found".format(len(files)),file=sys.stderr)
        for f in files:
            print("parsing '{}'".format(f),file=sys.stderr)
            print("\n# file: '{}'\n".format(f),file=sys.stdout)
            for l in parse_pyfile(f):
                print(l,file=sys.stdout)
        return
    if not path.endswith('.py'):
        print("'{}' is not a python source file".format(path),file=sys.stderr)
        return
    for l in parse_pyfile(path):
        print(l,file=sys.stdout)


# ============================================ html ============================================ #

def _html(args):
    path = path_arg(args.path)
    print(cli_color("HTML Input Path: {}".format(path),36),file=sys.stderr)
    from .tree import fileiter,filter_ftypes
    from .htmlparse import linktree
    if os.path.isdir(path):
        # search through target directory
        files = [os.path.join(path,f) for f in filter_ftypes(fileiter(path),['html'])]
        print("{} html files found".format(len(files)),file=sys.stderr)
        if len(files) == 0:
            return
        links = reduce(lambda x,y: x+y, [linktree.from_file(f) for f in files])
        print(links.tree(cli=sys.stdout.isatty()),file=sys.stdout)
        return
    if not path.endswith('.html'):
        cli_warning("'{}' is not an html file".format(path))
        return
    links = linktree.from_file(path)
    print(links.tree(cli=sys.stdout.isatty()),file=sys.stdout)


# ============================================ css ============================================ #

def _css(args):
    path = path_arg(args.path)
    if not path.endswith('.css'):
        cli_warning("'{}' is not an css file".format(path))
        return
    print(cli_color("CSS Input Path: {}".format(path),36),file=sys.stderr)
    from .css import CSSFile
    file = CSSFile.from_file(path)
    if args.group:
        file.group_selectors(inplace=True)
    if args.condense:
        file.condense(inplace=True)
    print(repr(file),file=sys.stdout)




# ============================================ Main ============================================ #

def main():
    parser = argparse.ArgumentParser(prog='cparse',description='code parser',epilog='Please consult https://github.com/luciancooper/cparse for further instruction')
    subparsers = parser.add_subparsers(title="Available sub commands",metavar='command')

    # ------------------------------------------------ tree ------------------------------------------------ #

    parser_tree = subparsers.add_parser('tree', help='print file tree',description="File tree command")
    parser_tree.add_argument('path',nargs='?',default=os.getcwd(),help='tree root directory')
    parser_tree.add_argument('-a',dest='hidden',action='store_true',help='include hidden files')
    parser_tree.add_argument('-f','--format',dest='format',type=str,default="%f",help='display format for files')
    parser_tree_filter = parser_tree.add_mutually_exclusive_group(required=False)
    parser_tree_filter.add_argument('-p',dest='pattern',metavar='pattern',help='wild card pattern')
    parser_tree_filter.add_argument('-r',dest='regexp',metavar='regexp',help='regexp match pattern')
    parser_tree_filter.add_argument('-t',dest='filetype',action='append',metavar='filetype',help='file type filter')
    parser_tree.add_argument('-exc','--exclude',dest='exclude',action='append',metavar='path',help='paths to exclude from tree')
    parser_tree.add_argument('-inc','--include',dest='include',action='append',metavar='path',help='paths to include in tree')
    parser_tree.set_defaults(run=_tree)

    # ------------------------------------------------ ls ------------------------------------------------ #

    parser_ls = subparsers.add_parser('ls', help='list files in directory',description="List files command")
    parser_ls.add_argument('path',nargs='?',default=os.getcwd(),help='root directory')
    parser_ls.add_argument('-r',dest='recursive',action='store_true',help='search recursively')
    parser_ls.add_argument('-a',dest='hidden',action='store_true',help='include hidden files')
    parser_ls.add_argument('-f','--format',dest='format',type=str,default="%f",help='display format for files')
    parser_ls.set_defaults(run=_ls)

    # ------------------------------------------------ py ------------------------------------------------ #

    parser_py = subparsers.add_parser('py', help='python code parser',description="python code parser")
    parser_py.add_argument('path',nargs='?',default=os.getcwd(),help='either a directory to search for .py files in, or a .py file')
    #parser_py.add_argument('-a',dest='ask',action='store_true',help='ask to include files')
    #parser_py.add_argument('-r',dest='recursive',action='store_true',help='search root path recursively')
    parser_py.set_defaults(run=_py)


    # ------------------------------------------------ html ------------------------------------------------ #

    parser_html = subparsers.add_parser('html', help='html link parser',description="html link parser")
    parser_html.add_argument('path',nargs='?',default=os.getcwd(),help='either a directory to search for html files in, or a html file')
    #parser_html.add_argument('-a',dest='ask',action='store_true',help='ask to include files')
    #parser_html.add_argument('-r',dest='recursive',action='store_true',help='search root path recursively')
    parser_html.set_defaults(run=_html)

    # ------------------------------------------------ css ------------------------------------------------ #

    parser_css = subparsers.add_parser('css', help='css file parser',description="css code parser")
    parser_css.add_argument('path',help='a css file to parse')
    parser_css.add_argument('-g',dest='group',action='store_true',help='group identical selector property blocks')
    parser_css.add_argument('-c',dest='condense',action='store_true',help='condense redundancies within property blocks')
    parser_css.set_defaults(run=_css)


    # ------------------------------------------------------------------------------------------------ #
    args = parser.parse_args()
    #cli_warning("about to run cparse {}".format(args))
    args.run(args)
