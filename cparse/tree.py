import os,re,fnmatch,functools
from .util import iter_reduce
from .fpath import splitpath,fmodified,fcreated,ftype

__all__ = ['maketree','ls','fileiter','filter_match','filter_ftypes','filter_regexp']

# ============================================ Tree ============================================ #

def maketree(paths,lvl=0,fmt=lambda f: f.filename):
    i,n = 0,len(paths)
    while i < n and len(paths[i])-lvl == 1:
        i=i+1
    if i == n:
        return ["├── {}".format(fmt(f)) for f in paths[:-1]]+["└── {}".format(fmt(paths[-1]))]
    ftree = ["├── {}".format(fmt(f)) for f in paths[:i]]
    groups = [i]+[x for x in range(i+1,n) if paths[x].path[lvl]!=paths[x-1].path[lvl]]
    for i1,i2 in iter_reduce(groups):
        ftree += ["├── {}".format(paths[i1].path[lvl])]+["│   {}".format(f) for f in maketree(paths[i1:i2],lvl+1,fmt)]
    i = groups[-1]
    return ftree + ["└── {}".format(paths[i].path[lvl])]+["    {}".format(f) for f in maketree(paths[i:],lvl+1,fmt)]

# ============================================ File Iter ============================================ #

def fileiter(root):
    """generator that yields all files in [root]"""
    lsdir = os.listdir(root)
    isdir = [int(os.path.isdir(os.path.join(root,f))) for f in lsdir]
    for f in [y for x,y in zip(isdir,lsdir) if x==0]:
        yield f
    for d in [y for x,y in zip(isdir,lsdir) if x==1]:
        for f in fileiter(os.path.join(root,d)):
            yield os.path.join(d,f)

# ============================================ ls ============================================ #

def ls(root,recursive):
    """generator that yields all files and dir in first level of [root]"""
    content = os.listdir(root)
    isdir = [int(os.path.isdir(os.path.join(root,f))) for f in content]
    files = sorted([y for x,y in zip(isdir,content) if x==0])
    dirs = sorted([y for x,y in zip(isdir,content) if x==1])
    if recursive:
        dirs = [a for b in [[os.path.join(d,f) for f in ls(os.path.join(root,d),recursive)] for d in dirs] for a in b]
    return files+dirs

# ============================================ File Filtering ============================================ #

def _file_filter(fn):
    def wrapper(files,*args,**kwargs):
        for f in files:
            if fn(f,*args,**kwargs):
                yield f
    return functools.update_wrapper(wrapper,fn)

@_file_filter
def filter_match(file,pattern):
    """filters out files based on [pattern]"""
    return fnmatch.fnmatch(file,pattern)

@_file_filter
def filter_ftypes(file,ftypes):
    """filters out files not included in [ftypes]"""
    return ftype(file) in ftypes

@_file_filter
def filter_regexp(file,regexp):
    """filters out files not included in [filetypes]"""
    return bool(re.match(regexp,file))
