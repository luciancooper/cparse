import os,re

# ============================================ comments ============================================ #

def comment_start(line):
    stack = []
    for i,c in enumerate(line):
        if c == '"' or c =="'":
            if len(stack)==0:
                stack.append(c)
            elif stack[0] == c:
                stack.pop()
        elif c == '#' and len(stack)==0:
            return i
    return None

def strip_comment(line):
    i = comment_start(line)
    return line[:i] if i != None else line

# ============================================ parse ============================================ #

def checkfor_objstart(line,lvl):
    if len(line) <= lvl*4:
        return None
    x = re.match('(?:class|def)(?= )',line[lvl*4:])
    if x == None:
        return None
    else:
        return x.group(0)

def checkfor_indented_line(line,lvl):
    if len(line) == 0 or line=='\n':
        return True
    return line[lvl*4:].startswith('    ')

def parse_pyobjects(lines,lvl):
    lineitr = iter(lines)
    try:
        line = next(lineitr)
        while line != None:
            tobj = checkfor_objstart(line,lvl)
            while tobj == None:
                line = next(lineitr)
                tobj = checkfor_objstart(line,lvl)
            objln = [line]
            try:
                line = next(lineitr)
                while checkfor_indented_line(line,lvl):
                    objln.append(line)
                    line = next(lineitr)
            except StopIteration:
                line = None
            yield tobj,objln
    except StopIteration:
        pass

def parse_pychunk(lines,lvl):
    ind = (lvl*4)*' '
    for t,ln in parse_pyobjects(lines,lvl):
        name = strip_comment(ln[0][lvl*4+len(t)+1:]).strip()
        #assert name.endswith(':'), name
        yield '{}{} {}'.format(ind,t,name[:-1])
        if t == 'def':
            continue
        for subitem in parse_pychunk(ln[1:],lvl+1):
            yield subitem

def parse_pyfile(file):
    with open(file,'r') as f:
        for l in parse_pychunk(f,0):
            yield l


# ============================================ file lines ============================================ #

def pyfile_lines(path):
    with open(path,'r') as file:
        for line in file:
            line = strip_comment(line[:-1])
            i,n = 0,len(line)
            while i < n and line[i]==' ':
                i=i+1
            ind,line = i//4,line[i:]
            if len(line) > 0:
                yield ind,line















