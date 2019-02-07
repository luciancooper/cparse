
import re,pydecorator
from ..util import reduce,iter_reduce,is_iterable
from . import InvalidCSSError


__all__ = ['Selector']


# ============================================ Classes (Selector) ============================================ #

@pydecorator.list
def merge_consecutive(indexes,merge=slice):
    """Merges together consecutive values in a sorted list of integers"""
    it = iter(indexes)
    try:
        v0 = next(it)
    except StopIteration:
        return
    try:
        while True:
            v1 = next(it)
            if v1-v0 > 1:
                yield v0
                v0,v1 = v1,None
                continue
            v,v0,v1 = v0,v1,None
            try:
                while True:
                    v1 = next(it)
                    if v1-v0 > 1:
                        yield merge(v,v0+1)
                        v0,v,v1 = v1,None,None
                        break
                    v0,v1 = v1,None
            except StopIteration:
                yield merge(v,v0+1)
                return
    except StopIteration:
        yield v0


def add_specificity(a,b):
    return tuple(x0+x1 for x0,x1 in zip(a,b))

def cmp_specificity(a,b):
    s0,s1,s2 = (x0-x1 for x0,x1 in zip(a,b))
    return (1 if s0 > 0 else -1) if s0 != 0 else (1 if s1 > 0 else -1) if s1 != 0 else 0 if s2 == 0 else 1 if s2 > 0 else -1
    

