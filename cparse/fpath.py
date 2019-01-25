# File Path Utilities

import os,re,fnmatch
import pydecorator
from .util import timestamp,cli_color

__all__ = ['fcreated','fmodified','ftype','splitpath','cmp_paths','sort_paths','File']


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


def splitpath(path):
    """Splits a path into all its components"""
    p0,p1,p = (*os.path.split(path),tuple())
    while p1!='':
        p0,p1,p = (*os.path.split(p0),(p1,) + p)
    return p


def cmp_paths(p1,p2):
    """p1 & p2 must be in split tuple form, -> returns [-1 if p1 < p2] [1 if p1 > p2] [0 if p1 == p2]"""
    for d1,d2 in zip(p1[:-1],p2[:-1]):
        if d1 == d2:
            continue
        return -1 if d1 < d2 else 1
    n1,n2 = len(p1),len(p2)
    if n1 != n2:
        return -1 if n1 < n2 else 1
    f1,f2 = p1[-1],p2[-1]
    return 1 if f1 > f2 else -1 if f1 < f2 else 0


sort_paths = pydecorator.mergesort(duplicate_values=True)(cmp_paths)

# ============================================ File ============================================ #

class File():
    def __init__(self,path,abspath=None):
        # Normalize Path
        path = os.path.normcase(path)
        # Split Path
        self.path = splitpath(path)
        # Determine Absolute Path
        if abspath != None:
            self.abspath = os.path.normcase(abspath)
        elif os.path.isabs(path):
            self.abspath = path
        else:
            self.abspath = os.path.normpath(os.path.join(os.getcwd(),path))

    # Properties
    def __str__(self): return os.path.join(*self.path)

    def __len__(self): return len(self.path)

    @property
    def filename(self): return self.path[-1]

    @property
    def filepath(self): return os.path.join(*self.path)

    @property
    def created(self): return fcreated(self.abspath)

    @property
    def modified(self): return fmodified(self.abspath)

    @property
    def filetype(self):
        """returns file extension"""
        try:
            file = self.path[-1]
            i = file.rindex('.')
            return file[i+1:]
        except ValueError:
            return ''

    def _format_code(self,code,cli):
        # Date Modified
        if code == 'm':
            return cli_color(timestamp(self.modified),33) if cli else timestamp(self.modified)
        if code == 'c':
            return cli_color(timestamp(self.created),32) if cli else timestamp(self.created)
        if code == 'f':
            return self.filename
        if code == 'F':
            return self.filepath
        raise IndexError("Unrecognized Format Variable '{}'".format(code))

    # Pattern
    @pydecorator.str
    def fmt(self,pattern,cli=False):
        """Returns a formatted version of file"""
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


    # Checks

    def inpath(self,path):
        if len(self.path)-1 < len(path):
            return False
        for p1,p2 in zip(self.path,path):
            if p1 != p2:
                return False
        return True

    def is_match(self,pattern):
        """does match unix style [pattern]"""
        return fnmatch.fnmatch(self.filepath,pattern)

    def is_ftype(self,ftypes):
        """Check if filetype is one of supplied [ftypes]"""
        return self.filetype in ftypes

    def is_regexp(self,regexp):
        """Check if filepath matches [regexp]"""
        return bool(re.match(regexp,self.filepath))

    # Comparisons

    def cmp(self,other):
        if not isinstance(other,File): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return cmp_paths(self.path,other.path)

    def __eq__(self,other):
        if not isinstance(other,File): return False
        return cmp_paths(self.path,other.path) == 0

    def __ne__(self,other):
        if not isinstance(other,File): return True
        return cmp_paths(self.path,other.path) != 0

    def __lt__(self, other):
        if not isinstance(other,File): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return cmp_paths(self.path,other.path) == -1

    def __le__(self, other):
        if not isinstance(other,File): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return cmp_paths(self.path,other.path) <= 0

    def __gt__(self, other):
        if not isinstance(other,File): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return cmp_paths(self.path,other.path) == 1

    def __ge__(self, other):
        if not isinstance(other,File): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return cmp_paths(self.path,other.path) >= 0
