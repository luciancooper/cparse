import sys,os,argparse

# ============================================ Tree ============================================ #

def _tree(args):
    from .tree import maketree,fileiter,filter_match,filter_ftypes,filter_regexp
    files = fileiter(args.path)
    if args.pattern is not None:
        files = filter_match(files,args.pattern)
    elif args.regexp is not None:
        files = filter_regexp(files,args.regexp)
    elif args.filetype is not None:
        files = filter_ftypes(files,args.filetype)
    for l in maketree(files):
        print(l,file=sys.stdout)
    
# ============================================ Py ============================================ #

def _py(args):
    from .tree import fileiter,filter_ftypes
    from .pyparse import parse_pyfile
    if not os.path.exists(args.path):
        print("target path '{}' does not exist".format(args.path),file=sys.stderr)
        return
    if os.path.isdir(args.path):
        files = [os.path.join(args.path,f) for f in filter_ftypes(fileiter(args.path),['py'])]
        print("{} python files found".format(len(files)),file=sys.stderr)
        for f in files:
            print("parsing '{}'".format(f),file=sys.stderr)
            print("\n# file: '{}'\n".format(f),file=sys.stdout)
            for l in parse_pyfile(f):
                print(l,file=sys.stdout)
        return
    if not args.path.endswith('.py'):
        print("'{}' is not a python source file".format(args.path),file=sys.stderr)
        return
    for l in parse_pyfile(args.path):
        print(l,file=sys.stdout)



# ============================================ Main ============================================ #

def main():
    parser = argparse.ArgumentParser(prog='cparse',description='code parser',epilog='Please consult https://github.com/luciancooper/cparse for further instruction')
    subparsers = parser.add_subparsers(title="Available sub commands",metavar='command')

    # ------------------------------------------------ setup ------------------------------------------------ #

    parser_tree = subparsers.add_parser('tree', help='print file tree',description="File tree command")
    parser_tree.add_argument('path',nargs='?',default=os.getcwd(),help='tree root directory')
    parser_tree_filter = parser_tree.add_mutually_exclusive_group(required=False)
    parser_tree_filter.add_argument('-p',dest='pattern',metavar='pattern',help='wild card pattern')
    parser_tree_filter.add_argument('-r',dest='regexp',metavar='regexp',help='regexp match pattern')
    parser_tree_filter.add_argument('-ft',dest='filetype',action='append',metavar='filetype',help='file type filter')
    parser_tree.set_defaults(run=_tree)

    # ------------------------------------------------ py ------------------------------------------------ #

    parser_py = subparsers.add_parser('py', help='python code parser',description="python code parser")
    parser_py.add_argument('path',nargs='?',default=os.getcwd(),help='either a directory to search for .py files in, or a .py file')
    #parser_py.add_argument('-a',dest='ask',action='store_true',help='ask to include files')
    #parser_py.add_argument('-r',dest='recursive',action='store_true',help='search root path recursively')
    parser_py.set_defaults(run=_py)

    # ------------------------------------------------------------------------------------------------ #
    args = parser.parse_args()
    args.run(args)
