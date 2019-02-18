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
    # path , hidden , maxdepth , format , (pattern | regexp | filetype) , exclude, include
    path = path_arg(args.path)
    print(cli_color(path,36),file=sys.stderr)
    from .fpath import File,splitpath
    from .tree import maketree,ls_files
    # maxdepth
    files = [File(f,os.path.join(path,f)) for f in ls_files(path,True,args.maxdepth)]
    # hidden
    if args.hidden == False:
        files = [x for x in files if not x.hidden]
    # (pattern | regexp | filetype)
    if args.pattern is not None:
        files = [x for x in files if x.is_match(args.pattern)]
    elif args.regexp is not None:
        files = [x for x in files if x.is_regexp(args.regexp)]
    elif args.filetype is not None:
        files = [x for x in files if x.is_ftype(args.filetype)]

    # exclude, include
    if args.include != None:
        include = [splitpath(p) for p in args.include]
        files = [x for x in files if any(x.inpath(p) for p in include)]
    if args.exclude != None:
        exclude = [splitpath(p) for p in args.exclude]
        files = [x for x in files if not any(x.inpath(p) for p in exclude)]

    # ---- Make Tree ---- #
    ftree = maketree(sorted(files),fmt=args.format,cli=sys.stdout.isatty())
    print('\n'.join(['.']+ftree),file=sys.stdout)


# ============================================ ls ============================================ #

def _ls(args):
    # path , hidden , recursive, maxdepth , limit , format , (pattern | regexp | filetype) , type [f,d] , exclude, include, sort [m,M,c,C]
    path = path_arg(args.path)
    print(cli_color(path,36),file=sys.stderr)
    from .fpath import File,splitpath
    from .tree import ls,ls_files,ls_dirs
    #  (files | dirs)
    lsfn = ls
    if args.type == 'f':
        lsfn = ls_files
    elif args.type == 'd':
        lsfn = ls_dirs
    # recursive, maxdepth
    flist = [File(x,os.path.join(path,x)) for x in lsfn(path,args.recursive,args.maxdepth)]
    # hidden
    if args.hidden == False:
        flist = [x for x in flist if not x.hidden]
    # (pattern | regexp | filetype)
    if args.pattern is not None:
        flist = [x for x in flist if x.is_match(args.pattern)]
    elif args.regexp is not None:
        flist = [x for x in flist if x.is_regexp(args.regexp)]
    elif args.filetype is not None:
        flist = [x for x in flist if x.is_ftype(args.filetype)]

    # exclude, include
    if args.include != None:
        include = [splitpath(p) for p in args.include]
        flist = [x for x in flist if any(x.inpath(p) for p in include)]
    if args.exclude != None:
        exclude = [splitpath(p) for p in args.exclude]
        flist = [x for x in flist if not any(x.inpath(p) for p in exclude)]

    # sort
    if args.sort is not None:
        if args.sort.lower() == 'm':
            flist = sorted(flist,key=lambda x: x.modified,reverse=(args.sort=='m'))
        elif args.sort.lower() == 'c':
            flist = sorted(flist,key=lambda x: x.created,reverse=(args.sort=='c'))
    else:
        flist = sorted(flist)
    # limit
    limit = min(args.limit,len(flist)) if args.limit is not None else len(flist)
    # ---- Print Out ---- #
    isatty = sys.stdout.isatty()
    for x in flist[:limit]:
        print(x.fmt(args.format,cli=isatty),file=sys.stdout)

# ============================================ Py ============================================ #

def _py(args):
    path = path_arg(args.path)
    from .fpath import ftype
    from .tree import ls_files
    from .pyparse import parse_pyfile
    if os.path.isdir(path):
        files = [os.path.join(path,x) for x in ls_files(path) if ftype(x)=='py']
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
    from .fpath import ftype
    from .tree import ls_files
    from .htmlparse import linktree
    if os.path.isdir(path):
        # search through target directory
        files = [os.path.join(path,x) for x in ls_files(path) if ftype(x)=='html']
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
    file.print(file=sys.stdout,linespace=1,stacked=args.stacked)

# ============================================ Main ============================================ #

