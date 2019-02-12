import re,pydecorator
from ..util import is_iterable,iter_reduce

__all__ = ['Property','PropertyBlock']

class Property():
    def __init__(self,key,value):
        self.key = key
        self.value = value
    def __str__(self):
        return "{}: {};".format(self.key,self.value)

    @classmethod
    def parse(cls,code):
        code = code.strip()
        if code.endswith(';'):
            code = code[:-1]
        m = re.match(r'([\w\-]+)\s*\:\s*',code)
        k,v = m.group(1),code[m.span()[1]:].strip()
        return cls(k,v)

    # ============== Sorting ============== #

    def cmp(self,other):
        if not isinstance(other,Property): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return -1 if self.key < other.key else 1 if self.key > other.key else 0

    def __eq__(self,other):
        if not isinstance(other,Property): return False
        return self.key == other.key and self.value == other.value

    def __ne__(self,other):
        if not isinstance(other,Property): return True
        return self.key != other.key or self.value != other.value

    def __lt__(self, other):
        if not isinstance(other,Property): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.key < other.key

    def __le__(self, other):
        if not isinstance(other,Property): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.key <= other.key

    def __gt__(self, other):
        if not isinstance(other,Property): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.key > other.key

    def __ge__(self, other):
        if not isinstance(other,Property): raise ValueError("Cannot compare to object of type {}".format(type(other).__name__))
        return self.key >= other.key

    # ============== Concatenation ============== #

    def __add__(self,other):
        if type(other) == Property:
            return PropertyBlock([self,other])
        if type(other) == PropertyBlock:
            return PropertyBlock([self]+other.properties)
        if is_iterable(other):
            other = list(other)
            if any(type(x) != Property for x in other):
                raise ValueError("Cannot concatenate unless all elements of iterable are instances of Property")
            return PropertyBlock([self]+other)
        raise ValueError("Cannot concatenate property with object of type {}".format(type(other).__name__))

    def __radd__(self,other):
        if is_iterable(other):
            other = list(other)
            if any(type(x) != Property for x in other):
                raise ValueError("Cannot concatenate unless all elements of iterable are instances of Property")
            return PropertyBlock(other+[self])
        raise ValueError("Cannot concatenate property with object of type {}".format(type(other).__name__))



# ============================================ Blocks ============================================ #


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

    @classmethod
    def parse(cls,code):
        code = code.strip()
        breaks = property_breaks(code)
        return cls([Property.parse(code[i+1:j]) for i,j in iter_reduce(breaks,-1)])

    def __str__(self):
        return '\n'.join(str(x) for x in self.properties)

    def indented(self,count=1):
        return '\n'.join("\t"*count+str(x) for x in self.properties)

    def __len__(self):
        return len(self.properties)
    
    def __iter__(self):
        for p in self.properties:
            yield p

    def __eq__(self,other):
        if not isinstance(other,PropertyBlock): return False
        if len(self) != len(other):
            return False
        return all(p0 == p1 for p0,p1 in zip(self.properties,other.properties))

    def __ne__(self,other):
        if not isinstance(other,PropertyBlock): return True
        if len(self) != len(other):
            return True
        return any(p0 != p1 for p0,p1 in zip(self.properties,other.properties))
    
    
    @staticmethod
    @pydecorator.mergesort_groups
    def group_properties(a,b):
        return a.cmp(b)
    
    def condense(self,inplace=False):
        """Removes redundant properties"""
        groups = self.group_properties(range(len(self.properties)),self.properties)
        indexes = [max(g) for g in groups]
        properties = [self.properties[i] for i in sorted(indexes)]
        if inplace == False:
            return PropertyBlock(properties)
        self.properties = properties


    def sorted(self):
        return PropertyBlock(sorted(self.properties))

    
    # ============== Concatenation ============== #

    
    def __add__(self,other):
        if type(other) == Property:
            return PropertyBlock(self.properties+[other])
        if type(other) == PropertyBlock:
            return PropertyBlock(self.properties+other.properties)
        if is_iterable(other):
            other = list(other)
            if any(type(x) != Property for x in other):
                raise ValueError("Cannot concatenate unless all elements of iterable are instances of Property")
            return PropertyBlock(self.properties+other)
        raise ValueError("Cannot concatenate property block with object of type {}".format(type(other).__name__))

    def __radd__(self,other):
        if is_iterable(other):
            other = list(other)
            if any(type(x) != Property for x in other):
                raise ValueError("Cannot concatenate unless all elements of iterable are instances of Property")
            return PropertyBlock(other+self.properties)
        raise ValueError("Cannot concatenate property block with object of type {}".format(type(other).__name__))
    
    def __iadd__(self,other):
        if type(other) == Property:
            self.properties = self.properties + [other]
            return self
        if type(other) == PropertyBlock:
            self.properties = self.properties + other.properties
            return self
        if is_iterable(other):
            other = list(other)
            if any(type(x) != Property for x in other):
                raise ValueError("Cannot concatenate unless all elements of iterable are instances of Property")
            self.properties = self.properties + other
            return self
        raise ValueError("Cannot concatenate property block with object of type {}".format(type(other).__name__))
    


