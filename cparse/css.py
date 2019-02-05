
import re,os
import pydecorator
from .util import read_file,iter_reduce,reduce,getkey


class InvalidCSSError(Exception):
    def __init__(self,message):
        super().__init__("Invalid CSS Error: {}".format(message))


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

@pydecorator.list
def parse_css(css):
    def parse_keyword():
        nonlocal css
        kw = re.match(r'@([\w\-]+)',css).group(1)
        try:
            if kw.lower() in ['charset','import','namespace']:
                colon = css.index(";")
                css = css[colon+1:].strip()
            else:
                i,j = parse_codeblock(css)
                css = css[j:].strip()
            return
        except ValueError:
            pass
        raise InvalidCSSError("From Keyword @{}".format(kw))
    
    def parse_rule():
        nonlocal css
        if len(css) == 0:
            raise ValueError
        if css.startswith("@"):
            parse_keyword()
            return parse_rule()
        i,j = parse_codeblock(css)
        selector = css[:i]
        block = css[i+1:j-1]
        css = css[j:].strip()
        return selector,block

    css = remove_comments(css).strip()
    try:
        while True:
            selectors,block = parse_rule()
            properties = PropertyBlock.parse(block)
            for s in Selector.split(selectors):
                yield Rule(s,properties)
    except ValueError:
        pass




# ============================================ Classes (Property) ============================================ #

class Property():
    def __init__(self,key,value):
        self.key = key
        self.value = value
    def __str__(self):
        return "%s: %s;"%(self.key,self.value)

    @classmethod
    def parse(cls,code):
        code = code.strip()
        if code.endswith(';'):
            code = code[:-1]
        m = re.match(r'([\w\-]+)\s*\:\s*',code)
        k,v = m.group(1),code[m.span()[1]:]
        return cls(k,v)


@pydecorator.list
def property_breaks(block):
    stack = []
    for i,c in enumerate(block):
        if c == '"' or c =="'":
            if len(stack)==0:
                stack.append(c)
            elif stack[0] == c:
                stack.pop()
        elif c == ';' and len(stack)==0:
            yield i


class PropertyBlock():
    def __init__(self,properties):
        self.properties = properties

    def __str__(self):
        return '\n'.join(str(x) for x in self.properties)

    def indented(self):
        return '\n'.join("\t%s"%x for x in self.properties)
        
    @classmethod
    def parse(cls,code):
        code = code.strip()
        breaks = property_breaks(code)
        return cls([Property.parse(code[i+1:j]) for i,j in iter_reduce(breaks,-1)])
    
    def stack(self,other):
        """Stacks self on top of other"""
        if isinstance(other,PropertyBlock):
            return PropertyBlock(self.properties + other.properties)
        if isinstance(other,Property):
            return PropertyBlock(self.properties+[other])
        raise ValueError("Cannot perform stack operation with object of type {}".format(type(other).__name__))


# ============================================ Classes (Selector) ============================================ #


@pydecorator.list
def selector_splits(block):
    stack = []
    for i,c in enumerate(block):
        if c == '"' or c =="'":
            if len(stack)==0:
                stack.append(c)
            elif stack[0] == c:
                stack.pop()
        elif c == ',' and len(stack)==0:
            yield i

@pydecorator.list
def selector_breaks(code):
    qstack = []
    pstack = 0
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
            continue
        if c == ')':
            if pstack == 0:
                raise InvalidCSSError("Unbalanced Parentheses: '{}'".format(code))
            pstack -= 1
            continue
        if pstack == 0 and (c == ' ' or c == '+' or c == '>' or c == '~'):
            yield i

@pydecorator.list
def merge_consecutive(indexes,merge=slice):
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


@pydecorator.list
def selector_attribute_blocks(code):
    qstack = []
    pstack = 0
    bstart = None
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
            if pstack == 0:
                raise InvalidCSSError("Unbalanced Parentheses in selector block: '{}'".format(code))
            pstack -= 1
            continue
        if pstack > 0:
            continue
        if c == '[':
            if bstart != None:
                raise InvalidCSSError("Invalid attribute selectors in block: '{}'".format(code))
            bstart = i
        elif c == ']':
            if bstart == None:
                raise InvalidCSSError("Unbalanced Brackets in selector block: '{}'".format(code))
            yield (bstart,i)
            bstart = None

@pydecorator.list
def selector_separators(code):
    qstack = []
    pstack = 0
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
            continue
        if c == ')':
            if pstack == 0:
                raise InvalidCSSError("Unbalanced Parentheses in selector block: '{}'".format(code))
            pstack -= 1
            continue
        if pstack == 0 and (c == '#' or c == ':' or c == '.'):
            yield i