class SelectorUnit():
    """
    [code]: standardized selector (str)
    [specificity]: css specificity calculation (s0,s1,s2)
    [logical]: a boolean indicating if selector makes sense
    [pseudo_element]: a boolean indicating whether or not the selector contains a pseudo_element
    """

    def __init__(self,code,specificity,logical,pseudo_element):
        self.code = code
        self.specificity = tuple(specificity)
        self.logical = logical
        self.pseudo_element = pseudo_element

    def __str__(self):
        return self.code

    

    # ============== parsing ============== #

    @staticmethod
    def _parse_attributes(code):
        """Finds the attribute selectors in css selector"""
        qstack,pstack,bstart,index = [],0,None,[]
        for i,c in enumerate(code):
            if c == '"' or c =="'":
                if pstack == 0 and bstart == None:
                    raise InvalidCSSError("Invalid selector block: '{}'".format(code))
                if len(qstack)==0:
                    qstack.append(c)
                elif qstack[0] == c:
                    qstack.pop()
                continue
            if len(qstack) > 0:
                continue
            if c == '(':
                pstack += 1
                continue
            if c == ')':
                if pstack == 0: raise InvalidCSSError("Unbalanced Parentheses in selector block: '{}'".format(code))
                pstack -= 1
                continue
            if pstack > 0:
                continue
            if c == '[':
                if bstart != None: raise InvalidCSSError("Invalid attribute selectors in block: '{}'".format(code))
                bstart = i
            elif c == ']':
                if bstart == None:
                    raise InvalidCSSError("Unbalanced Brackets in selector block: '{}'".format(code))
                index.append((bstart,i))
                bstart = None
        return index
    
    @staticmethod
    def _parse_separators(code):
        qstack,pstack,indexes = [],0,[]
        for i,c in enumerate(code):
            if c == '"' or c =="'":
                if pstack == 0:
                    raise InvalidCSSError("Invalid selector block: '{}'".format(code))
                if len(qstack)==0:
                    qstack.append(c)
                elif qstack[0] == c:
                    qstack.pop()
                continue
            if len(qstack) > 0:
                continue
            if c == '(':
                pstack += 1
            elif c == ')':
                if pstack == 0:
                    raise InvalidCSSError("Unbalanced Parentheses in selector block: '{}'".format(code))
                pstack -= 1
            elif pstack == 0 and (c == '#' or c == ':' or c == '.'):
                indexes.append(i)
        return indexes

    
    @staticmethod
    def _parse_parenblock(code):
        """
        returns the start and end indexes of parentheses block
        ex: input 'not(div)' -> returns 3,8 (slice looks like this: '(div)')
        ex: input 'not(not(div)) -> returns 3,13 (slice looks like this: '(not(div))')
        """
        qstack = []
        i,n = code.index("("),len(code)
        j,stack = i+1,1
        while j < n and stack > 0:
            if code[j] == '"' or code[j] =="'":
                if len(qstack)==0:
                    qstack.append(code[j])
                elif qstack[0] == code[j]:
                    qstack.pop()
                j+=1
                continue
            if len(qstack) > 0:
                j+=1
                continue
            if code[j] == '(':
                stack += 1
            elif code[j] == ')':
                if stack == 0: raise InvalidCSSError("Unbalanced Parentheses in selector block: '{}'".format(code))
                stack -= 1
            j+=1
        if stack > 0:
            raise InvalidCSSError("Code: '{}'".format(code[i:j]))
        return i,j

    
    PSEUDO_CLS = ['active','checked','default','defined','disabled','empty','enabled','first','first-child','first-of-type','focus','focus-visible','focus-within','host','host','hover','indeterminate','in-range','invalid','lang','last-child','last-of-type','left','link','not','nth-child','nth-last-child','nth-last-of-type','nth-of-type','only-child','only-of-type','optional','out-of-range','read-only','read-write','required','right','root','scope','target','valid','visited']
    PSEUDO_ELE = ['after','before','cue','first-letter','first-line','selection','slotted']

    @classmethod
    def parse(cls,css):
        """ Parses selector block, returns SelectorUnit instance"""
        code,logical,spec = css,True,[0,0,0]
        attrinx = cls._parse_attributes(code)
        attrs = [code[i:j+1] for i,j in attrinx]
        spec[1] += len(attrinx)

        if len(attrinx) > 0:
            code = code[:attrinx[0][0]]+''.join(code[x1[1]+1:x2[0]] for x1,x2 in iter_reduce(attrinx))+code[attrinx[-1][1]+1:]
            # TODO - Logical Check -> ex attr selectors [a='b'][a='c'] will never select anything 

        sep = merge_consecutive(cls._parse_separators(code),range)
        if any(type(x)==range and (len(x) > 2 or not all(code[i]==':' for i in x)) for x in sep):
            raise InvalidCSSError("invalid selector block: '{}'".format(css))
        sep = [min(x) if type(x) == range else x for x in sep]
        if len(sep) == 0:
            if code != '*':
                spec[2]+=1
                return cls(code + ''.join(attrs),spec,logical,False)
            return cls(''.join(attrs) if len(attrs) > 0 else '*',spec,logical,False)
        ele = code[:sep[0]]
        ele,spec[2] = ('',0) if ele == '*' or ele=='' else (ele,1)
        components = [code[i:j] for i,j in iter_reduce(sep+[len(code)])]
        # ======= ID Selectors ======= #
        ids = sorted([x for x in components if x.startswith('#')])
        if len(set(ids)) > 1:
            # illogical selector (multiple ids)
            logical = False
        spec[0] = len(ids)
        # ======= Class Selectors ======= #
        classes = sorted([x for x in components if x.startswith('.')])
        spec[1] += len(classes)
        # ======= Pseudo Selectors ======= #
        pseudo = [x for x in components if x.startswith(':')]
        pseudo_tag = [re.match(r'::?([\w\-]+)',x).group(1) for x in pseudo]
        pseudo_ele = [int(x in cls.PSEUDO_ELE) for x in pseudo_tag]

        # == Pseudo classes == #
        pseudo_cls = [x for x,e in zip(pseudo,pseudo_ele) if e==0]
        if any(x.startswith('::') for x in pseudo_cls):
            raise InvalidCSSError("Pseudo classes cannot use '::' syntax: '{}'".format(css))
        for i,pcls in enumerate(pseudo_cls):
            if pcls.startswith(":not"):
                z0,z1 = cls._parse_parenblock(pcls)
                notsel = cls.parse(pcls[z0+1:z1-1])
                if notsel.pseudo_element:
                    raise InvalidCSSError(":not pseudo classes cannot contain pseudo element selectors: '{}'".format(pcls))
                spec = list(add_specificity(spec,notsel.specificity))
                pseudo_cls[i] = pcls[:z0+1]+str(notsel)+pcls[z1-1:]
                continue
            spec[1] += 1
        
        # == Pseudo elements == #
        if sum(pseudo_ele) > 1:
            raise InvalidCSSError("Multiple pseudo elements in selector '{}'".format(css))
        if sum(pseudo_ele) == 1:
            if pseudo_ele[-1] != 1 or not css.endswith(pseudo[-1]):
                raise InvalidCSSError("Pseudo elements must come at the end of selector '{}'".format(css))
            if not pseudo[-1].startswith('::') and pseudo_tag[-1] in ['selection','slotted']:
                raise InvalidCSSError("Pseudo element '{}' must use '::' syntax ('{}')".format(pseudo_tag[-1],css))
            spec[2]+=1
            return cls(ele+''.join(ids+classes+attrs+pseudo_cls)+pseudo[-1],spec,logical,True)
        return cls(ele+''.join(ids+classes+attrs+pseudo_cls),spec,logical,False)


