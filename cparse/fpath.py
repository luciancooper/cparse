# File Path Utilities

import os,re,fnmatch
import pydecorator
from .util import mergesort,timestamp,ftype_cli,cli_color

__all__ = ['ftype','splitpath','joinpath','natural_cmp','cmp_pathsegs','Path']


def ftype(path):
    """returns file extension of [path]"""
    try:
        file = os.path.basename(path)
        i = file.rindex('.')
        return file[i+1:]
    except ValueError:
        return ''


def splitpath(path):
    """Splits a path into all its components"""
    p0,p1,p = (*os.path.split(path),tuple())
    while p1!='':
        p0,p1,p = (*os.path.split(p0),(p1,) + p)
    return p if p0 is '' else (p1,)+p

def joinpath(*args):
    if len(args)>1:
        return os.sep.join(args)
    if len(args)==1:
        return os.sep if args[0]=='' else args[0]
    raise "joinpath requires 1 or more arguments"

def natural_cmp(a,b):
    i,j,n,m = 0,0,len(a),len(b)
    while i<n and j<m:
        if not a[i].isnumeric() or not b[j].isnumeric():
            if a[i] == b[j]:
                i,j = i+1,j+1
                continue
            return -1 if a[i] < b[j] else 1
        i2,j2 = i+1,j+1
        while i2 < n and a[i2].isnumeric():
            i2+=1
        while j2 < m and b[j2].isnumeric():
            j2+=1
        na,nb = a[i:i2],b[j:j2]
        if na == nb:
            i,j = i2,j2
            continue
        if na[0]=='0' or nb[0]=='0':
            return -1 if na < nb else 1
        if int(na) == int(nb):
            raise "Logical Error na:[%s] nb:[%s]"%(na,nb)
        return -1 if int(na) < int(nb) else 1
    if i < n:
        return -1 if a[i] in " _-–,;!?¡" else 1
    if j < m:
        return 1 if b[j] in " _-–,;!?¡" else -1
    assert a == b, "'%s' not equal to '%s'"%(a,b)
    return 0


def cmp_pathsegs(a,b):
    """
    args: a & b must be in split tuple form
    returns:
        -1: a < b
         1: a > b
         0: a == b
    """
    for i,j in zip(a,b):
        if i == j:
            continue
        return natural_cmp(i,j)
    n,m = len(a),len(b)
    return 0 if n==m else -1 if n < m else 1



# ============================================ File ============================================ #


class PathMeta(type):
    def __call__(cls,*args,**kwargs):
        obj,args,kwargs = cls.__new__(cls,*args,**kwargs)
        obj.__init__(*args,**kwargs)
        return obj
    

def _settle_args(path,abspath=None):
    path = os.path.normpath(path)
    if abspath != None:
        return path,os.path.normpath(abspath)
    if os.path.isabs(path):
        return path,path
    else:
        return path,os.path.normpath(os.path.join(os.getcwd(),path))