def parse_parenblock(code):
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


PSEUDO_CLASSES = ['active','checked','default','defined','disabled','empty','enabled','first','first-child','first-of-type','focus','focus-visible','focus-within','host','host','hover','indeterminate','in-range','invalid','lang','last-child','last-of-type','left','link','not','nth-child','nth-last-child','nth-last-of-type','nth-of-type','only-child','only-of-type','optional','out-of-range','read-only','read-write','required','right','root','scope','target','valid','visited']
PSEUDO_ELEMENTS = ['after','before','cue','first-letter','first-line','selection','slotted']

def selector_parse_specificity(css):
    """
    Parses selector block
    --------------------------
    Returns:
        [code]: standardized selector (str)
        [specificity]: css specificity calculation (s0,s1,s2)
        [logical]: a boolean indicating if selector makes sense
        [pseudo_element]: a boolean indicating whether or not the selector contains a pseudo_element
    """
    #print(f"selector_parse_specificity: '{css}'")
    code,logical = css,True
    attrinx = selector_attribute_blocks(code)
    attrs,s1 = [code[i:j+1] for i,j in attrinx],len(attrinx)
    if len(attrinx) > 0:
        code = code[:attrinx[0][0]]+''.join(code[x1[1]+1:x2[0]] for x1,x2 in iter_reduce(attrinx))+code[attrinx[-1][1]+1:]
        # TODO - Logical Check -> ex attr selectors [a='b'][a='c'] will never select anything 

    sep = merge_consecutive(selector_separators(code),range)
    #print(f"Code: '{code}' Seps: {sep}")
    if any(type(x)==range and (len(x) > 2 or not all(code[i]==':' for i in x)) for x in sep):
        raise InvalidCSSError("invalid selector block: '{}'".format(css))
    sep = [min(x) if type(x) == range else x for x in sep]
    if len(sep) == 0:
        if code != '*':
            return code + ''.join(attrs),(0,s1,1),logical,False
        return (''.join(attrs) if s1 > 0 else '*'),(0,s1,0),logical,False
    ele = code[:sep[0]]
    ele,s2 = ('',0) if ele == '*' or ele=='' else (ele,1) 
    components = [code[i:j] for i,j in iter_reduce(sep+[len(code)])]
    # ======= ID Selectors ======= #
    ids = sorted([x for x in components if x.startswith('#')])
    if len(set(ids)) > 1:
        # illogical selector (multiple ids)
        logical = False
    s0 = len(ids)
    # ======= Class Selectors ======= #
    classes = sorted([x for x in components if x.startswith('.')])
    s1 += len(classes)
    # ======= Pseudo Selectors ======= #
    pseudo = [x for x in components if x.startswith(':')]
    pseudo_tag = [re.match(r'::?([\w\-]+)',x).group(1) for x in pseudo]
    pseudo_ele = [int(x in PSEUDO_ELEMENTS) for x in pseudo_tag]

    # == Pseudo classes == #
    pseudo_cls = [x for x,e in zip(pseudo,pseudo_ele) if e==0]
    if any(x.startswith('::') for x in pseudo_cls):
        raise InvalidCSSError("Pseudo classes cannot use '::' syntax: '{}'".format(css))
    for i,pcls in enumerate(pseudo_cls):
        if pcls.startswith(":not"):
            z0,z1 = parse_parenblock(pcls)
            zcode,zspec,zlogic,zpsele = selector_parse_specificity(pcls[z0+1:z1-1])
            if zpsele:
                raise InvalidCSSError(":not pseudo classes cannot contain pseudo element selectors: '{}'".format(pcls))
            s0,s1,s2 = s0+zspec[0],s1+zspec[1],s2+zspec[2]
            pseudo_cls[i] = pcls[:z0+1]+zcode+pcls[z1-1:]
            continue
        s1 += 1
    
    # == Pseudo elements == #
    if sum(pseudo_ele) > 1:
        raise InvalidCSSError("Multiple pseudo elements in selector '{}'".format(css))
    if sum(pseudo_ele) == 1:
        if pseudo_ele[-1] != 1 or not css.endswith(pseudo[-1]):
            raise InvalidCSSError("Pseudo elements must come at the end of selector '{}'".format(css))
        if not pseudo[-1].startswith('::') and pseudo_tag[-1] in ['selection','slotted']:
            raise InvalidCSSError("Pseudo element '{}' must use '::' syntax ('{}')".format(pseudo_tag[-1],css))
        return ele+''.join(ids+classes+attrs+pseudo_cls)+pseudo[-1],(s0,s1,s2+1),logical,True
    
    selcode,spec = ele+''.join(ids+classes+attrs+pseudo_cls),(s0,s1,s2)
    #print(f"\nselector_parse_specificity('{css}') -> '{selcode}' {spec}\n")
    return selcode,spec,logical,False


