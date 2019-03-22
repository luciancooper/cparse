
import sys,re,os
import pydecorator
from .util import read_file,getkey,is_url,split_url,cli_warning
from .fpath import Path
from .tree import maketree
from html.parser import HTMLParser

__all__ = ['linktree']

# Depreciated
def relative_path(root,path):
    """both [root] and [path] are in split tuple form"""
    i = 0
    while i < len(path) and path[i]=='..':
        i+=1
    if i == 0:
        return root + path
    if i > len(root):
        # Relative goes back further than root, return path relative to root
        return ('..',)*(i-len(root))+path[i:]
    return root[:-i]+path[i:]


@pydecorator.mergesort(duplicate_values=False)
def sortset(a,b):
    return 1 if a > b else -1 if a < b else 0


class linktree():
    def __init__(self,html,scripts,stylesheets):
        self.html = html
        self.scripts = scripts
        self.stylesheets = stylesheets

    @staticmethod
    def _localpath(root,file):
        file = os.path.normcase(file)
        if not os.path.isabs(file):
            file = os.path.normpath(os.path.join(root,file))
        return file

    @classmethod
    def from_file(cls,path):
        parser = LinkParser(path)
        if is_url(path):
            raise NotImplementedError("havn't implemented link parsing from urls yet ({})".format(path))
        root = os.path.split(path)[0]
        scripts = [cls._localpath(root,f) for f in parser.scripts if not is_url(f)]
        stylesheets = [cls._localpath(root,f) for f in parser.stylesheets if not is_url(f)]
        return cls([path],scripts,stylesheets)

    def add_file(self,path):
        parser = LinkParser(path)
        if is_url(path):
            raise NotImplementedError("havn't implemented link parsing from urls yet ({})".format(path))
        root = os.path.split(path)[0]
        scripts = [self._localpath(root,f) for f in parser.scripts if not is_url(f)]
        stylesheets = [self._localpath(root,f) for f in parser.stylesheets if not is_url(f)]
        self.html = sortset(self.html+[path])
        self.scripts = sortset(self.scripts+scripts)
        self.stylesheets = sortset(self.stylesheets+stylesheets)

    def __add__(self,other):
        if type(other) is not linktree:
            raise ValueError("Cannot add {} to linktree".format(type(other)))
        return self.__class__(sortset(self.html+other.html),sortset(self.scripts+other.scripts),sortset(self.stylesheets+other.stylesheets))

    def __iadd__(self,other):
        if type(other) is not linktree:
            raise ValueError("Cannot add {} to linktree".format(type(other)))
        self.html = sortset(self.html+other.html)
        self.scripts = sortset(self.scripts+other.scripts)
        self.stylesheets = sortset(self.stylesheets+other.stylesheets)
        return self

    def files(self,html=True,scripts=True,stylesheets=True):
        files = (self.html if html else [])+(self.scripts if scripts else [])+(self.stylesheets if stylesheets else [])
        if len(files)==0:
            return files
        root = os.path.join(os.path.commonpath(files),"")
        return [f[len(root):] for f in files]

    def tree(self,html=True,scripts=True,stylesheets=True,cli=False):
        files = (self.html if html else [])+(self.scripts if scripts else [])+(self.stylesheets if stylesheets else [])
        if len(files)==0:
            return files
        root = os.path.join(os.path.commonpath(files),"")
        files = sorted([Path(f[len(root):],f) for f in files])
        return '\n'.join(['.']+maketree(files,fmt='%n',cli=cli))



class LinkParser(HTMLParser):

    def __init__(self,file):
        """Parse all links in input file. File must be an absolute path"""
        super().__init__()
        self.scripts = set()
        self.stylesheets = set()
        self.feed(read_file(file))

    # Handle start tag event
    def handle_starttag(self, tag, attrs):
        if tag == "link":
            attrs = dict(attrs)
            if not getkey(attrs,"rel") == "stylesheet":
                return
            href = getkey(attrs,"href")
            if href != None:
                self.stylesheets.add(href)
            return
        if tag == "script":
            attrs = dict(attrs)
            if not getkey(attrs,'type','').startswith("text/javascript"):
                return
            src = getkey(attrs,"src")
            if src != None:
                self.scripts.add(src)
            return
