import sys,os,argparse
from .util import cli_warning,cli_cyan,cli_green,reduce


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
    path = path_arg(args.path)
    from .tree import maketree,fileiter,filter_match,filter_ftypes,filter_regexp,fcreated,fmodified
    files = fileiter(path)
    if args.pattern is not None:
        files = filter_match(files,args.pattern)
    elif args.regexp is not None:
        files = filter_regexp(files,args.regexp)
    elif args.filetype is not None:
        files = filter_ftypes(files,args.filetype)
    files,times = list(files),None
    if args.tcreated:
        times = [fcreated(os.path.join(path,x)) for x in files]
    elif args.tmodified:
        times = [fmodified(os.path.join(path,x)) for x in files]
    for l in maketree(files,times):
        print(l,file=sys.stdout)

# ============================================ ls ============================================ #

def _ls(args):
    path = path_arg(args.path)
    from .tree import ls,fmodified,fcreated
    from .util import str_col,timestamp
    flist = ls(path,args.recursive)
    output = flist
    if args.fcreated or args.fmodified:
        output = [""]+output
    if args.fmodified:
        modified = ["Modified"]+[timestamp(fmodified(os.path.join(path,f))) for f in flist]
        output = ["{}  {}".format(*x) for x in zip(str_col(modified,"<"),output)]
    if args.fcreated:
        created = ["Created"]+[timestamp(fcreated(os.path.join(path,f))) for f in flist]
        output = ["{}  {}".format(*x) for x in zip(str_col(created,"<"),output)]
    for l in output:
        print(l,file=sys.stdout)


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
    cli_cyan(f"HTML Input Path: {path}")
    from .tree import fileiter,filter_ftypes
    from .htmlparse import linktree
    if os.path.isdir(path):
        # search through target directory
        files = [os.path.join(path,f) for f in filter_ftypes(fileiter(path),['html'])]
        print("{} html files found".format(len(files)),file=sys.stderr)
        if len(files) == 0:
            return
        links = reduce(lambda x,y: x+y, [linktree.from_file(f) for f in files])
        print(links.tree(),file=sys.stdout)
        return
    if not path.endswith('.html'):
        cli_warning("'{}' is not an html file".format(path))
        return
    links = linktree.from_file(path)
    print(links.tree(),file=sys.stdout)



# ============================================ Main ============================================ #

def main():
    parser = argparse.ArgumentParser(prog='cparse',description='code parser',epilog='Please consult https://github.com/luciancooper/cparse for further instruction')
    subparsers = parser.add_subparsers(title="Available sub commands",metavar='command')

    # ------------------------------------------------ tree ------------------------------------------------ #

    parser_tree = subparsers.add_parser('tree', help='print file tree',description="File tree command")
    parser_tree.add_argument('path',nargs='?',default=os.getcwd(),help='tree root directory')
    parser_tree_filter = parser_tree.add_mutually_exclusive_group(required=False)
    parser_tree_filter.add_argument('-p',dest='pattern',metavar='pattern',help='wild card pattern')
    parser_tree_filter.add_argument('-r',dest='regexp',metavar='regexp',help='regexp match pattern')
    parser_tree_filter.add_argument('-ft',dest='filetype',action='append',metavar='filetype',help='file type filter')
    parser_tree_times = parser_tree.add_mutually_exclusive_group(required=False)
    parser_tree_times.add_argument('-m',dest='tmodified',action='store_true',help='display time last modified')
    parser_tree_times.add_argument('-c',dest='tcreated',action='store_true',help='display time created')
    parser_tree.set_defaults(run=_tree)

    # ------------------------------------------------ ls ------------------------------------------------ #

    parser_ls = subparsers.add_parser('ls', help='list files in directory',description="List files command")
    parser_ls.add_argument('path',nargs='?',default=os.getcwd(),help='root directory')
    parser_ls.add_argument('-r',dest='recursive',action='store_true',help='search recursively')
    parser_ls.add_argument('-c',dest='fcreated',action='store_true',help='list time created')
    parser_ls.add_argument('-m',dest='fmodified',action='store_true',help='list time last modified')
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

    # ------------------------------------------------------------------------------------------------ #
    args = parser.parse_args()
    #cli_warning("about to run cparse {}".format(args))
    args.run(args)