class Selector():
    def __init__(self,code,specificity,logical):
        self.code = code
        self.specificity = specificity
        self.logical = logical

    def __str__(self):
        #return "%s (%i,%i,%i)"%(self.code,*self.specificity)
        return self.code

    @classmethod
    def parse(cls,code):
        #print(f"{cls.__name__}.parse('{code}')")
        code = code.strip()
        bindex = selector_breaks(code)
        if len(bindex) == 0:
            code,spec,logical,psele = selector_parse_specificity(code)
            return cls(code,spec,logical)
        if bindex[0] == 0 or bindex[-1] == len(code)-1:
            raise InvalidCSSError("Invalid Selector: '{}'".format(code))
        breaks = merge_consecutive(bindex,slice)
        #segs = [code[(i+1 if type(i)==int else i[1]+1):(j if type(j)==int else j[0])] for i,j in iter_reduce(breaks+[len(code)],-1)]
        #joins = [' ' if x.isspace() else x.strip() for x in (code[i[0]:i[1]+1] if type(i)==tuple else code[i] for i in breaks)]
        segs = [code[(i+1 if type(i)==int else i.stop):(j if type(j)==int else j.start)] for i,j in iter_reduce(breaks+[len(code)],-1)]
        joins = [' ' if x.isspace() else x.strip() for x in (code[i] for i in breaks)]
        #print("Segs: %s Joins: %s"%(''.join("[%s]"%x for x in segs),''.join("[%s]"%x for x in joins)))
        if any(len(x)>1 for x in joins):
            raise InvalidCSSError("Invalid Selector: '{}'".format(code))
        segs,specs,logical,psele = zip(*(selector_parse_specificity(x) for x in segs))
        if any(psele[:-1]):
            raise InvalidCSSError("Invalid Selector, pseudo elements must appear after all other selectors ('{}')".format(code))
        key = ''.join([segs[0]]+[j+x for j,x in zip(joins,segs[1:])])
        spec = reduce(lambda x1,x2: tuple(v1+v2 for v1,v2 in zip(x1,x2)),specs)
        logical = all(logical)
        return cls(key,spec,logical)

    @classmethod
    def split(cls,code):
        code = code.strip()
        splits = selector_splits(code)
        return [cls.parse(code[i+1:j].strip()) for i,j in iter_reduce(splits+[len(code)],-1)]

    def cmp_spec(self,other):
        """Returns [0 --> equal] [1 --> self takes precident over other] [-1 --> other takes precident over self]"""
        if not isinstance(other,Selector):
            raise ValueError("Cannot perform comparison operation with object of type {}".format(type(other).__name__))
        s0,s1,s2 = (x0-x1 for x0,x1 in zip(self.specificity,other.specificity))
        return (1 if s0 > 0 else -1) if s0 != 0 else (1 if s1 > 0 else -1) if s1 != 0 else 0 if s2 == 0 else 1 if s2 > 0 else -1

    def cmp_key(self,other):
        if not isinstance(other,Selector):
            raise ValueError("Cannot perform comparison operation with object of type {}".format(type(other).__name__))
        return 0 if self.code == other.code else 1 if self.code > other.code else -1
        
    

# ============================================ Classes (Rule) ============================================ #


class FileRuleAttr():
    def __init__(self,rindex,findex=None,filename=None):
        self.rindex = rindex
        if findex is not None:
            self.findex = findex
        if filename is not None: 
            self.filename = filename
    
    def __str__(self): 
        if hasattr(self,'filename'):
            if hasattr(self,'findex'):
                return "[{}-{} : {}]".format(getattr(self,'findex'),getattr(self,'filename'),self.rindex)
            return "[{} : {}]".format(getattr(self,'filename'),self.rindex)
        if hasattr(self,'findex'):
            return "[{} : {}]".format(getattr(self,'findex'),self.rindex)
        return "[{}]".format(self.rindex)
    
    def cmp(self,other):
        if type(other) is not FileRuleAttr:
            raise ValueError("Cannot perform comparison operation with object of type {}".format(type(other).__name__))
        if hasattr(self,'findex') != hasattr(other,'findex'):
            raise ValueError("Cannot compare file attr of two rules with different file awareness")
        finx0,finx1 = getattr(self,'findex',None),getattr(other,'findex',None)
        if finx0 != finx1:
            return 1 if finx0 > finx1 else -1
        rinx0,rinx1 = self.rindex,other.rindex
        return 0 if rinx0==rinx1 else 1 if rinx0 > rinx1 else -1

    def __eq__(self,other):
        if not isinstance(other,FileRuleAttr): return False
        return self.cmp(other) == 0

    def __ne__(self,other):
        if not isinstance(other,FileRuleAttr): return True
        return self.cmp(other) != 0

    def __lt__(self, other):
        if not isinstance(other,FileRuleAttr): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.cmp(other) == -1

    def __le__(self, other):
        if not isinstance(other,FileRuleAttr): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.cmp(other) <= 0

    def __gt__(self, other):
        if not isinstance(other,FileRuleAttr): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.cmp(other) == 1

    def __ge__(self, other):
        if not isinstance(other,FileRuleAttr): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.cmp(other) >= 0