class Path(metaclass=PathMeta):
    def __new__(cls,*args):
        """
        Use of this constructor assumes one of the following scenarios:
        * (entry,path,abspath)
        * (entry,abspath)
        * (entry,path)
        * (entry)
        """
        if (type(args[0])==os.DirEntry):
            entry,args = args[0],args[1:]
            if len(args) == 0:
                path,abspath = _settle_args(entry.path)
            elif len(args) == 1:
                path,abspath = (entry.path,args[0]) if os.path.isabs(args[0]) else _settle_args(args[0])
            else:
                path,abspath = _settle_args(*args)
            stats = entry.stat()
            return object.__new__(Dir if entry.is_dir() else File),(path,abspath),{'created':stats.st_birthtime,'modified':stats.st_mtime,'size':stats.st_size,'ino':stats.st_ino}
        path,abspath = _settle_args(*args)
        if not os.path.exists(abspath):
            return object.__new__(cls),(path,abspath),{}
        # Get Created/Modified times
        stats = os.stat(abspath)
        return object.__new__(Dir if os.path.isdir(abspath) else File),(path,abspath),{'created':stats.st_birthtime,'modified':stats.st_mtime,'size':stats.st_size,'ino':stats.st_ino}
        

    def __init__(self,path,abspath,**kwargs):
        #print(f"Path.__init__({path},{abspath},{kwargs})")
        # Split Path
        self._path = splitpath(path)
        self._abspath = splitpath(abspath)
        # Assign Properties
        for k,v in kwargs.items():
            setattr(self,k,v)

    
    def __str__(self): return joinpath(*self._path)

    def __len__(self): return len(self._path)

    # --------- Path --------- #

    @property
    def name(self): return self._path[-1]

    @property
    def isfile(self):
        return '.' in self.name

    @property
    def isdir(self):
        return '.' not in self.name

    @property
    def _dir(self):
        return self._path[:-1] if self.isfile else self._path

    @property
    def path(self): return joinpath(*self._path)

    @property
    def dirpath(self):return joinpath(*self._dir)

    @property
    def abspath(self): return joinpath(*self._abspath)

    @property
    def rootpath(self):
        if len(self._path) == len(self._abspath):
            return "/"
        return joinpath(*self._abspath[:-len(self._path)],'')

    # --------- file properties --------- #

    @property
    def filetype(self):
        """returns file extension"""
        if self.isdir:
            return None
        try:
            file = self._path[-1]
            i = file.rindex('.')
            return file[i+1:]
        except ValueError:
            return ''

    @property
    def filename(self):
        """returns file name without extension"""
        if self.isdir:
            return None
        try:
            file = self._path[-1]
            i = file.rindex('.')
            return file[:i]
        except ValueError:
            return self._path[-1]
    
    # --------- path properties --------- #

    @property
    def hidden(self): return any(x.startswith('.') for x in self._path)


    # --------- Format --------- #

    def _format_code(self,code,cli):
        # Date Modified
        if code == 'n':
            if not cli or not self.isfile: return self.name
            ft = self.filetype
            return cli_color(self.name,ftype_cli[ft]) if ft in ftype_cli else self.name
        if code == 'f': return self.path
        if code == 'F': return self.abspath
        if code == 'd': return self.dirpath
        # inode number
        if code == 'i':
            return '-' if not hasattr(self,'ino') else cli_color(self.ino,'38;5;165') if cli else str(self.ino)
        # Date Modified
        if code == 'm':
            return '-' if not hasattr(self,'modified') else cli_color(timestamp(self.modified),33) if cli else timestamp(self.modified)
        # Date created
        if code == 'c':
            return '-' if not hasattr(self,'created') else cli_color(timestamp(self.created),32) if cli else timestamp(self.created)
        # File Size
        if code == 'b':
            return '-' if not hasattr(self,'size') else cli_color(str(self.size),34) if cli else str(self.size)
        raise IndexError("Unrecognized Format Variable '{}'".format(code))

    @pydecorator.str
    def fmt(self,pattern,cli=False):
        """Returns a formatted version of path"""
        i = 0
        try:
            j = pattern.index("%",i)
            while True:
                if j > i:
                    yield pattern[i:j]
                yield self._format_code(pattern[j+1],cli)
                i = j+2
                j = pattern.index("%",i)
        except ValueError:
            j = len(pattern)
        finally:
            if j > i:
                yield pattern[i:j]

    # --------- Checks --------- #

    def inpath(self,path):
        if (len(self._path)-(1 if self.isfile else 0)) < len(path):
            return False
        for p1,p2 in zip(self._path,path):
            if p1 != p2:
                return False
        return True

    def is_match(self,pattern):
        """does match unix style [pattern]"""
        return fnmatch.fnmatch(self.path,pattern)

    def is_regexp(self,regexp):
        """Check if path matches [regexp]"""
        return bool(re.match(regexp,self.path))

    #  --------- Comparisons --------- #

    def cmp(self,other):
        """
        -1: self < other
         1: self > other
         0: self == other
        """
        if not isinstance(other,Path): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        n = cmp_pathsegs(self._dir,other._dir)
        if n != 0: return n
        if self.isdir:
            return 0 if other.isdir else -1
        if other.isdir:
            return 1
        return natural_cmp(self.name,other.name)

    def __eq__(self,other): return self.cmp(other) == 0

    def __ne__(self,other): return self.cmp(other) != 0
    
    def __lt__(self, other): return self.cmp(other) == -1

    def __le__(self, other): return self.cmp(other) <= 0

    def __gt__(self, other): return self.cmp(other) == 1

    def __ge__(self, other): return self.cmp(other) >= 0

    #  --------- Comparisons --------- #

    def cmp_ftype(self,other):
        if not isinstance(other,Path): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        if self.isdir:
            return cmp_pathsegs(self._dir,other._dir) if other.isdir else -1
        if other.isdir: 
            return 1
        ft1,ft2 = self.filetype,other.filetype
        if ft1 != ft2:
            return -1 if ft1 < ft2 else 1
        n = cmp_pathsegs(self._dir,other._dir)
        return n if n != 0 else natural_cmp(self.name,other.name)

    def cmp_mtime(self,other):
        if not isinstance(other,Path): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.cmp(other) if self.modified == other.modified else 1 if self.modified < other.modified else -1

    def cmp_ctime(self,other):
        if not isinstance(other,Path): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.cmp(other) if self.created == other.created else 1 if self.created < other.created else -1

    def cmp_size(self,other):
        if not isinstance(other,Path): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.cmp(other) if self.size == other.size else 1 if self.size < other.size else -1

    def cmp_ino(self,other):
        if not isinstance(other,Path): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.cmp(other) if self.ino == other.ino else -1 if self.ino < other.ino else 1

