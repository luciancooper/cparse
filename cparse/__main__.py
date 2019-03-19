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
    # path , (dirflag | fileflag) , hidden , maxdepth , format , [exclude, include] , (pattern | regexp | filetype) , sort
    path = path_arg(args.path)
    print(cli_color(path,36),file=sys.stderr)
    from .fpath import Path,splitpath
    from .tree import maketree
    root = Path('.',path)

    #  (dirflag)
    if args.dirflag:
        ls = root.ls_dirs(args.maxdepth,args.hidden)
    else:
        # [exclude, include]
        inc = None if args.include is None else [splitpath(p) for p in args.include]
        exc = None if args.exclude is None else [splitpath(p) for p in args.exclude]
        # (fileflag)
        if args.fileflag:
            ls = root.ls_files(args.maxdepth,args.hidden,excprune=exc,incprune=inc)
        else:
            ls = root.ls(args.maxdepth,args.hidden,excprune=exc,incprune=inc)
        
        # [pattern , regexp , filetype]
        if args.pattern is not None:
            ls = [*filter(lambda x: x.is_match(args.pattern),ls)]
        if args.regexp is not None:
            ls = [*filter(lambda x: x.is_regexp(args.regexp),ls)]
        if args.filetype is not None:
            ls = [*filter(lambda x: x.isdir or x.is_ftype(args.filetype),ls)]
        
        # (sort)
        if args.sort is not None:
            klmb = (lambda x: x.modified) if args.sort.lower()=='m' else (lambda x: x.created) if args.sort.lower() == 'c' else (lambda x: x.size)
            rev = args.sort.islower()
            sort = lambda x: sorted(x,key=klmb,reverse=rev)
        else:
            sort = None

    # ---- Make Tree ---- #
    ftree = maketree(sorted(files),fmt=args.format,cli=sys.stdout.isatty())
    print('\n'.join(['.']+ftree),file=sys.stdout)


# ============================================ ls ============================================ #

