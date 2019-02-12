class InvalidCSSError(Exception):
    def __init__(self,message):
        super().__init__("Invalid CSS Error: {}".format(message))


import re,os,sys
import pydecorator
from ..util import read_file,iter_reduce,reduce,getkey
from .property import *
from .selector import *
from .rule import *


# Define Use

# Parse from input str
# Parse from input file
# Given directory and file list, parse system
# Given html file, parse link system






# ============================================ Parse Helper Functions ============================================ #

def remove_comments(file):
    """returns comments from css file str"""
    try:
        j,i0,i1 = 0,None,None
        while j < len(file):
            i0 = file.index('/*',j)
            i1 = file.index('*/',i0+2)
            file,j,i0,i1 = file[:i0]+file[i1+2:],i0,None,None
    except ValueError:
        if i0 != None:
            file = file[:i0]
    finally:
        return file


def parse_codeblock(css):
    i,n = css.index("{"),len(css)
    j,stack = i+1,1
    while j < n and stack > 0:
        if css[j] == '{':
            stack += 1
        elif css[j] == '}':
            stack -= 1
        j += 1
    if stack > 0:
        raise InvalidCSSError("Code: '{}'".format(css[i:j]))
    return i,j



# ============================================ Parse Code ============================================ #



# ============================================ Original File Attributes ============================================ #


class FileAttr():

    def __init__(self,**kwargs):
        for k,v in kwargs.items():
            setattr(self,k,v)

    def __str__(self):
        name = getattr(self,'name','CSSFile')
        if hasattr(self,'index'):
            return "{}-{}".format(getattr(self,'index'),name)
        return name

    # ============== comparison ============== #

    def cmp(self,other):
        if type(other) is not FileAttr:
            raise ValueError("Cannot perform comparison operation with object of type {}".format(type(other).__name__))
        if hasattr(self,'index') != hasattr(other,'index'):
            raise ValueError("Cannot compare file attr with different awareness")
        i0,i1 = getattr(self,'index',None),getattr(other,'index',None)
        if i0 == i1:
            return 0
        return 1 if i0 > i1 else -1

    def __eq__(self,other):
        if not isinstance(other,FileAttr): return False
        return self.cmp(other) == 0

    def __ne__(self,other):
        if not isinstance(other,FileAttr): return True
        return self.cmp(other) != 0

    def __lt__(self, other):
        if not isinstance(other,FileAttr): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.cmp(other) == -1

    def __le__(self, other):
        if not isinstance(other,FileAttr): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.cmp(other) <= 0

    def __gt__(self, other):
        if not isinstance(other,FileAttr): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.cmp(other) == 1

    def __ge__(self, other):
        if not isinstance(other,FileAttr): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.cmp(other) >= 0

class FileItemAttr():
    def __init__(self,index,fattr):
        self.index = index
        self.fattr = fattr

    def __str__(self):
        return "{}-{}".format(str(self.fattr),self.index)

    def __del__(self):
        del self.fattr
        del self.index


    def cmp(self,other):
        if type(other) is not FileItemAttr:
            raise ValueError("Cannot perform comparison operation with object of type {}".format(type(other).__name__))
        fcmp = self.fattr.cmp(other.fattr)
        if fcmp != 0:
            return fcmp
        return 1 if self.index > other.index else -1 if self.index < other.index else 0

    def __eq__(self,other):
        if not isinstance(other,FileItemAttr): return False
        return self.cmp(other) == 0

    def __ne__(self,other):
        if not isinstance(other,FileItemAttr): return True
        return self.cmp(other) != 0

    def __lt__(self, other):
        if not isinstance(other,FileItemAttr): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.cmp(other) == -1

    def __le__(self, other):
        if not isinstance(other,FileItemAttr): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.cmp(other) <= 0

    def __gt__(self, other):
        if not isinstance(other,FileItemAttr): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.cmp(other) == 1

    def __ge__(self, other):
        if not isinstance(other,FileItemAttr): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.cmp(other) >= 0



# ============================================ Classes (Rule) ============================================ #


# ============================================ CSS File ============================================ #


class CSSContainer():
    """Generic parent class"""
    def __init__(self,rules,attr):
        self.rules = rules
        self.attr = attr

    @staticmethod
    @pydecorator.mergesort_groups
    def grouprules_specificity(a,b):
        return a.cmp_specificity(b)

    @staticmethod
    @pydecorator.mergesort_groups
    def grouprules_selector(a,b):
        return a.cmp_selector(b)


    def __len__(self): return len(self.rules)

    def __iter__(self):
        for r in self.rules:
            yield r

    