class Dir(Path):

    def __new__(cls,*args):
        """
        Use of this direct constructor assumes one of 2 possible scenarios:
        1. (path [str],abspath [str]), where [path] & [abspath] point to a directory that exists
        2. (path [os.DirEntry],abspath [str])
        """
        if (type(args[0])==os.DirEntry):
            entry,args = args[0],args[1:]
            if len(args) == 0:
                path,abspath = _settle_args(entry.path)
            elif len(args) == 1:
                path,abspath = (entry.path,args[0]) if os.path.isabs(args[0]) else _settle_args(args[0])
            else:
                path,abspath = _settle_args(*args)
            stats = entry.stat()
        else:
            path,abspath = _settle_args(*args)
            stats = os.stat(abspath)
        return object.__new__(cls),(path,abspath),{'created':stats.st_birthtime,'modified':stats.st_mtime,'size':stats.st_size,'ino':stats.st_ino}

    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    # --------- properties --------- #

    @property
    def isfile(self): return False

    @property
    def isdir(self): return True

    @property
    def _dir(self):
        return self._path
    
    # --------- ls --------- #

    @staticmethod
    def _prune_dirs(dirs,excprune,incprune):
        # ---- EFFICIENT PRUNING ---- #
        if excprune is not None:
            # get newest round of nodes & use them to filter out dirs that are to be completely excluded
            e_n = [e[0] for e in excprune if len(e) == 1]
            dirs = [d for d in dirs if d.name not in e_n]
            # keep subtree arguments
            e_t = [e for e in excprune if len(e) > 1]
            e_p = [x if len(x)>0 else None for x in [[e[1:] for e in e_t if d.name==e[0]] for d in dirs]]
        else:
            e_p = [None]*len(dirs)
        if incprune is None:
            for d,e in zip(dirs,e_p):
                yield (d,e,None)
            return
        for d,e in zip(dirs,e_p):
            i_p = [i for i in incprune if i[0] == d.name]
            if len(i_p)==0:
                continue
            i_p = [i[1:] for i in i_p if len(i)>1]
            yield (d,e,i_p if len(i_p)>0 else None)

    def ls(self,depth=None,hidden=False,excprune=None,incprune=None):
        """
        finds all files and dirs in path
        args:
            * depth
            * hidden
            * excprune: exclude prune
            * incprune: include prune
        """
        path,abspath = self.path,self.abspath
        with os.scandir(abspath) as scan:
            p = [Path(x,os.path.join(path,x.name),os.path.join(abspath,x.name)) for x in scan]
        if not hidden: p = [x for x in p if not x.hidden]
        f = sorted([x for x in p if isinstance(x,File)],key=lambda x:x.name)
        dirs = sorted([x for x in p if isinstance(x,Dir)],key=lambda x:x.name)
        if depth is not None:
            if depth == 0:
                return f + (dirs if (excprune is None and incprune is None) else [d for d,e,i in self._prune_dirs(dirs,excprune,incprune)])
            depth = depth-1
        if excprune is None and incprune is None:
            return f+[a for b in [[d]+d.ls(depth,hidden) for d in dirs] for a in b]
        # PRUNING
        for d,e,i in self._prune_dirs(dirs,excprune,incprune):
            f.extend([d]+d.ls(depth,hidden,excprune=e,incprune=i))
        return f

    def ls_files(self,depth=None,hidden=False,excprune=None,incprune=None):
        """
        finds all files in path
        args:
            * depth
            * hidden
            * excprune: exclude prune
            * incprune: include prune
        """
        path,abspath = self.path,self.abspath
        with os.scandir(abspath) as scan:
            if depth == 0:
                f = [File(x,os.path.join(path,x.name),os.path.join(abspath,x.name)) for x in scan if x.is_file()]
                if not hidden: f = [x for x in f if not x.hidden]
                return sorted(f)
            p = [Path(x,os.path.join(path,x.name),os.path.join(abspath,x.name)) for x in scan]
        if not hidden: p = [x for x in p if not x.hidden]
        f = sorted([x for x in p if x.isfile])
        if depth is not None:
            depth = depth-1
        dirs = sorted([x for x in p if x.isdir])

        if excprune is None and incprune is None:
            return f+[a for b in [x.ls_files(depth,hidden) for x in dirs] for a in b]
        # PRUNING
        for d,e,i in self._prune_dirs(dirs,excprune,incprune):
            f.extend(d.ls_files(depth,hidden,excprune=e,incprune=i))
        return f

    def ls_dirs(self,depth=None,hidden=False):
        """
        finds all dirs in path
        """
        path,abspath = self.path,self.abspath
        with os.scandir(abspath) as scan:
            p = [Dir(x,os.path.join(path,x.name),os.path.join(abspath,x.name)) for x in scan if x.is_dir()]
        p = mergesort(p,lambda x,y: natural_cmp(x.name,y.name))
        if not hidden: p = [x for x in p if not x.hidden]
        if depth is not None:
            if depth == 0: return p
            depth = depth-1
        return [a for b in [[x]+x.ls_dirs(depth,hidden) for x in p] for a in b]

    

    
    

