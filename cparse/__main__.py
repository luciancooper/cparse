import sys,os,argparse

# ============================================ Tree ============================================ #

def _tree(args):
    from .tree import maketree,fileiter,filter_match,filter_ftypes,filter_regexp
    files = fileiter(args.root)
    if args.pattern is not None:
        files = filter_match(files,args.pattern)
    elif args.regexp is not None:
        files = filter_regexp(files,args.regexp)
    elif args.filetype is not None:
        files = filter_ftypes(files,args.filetype)
    for l in maketree(files):
        print(l,file=sys.stdout)
    

# ============================================ Main ============================================ #

def main():
    parser = argparse.ArgumentParser(prog='cparse',description='code parser',epilog='Please consult https://github.com/luciancooper/cparse for further instruction')
    subparsers = parser.add_subparsers(title="Available sub commands",metavar='command')

    # ------------------------------------------------ setup ------------------------------------------------ #

    parser_tree = subparsers.add_parser('tree', help='print file tree',description="File tree command")
    parser_tree.add_argument('root',nargs='?',default=os.getcwd(),help='tree root directory')
    #parser_tree.add_argument('dir',nargs=argparse.REMAINDER,default=os.getcwd(),help='tree directory')
    parser_tree_filter = parser_tree.add_mutually_exclusive_group(required=False)
    parser_tree_filter.add_argument('-p',dest='pattern',metavar='pattern',help='wild card pattern')
    parser_tree_filter.add_argument('-r',dest='regexp',metavar='regexp',help='regexp match pattern')
    parser_tree_filter.add_argument('-ft',dest='filetype',action='append',metavar='filetype',help='file type filter')
    parser_tree.set_defaults(run=_tree)

    # ------------------------------------------------  ------------------------------------------------ #
    args = parser.parse_args()
    args.run(args)