class CSSMediaGroup(CSSContainer):
    def __init__(self,selector,rules,attr):
        super().__init__(rules,attr)
        self.selector = selector

    def __str__(self):
        return "@media {}\n{}".format(self.selector,"\n".join("\t"+str(x) for x in self.rules))
    def __repr__(self):
        return "@media {} {{\n{}\n}}".format(self.selector,"\n".join(x.indented(1) for x in self.rules))
    
    @classmethod
    def parse(cls,selector,css,attr):
        # TODO - Parse selector
        x,rules = 0,[]
        css = remove_comments(css).strip()
        try:
            while len(css) > 0:
                if css.startswith("@"):
                    kw = re.match(r'@([\w\-]+)',css).group(1)
                    raise InvalidCSSError("'@{}' keyword found within @media block".format(kw))
                i,j = parse_codeblock(css)
                selector,block,css = css[:i],css[i+1:j-1],css[j:].strip()
                properties = PropertyBlock.parse(block)
                selectors = Selector.split(selector)
                rules.extend(CSSRule(s,properties,FileItemAttr(z+x,attr)) for z,s in enumerate(selectors))
                x += len(selectors)
            return cls(selector,rules,attr)
        except ValueError:
            # raised by parse_codeblock when '{' not found
            pass
        raise InvalidCSSError("'{}'".format(css))

    def group_selectors(self,inplace=False):
        index = self.grouprules_specificity(range(len(self.rules)),self.rules)
        groups = [a for b in [self.grouprules_selector(x,self.rules) for x in index] for a in b]
        rules = sorted([MergedRule.mergerules([self.rules[i] for i in x]) for x in groups],key=lambda x: x.attr)
        if inplace == False:
            return CSSMediaGroup(self.selector,rules,self.attr)
        self.rules = rules

    def condense(self,inplace=False):
        """Removes redundant properties"""
        if inplace==False:
            return CSSMediaGroup(self.selector,[r.condense() for r in self.rules],self.attr)
        for r in self.rules:
            r.condense(inplace=True)
        


class CSSFile(CSSContainer):

    @classmethod
    def from_file(cls,path,**kwargs):
        attr = FileAttr(path=path,name=os.path.basename(path),**kwargs)
        return cls.parse(read_file(path),attr)


    @classmethod
    def parse(cls,css,attr):
        x,rules = 0,[]
        css = remove_comments(css).strip()
        try:
            while len(css) > 0:
                if css.startswith("@"):
                    kw = re.match(r'@([\w\-]+)',css).group(1).lower()
                    try:
                        if kw in ['charset','import','namespace']:
                            colon = css.index(";")
                            value = css[len(kw)+1:colon].strip()
                            if kw == 'import':
                                # TODO - Implement import
                                pass
                            css = css[colon+1:].strip()
                        else:
                            i,j = parse_codeblock(css)
                            selector,block,css = css[len(kw)+1:i],css[i+1:j-1],css[j:].strip()
                            if kw == 'media':
                                rules.append(CSSMediaGroup.parse(selector,block,FileItemAttr(x,attr)))
                                x += 1
                        continue
                    except ValueError:
                        pass
                    raise InvalidCSSError("From Keyword @{}".format(kw))
                i,j = parse_codeblock(css)
                selector,block,css = css[:i],css[i+1:j-1],css[j:].strip()
                properties = PropertyBlock.parse(block)
                selectors = Selector.split(selector)
                rules.extend(CSSRule(s,properties,FileItemAttr(z+x,attr)) for z,s in enumerate(selectors))
                x += len(selectors)
            return cls(rules,attr)
        except ValueError:
            # raised by parse_codeblock when '{' not found
            pass
        raise InvalidCSSError("'{}'".format(css))


    def group_selectors(self,inplace=False):
        index = self.grouprules_specificity(range(len(self.rules)),self.rules)
        groups = [a for b in [self.grouprules_selector(x,self.rules) for x in index] for a in b]
        rules = sorted([MergedRule.mergerules([self.rules[i] for i in x]) for x in groups],key=lambda x: x.attr)
        if inplace==False:
            return CSSFile(rules,self.attr)
        self.rules = rules

    def condense(self,inplace=False):
        """Removes redundant properties"""
        if inplace==False:
            return CSSFile([r.condense() for r in self.rules],self.attr)
        for r in self.rules:
            r.condense(inplace=True)

    def stacked_map(self):
        pblocks = [x.block.sorted() for x in self.rules]
        imap = []
        indexes = [*range(len(self.rules))]
        while len(indexes)>0:
            i,indexes = indexes[0],indexes[1:]
            match = [int(pblocks[i] == pblocks[x]) for x in indexes]
            imap.append([i]+[x for x,m in zip(indexes,match) if m == 1])
            indexes = [x for x,m in zip(indexes,match) if m == 0]
        return imap

    def print(self,file=sys.stdout,linespace=0,stacked=False):
        # TODO - Add color support when file.isatty()
        if stacked == False:
            for r in self.rules:
                print(linespace*'\n',end='',file=file)
                print(repr(r),file=file)
            return
        for inxs in self.stacked_map():
            print(linespace*'\n',end='',file=file)
            selectors = ",\n".join(str(self.rules[i].selector) for i in inxs)
            block = self.rules[inxs[0]].block.indented()
            print("{} {{\n{}\n}}".format(selectors,block),file=file)
        


        

    def __str__(self):
        if hasattr(self.attr,'name'):
            return "{} ({})".format(getattr(self.attr,'name'),len(self))
        return "CSSFile ({})".format(len(self))

    def __repr__(self):
        return "\n".join(repr(x) for x in self.rules)