class File(Path):

    def __new__(cls,*args):
        """
        Use of this direct constructor assumes one of 2 possible scenarios:
        1. (path,abspath), where [path] is a string, which points to a file that exists
        2. (path,abspath), where [entry] is an instance of os.DirEntry
        """
        if (type(args[0])==os.DirEntry):
            entry,args = args[0],args[1:]
            if len(args) == 0:
                path,abspath = _settle_args(entry.path)
            elif len(args) == 1:
                path,abspath = (entry.path,args[0]) if os.path.isabs(args[0]) else _settle_args(args[0])
            else:
                path,abspath = _settle_args(*args)
            stats = entry.stat()
        else:
            path,abspath = _settle_args(*args)
            stats = os.stat(abspath)
        return object.__new__(cls),(path,abspath),{'created':stats.st_birthtime,'modified':stats.st_mtime,'size':stats.st_size,'ino':stats.st_ino}
        
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    
    # --------- path --------- #

    @property
    def isfile(self): return True

    @property
    def isdir(self): return False
    
    @property
    def _dir(self):
        return self._path[:-1]
    
    # --------- Checks --------- #

    def is_ftype(self,ftypes):
        """Check if filetype is one of supplied [ftypes]"""
        return self.filetype in ftypes

    # --------- I/O --------- #

    def read(self):
        with open(self.abspath,'r') as f:
            return f.read()

    def readlines(self):
        with open(self.abspath,'r') as f:
            for f in f.readlines():
                yield f
