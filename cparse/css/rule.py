from ..util import iter_reduce,reduce
from .selector import Selector


class CSSRule():
    def __init__(self,selector,block,attr):
        self.selector = selector
        self.block = block
        self.attr = attr

    def __str__(self):
        return "{} {{ ... {} ... }}".format(self.selector,len(self.block))

    def __repr__(self):
        return "{} {{\n{}\n}}".format(self.selector,self.block.indented())

    def indented(self,count=1):
        return "{0:}{1:} {{\n{2:}\n{0:}}}".format(count*'\t',self.selector,self.block.indented(count+1))
    
    def condense(self,inplace=False):
        """Removes redundant properties"""
        if inplace==True:
            self.block.condense(inplace=True)
            return
        return CSSRule(self.selector,self.block.condense(),self.attr)

    # ============== comparison ============== #

    def cmp_specificity(self,other):
        if isinstance(other,CSSRule):
            return self.selector.cmp_spec(other.selector)
        if isinstance(other,Selector):
            return self.selector.cmp_spec(other)
        raise ValueError("Cannot perform comparison operation with object of type {}".format(type(other).__name__))
    
    def cmp_selector(self,other):
        if isinstance(other,CSSRule):
            return self.selector.cmp_key(other.selector)
        if isinstance(other,Selector):
            return self.selector.cmp_key(other)
        raise ValueError("Cannot perform comparison operation with object of type {}".format(type(other).__name__))

    def cmp_attr(self,other):
        if not isinstance(other,CSSRule):
            raise ValueError("Cannot perform comparison operation with object of type {}".format(type(other).__name__))
        return self.attr.cmp(other.attr)
    

class MergedRule(CSSRule):
    def __init__(self,selector,block,attrs):
        self.selector = selector
        self.block = block
        self.attrs = attrs
    
    @classmethod
    def mergerules(cls,rules):
        if len(rules) == 0:
            raise ValueError("Must provide at least 1 rule")
        if len(rules) == 1:
            return rules[0]
        if not all(isinstance(x,CSSRule) for x in rules):
            raise ValueError("Rules must all be instances of FileRule")
        if not all(r0.cmp_selector(r1)==0 for r0,r1 in iter_reduce(rules)):
            raise ValueError("Cannot merge rules with different selectors")
        rules = sorted(rules,key=lambda x: x.attr)
        block = reduce(lambda x,y: x+y,[x.block for x in rules])
        attrs = [x.attr for x in rules]
        return cls(rules[0].selector,block,attrs)
    
    @property
    def attr(self):
        return max(self.attrs)

    def condense(self,inplace=False):
        """Removes redundant properties"""
        if inplace==True:
            self.block.condense(inplace=True)
            return
        return MergedRule(self.selector,self.block.condense(),self.attrs)