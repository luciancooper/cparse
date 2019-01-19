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
    from .tree import maketree,fileiter,filter_match,filter_ftypes,filter_regexp
    files = fileiter(path)
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
        links = reduce(lambda x,y: x+y, [linktree.from_file(f) for f in files])
        print(links.tree(),file=sys.stdout)
        
        #links = []
        #for f in files:
        #    print("parsing '{}'".format(f),file=sys.stderr)
        #    links += [linktree.from_file(f)]
        #cli_warning("Merging link files not yet implemented")
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