class Rule():
    def __init__(self,selector,block):
        self.selector = selector
        self.block = block

    def __str__(self):
        return str(self.selector)

    def __repr__(self):
        return "%s {\n%s\n}"%(self.selector,self.block.indented())
    
    
    
    def cmp_specificity(self,other):
        if isinstance(other,Rule):
            return self.selector.cmp_spec(other.selector)
        if isinstance(other,Selector):
            return self.selector.cmp_spec(other)
        raise ValueError("Cannot perform comparison operation with object of type {}".format(type(other).__name__))
    
    def cmp_selector(self,other):
        if isinstance(other,Rule):
            return self.selector.cmp_key(other.selector)
        if isinstance(other,Selector):
            return self.selector.cmp_key(other)
        raise ValueError("Cannot perform comparison operation with object of type {}".format(type(other).__name__))

    def cmp_fattr(self,other):
        if not isinstance(other,Rule):
            raise ValueError("Cannot perform comparison operation with object of type {}".format(type(other).__name__))
        return getattr(self,'fattr').cmp(getattr(other,'fattr'))
    




@pydecorator.mergesort(duplicate_values=True)
def sortrule_fattr(a,b):
    return a.cmp_fattr(b)



class MergedRule(Rule):
    def __init__(self,selector,block,fattrs):
        super().__init__(selector,block)
        self.fattrs = fattrs
    
    @classmethod
    def mergerules(cls,rules):
        if len(rules) == 0:
            raise ValueError("Must provide at least 1 rule")
        if len(rules) == 1:
            return rules[0]
        if not all(isinstance(x,Rule) for x in rules):
            raise ValueError("Rules must all be instances of FileRule")
        if not all(r0.cmp_selector(r1)==0 for r0,r1 in iter_reduce(rules)):
            raise ValueError("Cannot merge rules with different selectors")
        rules = sortrule_fattr(rules)
        block = reduce(lambda r0,r1 : r0.stack(r1),[x.block for x in rules])
        fattrs = [getattr(x,'fattr') for x in rules]
        return cls(rules[0].selector,block,fattrs)

    @property
    def fattr(self):
        return max(self.fattrs)



# ============================================ CSS File ============================================ #

@pydecorator.mergesort_groups
def grouprules_specificity(a,b):
    return a.cmp_specificity(b)

@pydecorator.mergesort_groups
def grouprules_selector(a,b):
    return a.cmp_selector(b)


class CSSFile():
    def __init__(self,rules,**kwargs):
        self.rules = rules
        for k,v in kwargs.items():
            setattr(self,k,v)
        
    @classmethod
    def read_file(cls,path,**kwargs):
        rules = parse_css(read_file(path))
        fname,findex = os.path.basename(path),getkey(kwargs,'findex',default=None)
        for i,rule in enumerate(rules):
            rule.fattr = FileRuleAttr(i,findex=findex,filename=fname)
        return cls(rules,path=path,fname=fname,**kwargs)

    
    def group_selectors(self):
        index = grouprules_specificity(range(len(self)),self.rules)
        groups = [a for b in [grouprules_selector(x,self.rules) for x in index] for a in b]
        rules = [MergedRule.mergerules([self.rules[i] for i in x]) for x in groups]
        return CSSFile(sortrule_fattr(rules),**self._kwattrs_('path','fname','findex'))

    
    @pydecorator.dict
    def _kwattrs_(self,*keys):
        for k in keys:
            if not hasattr(self,k):
                continue
            yield k,getattr(self,k)
    
    def __len__(self): return len(self.rules)
    
    def __str__(self):
        if hasattr(self,'fname'):
            return "{} ({})".format(getattr(self,'fname'),len(self))
        return "CSSFile ({})".format(len(self))

    def __repr__(self):
        return "\n".join(repr(x) for x in self.rules)
        
    def __iter__(self):
        for r in self.rules:
            yield r