class Selector():
    """A container class for SelectorUnits"""
    def __init__(self,units,combinators):
        assert len(units)-1==len(combinators), "units and combinators invalid"
        self.units = units
        self.combinators = combinators
        self.specificity = reduce(add_specificity,[x.specificity for x in units])
        self.logical = all(x.logical for x in units)

    def __str__(self):
        return ''.join([str(self.units[0])]+[c+str(u) for c,u in zip(self.combinators,self.units[1:])])

    # ============== parsing ============== #

    @staticmethod
    def _parse_combinators(code):
        qstack,pstack,index = [],0,[]
        for i,c in enumerate(code):
            if c == '"' or c =="'":
                if len(qstack)==0:
                    qstack.append(c)
                elif qstack[0] == c:
                    qstack.pop()
                continue
            if len(qstack) > 0:
                continue
            if c == '(':
                pstack += 1
            elif c == ')':
                if pstack == 0: raise InvalidCSSError("Unbalanced Parentheses: '{}'".format(code))
                pstack -= 1
            elif pstack == 0 and (c == ' ' or c == '+' or c == '>' or c == '~'):
                index.append(i)
        return index


    @classmethod
    def parse(cls,code):
        code = code.strip()
        combinators = cls._parse_combinators(code)
        if len(combinators) == 0:
            return cls([SelectorUnit.parse(code)],[])
        if combinators[0] == 0 or combinators[-1] == len(code)-1:
            raise InvalidCSSError("Invalid Selector: '{}'".format(code))
        combinators = merge_consecutive(combinators,slice)
        units = [code[(i+1 if type(i)==int else i.stop):(j if type(j)==int else j.start)] for i,j in iter_reduce(combinators+[len(code)],-1)]
        combinators = [' ' if x.isspace() else x.strip() for x in (code[i] for i in combinators)]
        if any(len(x)>1 for x in combinators):
            raise InvalidCSSError("Invalid Selector: '{}'".format(code))
        
        units = [SelectorUnit.parse(x) for x in units]
        if any(x.pseudo_element for x in units[:-1]):
            raise InvalidCSSError("Invalid Selector, pseudo elements must appear after all other selectors ('{}')".format(code))
        return cls(units,combinators)

    @classmethod
    def split(cls,code):
        """Splits a block of input selectors separated by commas (ex: 'div,span')"""
        code,splits,qstack = code.strip(),[],[]
        for i,c in enumerate(code):
            if c == '"' or c =="'":
                if len(qstack)==0:
                    qstack.append(c)
                elif qstack[0] == c:
                    qstack.pop()
            elif c == ',' and len(qstack)==0:
                splits.append(i)
        return [cls.parse(code[i+1:j].strip()) for i,j in iter_reduce(splits+[len(code)],-1)]

    # ============== comparison ============== #

    def cmp_spec(self,other):
        """Returns [0 --> equal] [1 --> self takes precident over other] [-1 --> other takes precident over self]"""
        if not isinstance(other,Selector):
            raise ValueError("Cannot perform comparison operation with object of type {}".format(type(other).__name__))
        return cmp_specificity(self.specificity,other.specificity)

    def cmp_key(self,other):
        if not isinstance(other,Selector):
            raise ValueError("Cannot perform comparison operation with object of type {}".format(type(other).__name__))
        a,b = str(self),str(other)
        return 0 if a==b else 1 if a>b else -1
        
    
