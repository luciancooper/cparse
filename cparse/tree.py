import os,re,fnmatch,functools
from .util import iter_reduce
from .fpath import splitpath,fmodified,fcreated,ftype

__all__ = ['maketree','ls','ls_files','ls_dirs']

# ============================================ Tree ============================================ #

def maketree(paths,lvl=0,fmt="%n",cli=False):
    """Recursively constructs tree from list of [File] objects"""
    i,n = 0,len(paths)
    while i < n and len(paths[i])-lvl == 1:
        i=i+1
    if i == n:
        nodes = [x.fmt(fmt,cli) for x in paths]
        return ["├── {}".format(x) for x in nodes[:-1]]+["└── {}".format(nodes[-1])]
    ftree = ["├── {}".format(x.fmt(fmt,cli)) for x in paths[:i]]
    groups = [i]+[x for x in range(i+1,n) if paths[x].path[lvl]!=paths[x-1].path[lvl]]
    for i1,i2 in iter_reduce(groups):
        ftree += ["├── {}".format(paths[i1].path[lvl])]+["│   {}".format(f) for f in maketree(paths[i1:i2],lvl+1,fmt,cli)]
    i = groups[-1]
    return ftree + ["└── {}".format(paths[i].path[lvl])]+["    {}".format(f) for f in maketree(paths[i:],lvl+1,fmt,cli)]


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
