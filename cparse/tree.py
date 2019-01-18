import pydecorator
import os

__all__ = ['maketree','fcreated','fmodified','ftype','filetree']

# ============================================ Tree ============================================ #

@pydecorator.mergesort_groups
def group_paths(a,b):
    return 1 if a[0] > b[0] else -1 if a[0] < b[0] else 0

@pydecorator.mergesort_map(duplicate_values=True)
def sortmap(a,b):
    return 1 if a > b else -1 if a < b else 0

def dirtree(root,paths):
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
        ftree += ["├── {}".format(name)]+["│   {}".format(f) for f in dirtree(os.path.join(root,name),[dirs[i][1:] for i in dirmap[x]])]
    name = dirnames[nmap[-1]]
    ftree += ["└── {}".format(name)]+["    {}".format(f) for f in dirtree(os.path.join(root,name),[dirs[i][1:] for i in dirmap[nmap[-1]]])]
    return ftree

def maketree(root,paths):
    """Paths are in the form [path,...]"""
    files = [tuple(f[len(root)+1:].split('/')) for f in paths]
    return [os.path.basename(root)]+dirtree(root,files)

# ============================================ Files ============================================ #

def fcreated(path):
    return os.stat(path).st_birthtime

def fmodified(path):
    return os.stat(path).st_mtime

def ftype(path):
    try:
        file = os.path.basename(path)
        i = file.rindex('.')
        return file[i+1:]
    except ValueError:
        return ''


def filetree(root,filetypes=None):
    ls = [os.path.join(root,f) for f in os.listdir(root)]
    isdir = [int(os.path.isdir(f)) for f in ls]
    dirs = [f for d,f in zip(isdir,ls) if d==1]
    files = [f for d,f in zip(isdir,ls) if d==0]
    if filetypes!=None:
        files = [f for f in files if ftype(f) in filetypes]
    return files + [a for b in [filetree(r,filetypes) for r in dirs] for a in b]
