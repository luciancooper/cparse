import pydecorator
import functools
import os
import inspect
import fnmatch
import re
from .util import timestamp

__all__ = ['maketree','fcreated','fmodified','ftype','ls','split','fileiter','filter_match','filter_ftypes','filter_regexp']

# ============================================ Tree ============================================ #

@pydecorator.mergesort_groups
def group_paths(a,b):
    return 1 if a[0] > b[0] else -1 if a[0] < b[0] else 0

@pydecorator.mergesort_map(duplicate_values=True)
def sortmap(a,b):
    return 1 if a > b else -1 if a < b else 0

def dirtree(paths):
    files = sorted([p[0] for p in paths if len(p)==1])
    dirs = [p for p in paths if len(p) > 1]
    if len(dirs) == 0:
        ftree = ["├── {}".format(f) for f in files[:-1]]+["└── {}".format(files[-1])]
        return ftree
    ftree = ["├── {}".format(f) for f in files]
    dirmap = group_paths(range(len(dirs)),dirs)
    dirnames = [dirs[min(x)][0] for x in dirmap]
    nmap = sortmap(dirnames)
    for x in nmap[:-1]:
        name = dirnames[x]
        ftree += ["├── {}".format(name)]+["│   {}".format(f) for f in dirtree([dirs[i][1:] for i in dirmap[x]])]
    name = dirnames[nmap[-1]]
    ftree += ["└── {}".format(name)]+["    {}".format(f) for f in dirtree([dirs[i][1:] for i in dirmap[nmap[-1]]])]
    return ftree

def dirtree_times(paths,times):
    ft = [(p[0],t) for p,t in zip(paths,times) if len(p)==1]
    dt = [(p,t) for p,t in zip(paths,times) if len(p)>1]
    if len(dt) == 0:
        files,ftimes = zip(*ft)
        fmap = sortmap(files)
        files = ["[{}] {}".format(timestamp(t),f) for f,t in zip([files[x] for x in fmap],[ftimes[x] for x in fmap])]
        ftree = ["├── {}".format(f) for f in files[:-1]]+["└── {}".format(files[-1])]
        return ftree
    if len(ft)>0:
        files,ftimes = zip(*ft)
        fmap = sortmap(files)
        ftree = ["├── [{}] {}".format(timestamp(t),f) for f,t in zip([files[x] for x in fmap],[ftimes[x] for x in fmap])]
    else:
        ftree = []
    dirs,dtimes = zip(*dt)
    dirmap = group_paths(range(len(dirs)),dirs)
    dirnames = [dirs[min(x)][0] for x in dirmap]
    nmap = sortmap(dirnames)
    for x in nmap[:-1]:
        name = dirnames[x]
        ftree += ["├── {}".format(name)]+["│   {}".format(f) for f in dirtree_times([dirs[i][1:] for i in dirmap[x]],[dtimes[i] for i in dirmap[x]])]
    name = dirnames[nmap[-1]]
    ftree += ["└── {}".format(name)]+["    {}".format(f) for f in dirtree_times([dirs[i][1:] for i in dirmap[nmap[-1]]],[dtimes[i] for i in dirmap[nmap[-1]]])]
    return ftree

def maketree(paths,times=None):
    """Paths are a list of relative paths"""
    paths = [split(path) for path in paths]
    if len(paths)==0:
        return ["."]
    return ["."]+(dirtree(paths) if times == None else dirtree_times(paths,times))


# ============================================ File Utils ============================================ #

def fcreated(path):
    """returns created timestamp of [path]"""
    return os.stat(path).st_birthtime

def fmodified(path):
    """returns last modified timestamp of [path]"""
    return os.stat(path).st_mtime

def ftype(path):
    """returns file extension of [path]"""
    try:
        file = os.path.basename(path)
        i = file.rindex('.')
        return file[i+1:]
    except ValueError:
        return ''

def split(path):
    """Splits a path into all its components"""
    p0,p1,p = (*os.path.split(path),tuple())
    while p1!='':
        p0,p1,p = (*os.path.split(p0),(p1,) + p)
    return p

# ============================================ File Iter ============================================ #

def fileiter(root):
    """generator that yields all files in [root]"""
    ls = os.listdir(root)
    isdir = [int(os.path.isdir(os.path.join(root,f))) for f in ls]
    for f in [y for x,y in zip(isdir,ls) if x==0]:
        yield f
    for d in [y for x,y in zip(isdir,ls) if x==1]:
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


