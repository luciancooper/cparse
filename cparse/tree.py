import os,re,fnmatch,functools
from .util import iter_reduce,mergesort
from .fpath import cmp_pathsegs

__all__ = ['maketree','ls','ls_files','ls_dirs']

# ============================================ Tree ============================================ #

def calc_structure(d,l=0):
    #print('{1:}\n{0:}'.format('-'*53,'\n'.join('(%s)'%','.join([(' %s ' if i!=l else '[%s]')%s for i,s in enumerate(x)]) for x in d)))
    n = len(d)
    g = [0]+[i for i in range(1,n) if d[i][l]!=d[i-1][l]]
    for i,j in iter_reduce(g):
        yield (3,),d[i][:l+1]
        if len(d[i])-l == 1:
            i = i+1
            if i==j:continue
        for xi,xd in calc_structure(d[i:j],l+1):
            yield (2,)+xi,xd
        #print('-'*50)
    i = g[-1]
    yield (1,),d[i][:l+1]
    if len(d[i])-l == 1:
        i = i+1
        if i==n:return
    for xi,xd in calc_structure(d[i:],l+1):
        yield (0,)+xi,xd

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
    if len(d[0]) == 0:
        d = d[1:]
    tinx,d = (list(x) for x in zip(*calc_structure(d)))
    #treelog(tinx,d)
    tinx,d,m = [(3,)]+tinx,[()]+d,[0]*(1+len(d))
    p = [*filter(lambda x: x.isfile,paths)]
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
    for x in range(i):
        tree.append("├── {}".format(p[x].fmt(fmt,cli)))
    for j in range(1,len(d)-1):
        tree.append("{} {}".format(''.join(box[x] for x in tinx[j]),d[j][-1]))
        if m[j] == 0:
            continue
        prefix = ''.join(box[x] for x in tinx[j][:-1])+box[tinx[j][-1]-1]
        for x in range(i,i+m[j]-1):
            tree.append('{}├── {}'.format(prefix,p[x].fmt(fmt,cli)))
        i = i+m[j]
        tree.append('{}{} {}'.format(prefix,box[3 if len(d[j+1])==len(d[j])+1 else 1],p[i-1].fmt(fmt,cli)))
    tree.append("{} {}".format(''.join(box[x] for x in tinx[-1]),d[-1][-1]))
    if m[-1] > 0:
        prefix = ''.join(box[x] for x in tinx[-1][:-1])+box[tinx[-1][-1]-1]
        pfiles = p[i:]
        for f in pfiles[:-1]:
            tree.append('{}├── {}'.format(prefix,f.fmt(fmt,cli)))
        tree.append('{}└── {}'.format(prefix,pfiles[-1].fmt(fmt,cli)))
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
