import os,re,fnmatch,functools
from .util import iter_reduce,mergesort,ftype_cli,cli_color,str_table
from .fpath import cmp_pathsegs

__all__ = ['maketree','ls','ls_files','ls_dirs','filetype_stat']

# ============================================ Tree ============================================ #

def calc_structure(d):
    def recurse(l,i0,i1):
        g = [i0]+[i for i in range(i0+1,i1) if d[i][l]!=d[i-1][l]]
        for i,j in iter_reduce(g):
            yield (3,),d[i][:l+1]
            if len(d[i])-l == 1:
                i = i+1
                if i==j:continue
            for r,rd in recurse(l+1,i,j):
                yield (2,)+r,rd
        i = g[-1]
        yield (1,),d[i][:l+1]
        if len(d[i])-l == 1:
            i = i+1
            if i==i1:return
        for r,rd in recurse(l+1,i,i1):
            yield (0,)+r,rd
    return [*recurse(0,0,len(d))]

def _treechunk(files,prefix,prefix_end,sort,*fmtargs):
    if sort is not None:
        files = sort(files)
    for f in files[:-1]:
        yield '{} {}'.format(prefix,f.fmt(*fmtargs))
    yield '{} {}'.format(prefix_end,files[-1].fmt(*fmtargs))

def maketree(paths,fmt="%n",cli=False,sort=None):
    """
    Recursively constructs tree from list of [Path] objects
    args:
        * fmt
        * cli
        * sort
    """
    box = ['   ','└──','│  ','├──']
    d = mergesort([x._dir for x in paths],cmp_pathsegs,unique=True)
    p = [*filter(lambda x: x.isfile,paths)]
    if len(d[0]) == 0:
        d = d[1:]

    # Setup sort
    if sort is not None:
        if sort.lower()=='m':
            fcmp = lambda x,y: x.cmp_mtime(y)
        elif sort.lower()=='c':
            fcmp = lambda x,y: x.cmp_ctime(y)
        elif sort.lower()=='b':
            fcmp = lambda x,y: x.cmp_size(y)
        elif sort.lower()=='i':
            fcmp = lambda x,y: x.cmp_ino(y)
        else:
            fcmp = lambda x,y: x.cmp_ftype(y)
        if sort.isupper():
            sort = lambda x: [*reversed(mergesort(x,fcmp))]
        else:
            sort = lambda x: mergesort(x,fcmp)
    if len(d) == 0:
        # only files
        return [*_treechunk(p,box[3],box[1],sort,fmt,cli)]
    tinx,d = (list(x) for x in zip(*calc_structure(d)))
    tinx,d,m = [(3,)]+tinx,[()]+d,[0]*(1+len(d))
    i,j,pn = 0,0,len(p)
    # ----- Create map between d and p ----- #
    # essentially do ...  while (i < pn)
    if pn > 0:
        while True:
            while d[j] != p[i]._dir:
                j=j+1
            while i < pn and d[j]==p[i]._dir:
                i,m[j] = i+1,m[j]+1
            if i == pn:
                break
    # ----- Build Tree----- #
    tree,i = [],m[0]
    if i > 0:
        tree.extend(_treechunk(p[:i],box[3],box[3],sort,fmt,cli))
    for j in range(1,len(d)-1):
        tree.append("{} {}".format(''.join(box[x] for x in tinx[j]),d[j][-1]))
        if m[j] == 0:
            continue
        prefix = ''.join(box[x] for x in tinx[j][:-1])+box[tinx[j][-1]-1]
        tree.extend(_treechunk(p[i:i+m[j]],prefix+box[3],prefix+box[3 if len(d[j+1])==len(d[j])+1 else 1],sort,fmt,cli))
        i = i+m[j]
    tree.append("{} {}".format(''.join(box[x] for x in tinx[-1]),d[-1][-1]))
    if m[-1] > 0:
        prefix = ''.join(box[x] for x in tinx[-1][:-1])+box[tinx[-1][-1]-1]
        tree.extend(_treechunk(p[i:],prefix+box[3],prefix+box[1],sort,fmt,cli))
    return tree


# ============================================ ls ============================================ #

def ls(root,recursive=True,depth=None):
    """finds all files and dirs in [root]"""
    lsdir = os.listdir(root)
    isdir = [int(os.path.isdir(os.path.join(root,f))) for f in lsdir]
    files = sorted([y for x,y in zip(isdir,lsdir) if x==0])
    dirs = sorted([y for x,y in zip(isdir,lsdir) if x==1])
    if not recursive:
        return files+dirs
    if depth is not None:
        if depth == 0: return files+dirs
        depth = depth-1
    return files + [a for b in [[d]+[os.path.join(d,x) for x in ls(os.path.join(root,d),recursive,depth)] for d in dirs] for a in b]

def ls_files(root,recursive=True,depth=None):
    """finds all files in [root]"""
    lsdir = os.listdir(root)
    isdir = [int(os.path.isdir(os.path.join(root,f))) for f in lsdir]
    files = sorted([y for x,y in zip(isdir,lsdir) if x==0])
    if not recursive:
        return files
    if depth is not None:
        if depth == 0: return files
        depth = depth-1
    dirs = sorted([y for x,y in zip(isdir,lsdir) if x==1])
    return files + [a for b in [[os.path.join(d,x) for x in ls_files(os.path.join(root,d),recursive,depth)] for d in dirs] for a in b]

def ls_dirs(root,recursive=True,depth=None):
    """finds all dirs in [root]"""
    lsdir = os.listdir(root)
    dirs = sorted([x for x in lsdir if os.path.isdir(os.path.join(root,x))])
    if not recursive: return dirs
    if depth is not None:
        if depth == 0: return dirs
        depth = depth-1
    return [a for b in [[d]+[os.path.join(d,x) for x in ls_dirs(os.path.join(root,d),recursive,depth)] for d in dirs] for a in b]

# ============================================ File-Type Stat ============================================ #

def filetype_stat(paths,cli=False):
    #paths = mergesort([*filter(lambda x:x.isfile,paths)],lambda x,y: x.cmp_ftype(y))
    paths = [*filter(lambda x:x.isfile,paths)]
    ftypes = [x.filetype for x in paths]
    ftmap = {x:0 for x in sorted(set(ftypes))}
    for ft in ftypes:
        ftmap[ft] += 1
    ft,n = (list(x) for x in zip(*(x for x in ftmap.items())))
    tot = sum(n)
    pct = ["{:.1f}%".format(x/tot*100) for x in n]
    header = ['ftype','count','pct']
    if not cli:
        return str_table([ft,n,pct],header)
    cols = [ft,[str(x) for x in n],pct]
    w = [max(len(x) for x in [h]+c) for h,c in zip(header,cols)]
    ftcol = [(cli_color(x.ljust(w[0],' '),ftype_cli[x]) if x in ftype_cli else x.ljust(w[0],' ')) for x in ft]
    cols = [ftcol]+[[x.rjust(w,' ') for x in c] for w,c in zip(w[1:],cols[1:])]
    l = '38;5;245'
    divider = cli_color('+-%s-+'%'-+-'.join(x*'-' for x in w),l)
    header = cli_color('| ',l)+cli_color(' | ',l).join(cli_color(h.ljust(x,' '),'38;5;230') for h,x in zip(header,w))+cli_color(' |',l)
    rows = [cli_color('| ',l)+cli_color(' | ',l).join(x)+cli_color(' |',l) for x in zip(*cols)]
    #lines = [divider]+[header]+[divider]+[a for b in [[r]+[divider] for r in rows] for a in b]
    lines = [divider]+[header]+[divider]+rows+[divider]
    return '\n'.join(lines)