def _ls(args):
    # path , (dirflag | fileflag) , hidden , recursive , maxdepth , limit , format, [exclude, include], [pattern , regexp , filetype] , sort
    path = path_arg(args.path)
    print(cli_color(path,36),file=sys.stderr)
    from .fpath import Path,splitpath
    root = Path('.',path)
    # (recursive & maxdepth)
    depth = 0 if not args.recursive else args.maxdepth
    #  (dirflag)
    if args.dirflag:
        ls = root.ls_dirs(depth,args.hidden)
    else:
        # [exclude, include]
        inc = None if args.include is None else [splitpath(p) for p in args.include]
        exc = None if args.exclude is None else [splitpath(p) for p in args.exclude]
        # (fileflag)
        if args.fileflag:
            ls = root.ls_files(depth,args.hidden,excprune=exc,incprune=inc)
            # (sort)
            if args.sort is not None:
                klmb = (lambda x: x.modified) if args.sort.lower()=='m' else (lambda x: x.created) if args.sort.lower() == 'c' else (lambda x: x.size)
                ls = sorted(ls,key=klmb,reverse = args.sort.islower())
        else:
            ls = root.ls(depth,args.hidden,excprune=exc,incprune=inc)
        
        # [pattern , regexp , filetype]
        if args.pattern is not None:
            ls = [*filter(lambda x: x.is_match(args.pattern),ls)]
        if args.regexp is not None:
            ls = [*filter(lambda x: x.is_regexp(args.regexp),ls)]
        if args.filetype is not None:
            ls = [*filter(lambda x: x.isdir or x.is_ftype(args.filetype),ls)]

    # (limit)
    limit = min(args.limit,len(ls)) if args.limit is not None else len(ls)
    # ---- Print Out ---- #
    isatty = sys.stdout.isatty()
    for x in ls[:limit]:
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
    # path , (dirflag | fileflag) , hidden , maxdepth , format , [exclude, include] , [pattern , regexp , filetype] , (-m | -M | -c | -C | -b | -B)
    parser_tree = subparsers.add_parser('tree', help='print file tree',description="File tree command")
    parser_tree.add_argument('path',nargs='?',default='.',help='tree root directory')
    parser_tree_flags = parser_tree.add_mutually_exclusive_group(required=False)
    parser_tree_flags.add_argument('-d',dest='dirflag',type='store_true',help='dirs only flag')
    parser_tree_flags.add_argument('-F',dest='fileflag',type='store_true',help='files only flag (ignore empty directories)')
    parser_tree.add_argument('-a',dest='hidden',action='store_true',help='include hidden files')
    parser_tree.add_argument('-n',dest='maxdepth',type=int,metavar='DEPTH',help='max tree depth')
    parser_tree.add_argument('-fmt',dest='format',type=str,default="%n",metavar='FORMAT',help='display format for tree nodes')
    parser_tree_prune = parser_tree.add_argument_group(title='pruning',description='control which dir branches to include in tree')
    parser_tree_prune.add_argument('-exc',dest='exclude',action='append',metavar='PATH',help='sub paths to exclude from tree')
    parser_tree_prune.add_argument('-inc',dest='include',action='append',metavar='PATH',help='sub paths to include in tree')
    parser_tree_filter = parser_tree.add_argument_group(title='filters',description='filter files included in tree')
    parser_tree_filter.add_argument('-wc',dest='pattern',metavar='PATTERN',help='wild card pattern')
    parser_tree_filter.add_argument('-grep',dest='regexp',metavar='REGEXP',help='regular expression to match')
    parser_tree_filter.add_argument('-ft',dest='filetype',action='append',metavar='FILETYPE',help='file type filter')
    parser_tree_sort = parser_tree.add_mutually_exclusive_group(required=False)
    parser_tree_sort.add_argument('-m',dest='sort',action='store_const',const='m',help='sort by modified time descending')
    parser_tree_sort.add_argument('-M',dest='sort',action='store_const',const='M',help='sort by modified time ascending')
    parser_tree_sort.add_argument('-c',dest='sort',action='store_const',const='c',help='sort by created time descending')
    parser_tree_sort.add_argument('-C',dest='sort',action='store_const',const='C',help='sort by created time ascending')
    parser_tree_sort.add_argument('-b',dest='sort',action='store_const',const='b',help='sort by size descending')
    parser_tree_sort.add_argument('-B',dest='sort',action='store_const',const='B',help='sort by size ascending')
    #parser_tree.add_argument('-sort',dest='sort',type=str,metavar='ARG',choices=['m','M','c','C','s','S'],help='sort files by created timestamp, modified timestamp, or size')
    parser_tree.set_defaults(run=_tree)

    # ------------------------------------------------ ls ------------------------------------------------ #
    # path , (dirflag | fileflag) , hidden , recursive, maxdepth , limit , format , [exclude, include] , [pattern , regexp , filetype] , (-m | -M | -c | -C | -b | -B)
    parser_ls = subparsers.add_parser('ls', help='list files in directory',description="List files command")
    parser_ls.add_argument('path',nargs='?',default='.',help='root directory')
    parser_ls.add_argument('-r',dest='recursive',action='store_true',help='list files recursively')
    parser_ls.add_argument('-n',dest='maxdepth',type=int,metavar='DEPTH',help='max depth if recursive flag is specified')
    parser_ls_flags = parser_ls.add_mutually_exclusive_group(required=False)
    parser_ls_flags.add_argument('-d',dest='dirflag',type='store_true',help='dirs only flag')
    parser_ls_flags.add_argument('-F',dest='fileflag',type='store_true',help='files only flag')
    parser_ls.add_argument('-a',dest='hidden',action='store_true',help='include hidden files')
    parser_ls.add_argument('-lim',dest='limit',type=int,metavar='COUNT',help='maximum items to list in output')
    parser_ls.add_argument('-fmt',dest='format',type=str,default="%f",metavar='FORMAT',help='display format for listed items')
    parser_ls_prune = parser_ls.add_argument_group(title='pruning',description='control which sub dirs to include when recursive flag is specified')
    parser_ls_prune.add_argument('-exc',dest='exclude',action='append',metavar='PATH',help='sub paths to exclude')
    parser_ls_prune.add_argument('-inc',dest='include',action='append',metavar='PATH',help='sub paths to include')
    parser_ls_filter = parser_ls.add_argument_group(title='filters',description='filter files to list')
    parser_ls_filter.add_argument('-wc',dest='pattern',metavar='PATTERN',help='wild card pattern')
    parser_ls_filter.add_argument('-grep',dest='regexp',metavar='REGEXP',help='regular expression to match')
    parser_ls_filter.add_argument('-ft',dest='filetype',action='append',metavar='FILETYPE',help='file type filter')
    parser_ls_sort = parser_ls.add_mutually_exclusive_group(required=False)
    parser_ls_sort.add_argument('-m',dest='sort',action='store_const',const='m',help='sort by modified time descending')
    parser_ls_sort.add_argument('-M',dest='sort',action='store_const',const='M',help='sort by modified time ascending')
    parser_ls_sort.add_argument('-c',dest='sort',action='store_const',const='c',help='sort by created time descending')
    parser_ls_sort.add_argument('-C',dest='sort',action='store_const',const='C',help='sort by created time ascending')
    parser_ls_sort.add_argument('-b',dest='sort',action='store_const',const='b',help='sort by size descending')
    parser_ls_sort.add_argument('-B',dest='sort',action='store_const',const='B',help='sort by size ascending')
    #parser_ls.add_argument('-sort',dest='sort',type=str,metavar='ARG',choices=['m','M','c','C','s','S'],help='sort files by created timestamp, modified timestamp, or size')
    parser_ls.set_defaults(run=_ls)

    # ------------------------------------------------ py ------------------------------------------------ #

    parser_py = subparsers.add_parser('py', help='python code parser',description="python code parser")
    parser_py.add_argument('path',nargs='?',default='.',help='either a directory to search for .py files in, or a .py file')
    #parser_py.add_argument('-a',dest='ask',action='store_true',help='ask to include files')
    #parser_py.add_argument('-r',dest='recursive',action='store_true',help='search root path recursively')
    parser_py.set_defaults(run=_py)


    # ------------------------------------------------ html ------------------------------------------------ #

    parser_html = subparsers.add_parser('html', help='html link parser',description="html link parser")
    parser_html.add_argument('path',nargs='?',default='.',help='either a directory to search for html files in, or a html file')
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