def main():
    parser = argparse.ArgumentParser(prog='cparse',description='code parser',epilog='Please consult https://github.com/luciancooper/cparse for further instruction')
    subparsers = parser.add_subparsers(title="Available sub commands",metavar='command')

    # ------------------------------------------------ tree ------------------------------------------------ #
    # path , hidden , maxdepth , format , (pattern | regexp | filetype) , exclude, include
    parser_tree = subparsers.add_parser('tree', help='print file tree',description="File tree command")
    parser_tree.add_argument('path',nargs='?',default=os.getcwd(),help='tree root directory')
    parser_tree.add_argument('-a',dest='hidden',action='store_true',help='include hidden files')
    parser_tree.add_argument('-n',dest='maxdepth',type=int,metavar='DEPTH',help='max tree depth');
    parser_tree.add_argument('-fmt',dest='format',type=str,default="%n",metavar='FORMAT',help='display format for tree nodes')
    parser_tree_filter = parser_tree.add_mutually_exclusive_group(required=False)
    parser_tree_filter.add_argument('-wc',dest='pattern',metavar='PATTERN',help='wild card pattern')
    parser_tree_filter.add_argument('-grep',dest='regexp',metavar='REGEXP',help='regular expression to match')
    parser_tree_filter.add_argument('-ft',dest='filetype',action='append',metavar='FILETYPE',help='file type filter')
    parser_tree.add_argument('-exc',dest='exclude',action='append',metavar='PATH',help='paths to exclude from tree')
    parser_tree.add_argument('-inc',dest='include',action='append',metavar='PATH',help='paths to include in tree')
    parser_tree.set_defaults(run=_tree)

    # ------------------------------------------------ ls ------------------------------------------------ #
    # path , hidden , recursive, maxdepth , limit , format , (pattern | regexp | filetype) , type [f,d] , exclude, include, sort [m,M,c,C]
    parser_ls = subparsers.add_parser('ls', help='list files in directory',description="List files command")
    parser_ls.add_argument('path',nargs='?',default=os.getcwd(),help='root directory')
    parser_ls.add_argument('-r',dest='recursive',action='store_true',help='list files recursively')
    parser_ls.add_argument('-n',dest='maxdepth',type=int,metavar='DEPTH',help='max depth if recursive flag is specified')
    parser_ls.add_argument('-a',dest='hidden',action='store_true',help='include hidden files')
    parser_ls.add_argument('-lim',dest='limit',type=int,metavar='COUNT',help='maximum items to list in output')
    parser_ls.add_argument('-fmt',dest='format',type=str,default="%f",metavar='FORMAT',help='display format for listed items')
    parser_ls_filter = parser_ls.add_mutually_exclusive_group(required=False)
    parser_ls_filter.add_argument('-wc',dest='pattern',metavar='PATTERN',help='wild card pattern')
    parser_ls_filter.add_argument('-grep',dest='regexp',metavar='REGEXP',help='regular expression to match')
    parser_ls_filter.add_argument('-ft',dest='filetype',action='append',metavar='FILETYPE',help='file type filter')
    parser_ls.add_argument('-type',dest='type',type=str,metavar='ARG',choices=['f','d'],help='specify to include either files or directories only')
    #parser_ls_type = parser_tree.add_mutually_exclusive_group(required=False)
    #parser_ls_type.add_argument('-files',dest='files',action='store_true', help='include files only')
    #parser_ls_type.add_argument('-d',dest='dirs',action='store_true', help='include directories only')
    parser_ls.add_argument('-sort',dest='sort',type=str,metavar='ARG',choices=['m','M','c','C'],help='sort output list by created or modified timestamp')
    parser_ls.add_argument('-exc',dest='exclude',action='append',metavar='PATH',help='paths to exclude if recursive flag is specified')
    parser_ls.add_argument('-inc',dest='include',action='append',metavar='PATH',help='paths to include if recursive flag is specified')
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
    parser_css.add_argument('-s',dest='stacked',action='store_true',help='stack matching selectors in output')
    parser_css.set_defaults(run=_css)


    # ------------------------------------------------------------------------------------------------ #
    args = parser.parse_args()
    #cli_warning("about to run cparse {}".format(args))
    args.run(args)
