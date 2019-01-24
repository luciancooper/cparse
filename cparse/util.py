import pydecorator
from datetime import datetime
import urllib.request
from contextlib import closing
import re
import sys
import os

#__all__ = ['extract','iter_reduce','timestamp','read_file','getkey']


def getkey(d,key,default=None):
    """gets key from dict (d), if key does not exist, return default"""
    if key in d:
        return d[key]
    else:
        return default


@pydecorator.list
def extract(index,collection):
    for x in index:
        yield collection[x]

def iter_reduce(iterable,init=None):
    it = iter(iterable)
    try:
        v0 = next(it) if init is None else init
    except StopIteration:
        return
    for v1 in it:
        yield v0,v1
        v0 = v1

def reduce(fn,iterable,init=None):
    it = iter(iterable)
    try:
        value = next(it) if init is None else init
    except StopIteration:
        return None
    for e in it:
        value = fn(value,e)
    return value


def timestamp(ts):
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


def is_url(path):
    return re.match(r'https?:\/\/',path)

def split_url(url):
    prefix = re.match(r'https?:\/\/',url)
    pieces = url[prefix.end(0):].split('/')
    domain = prefix.group(0)+pieces[0]
    return (domain,)+tuple(pieces[1:])

def read_file(file):
    if is_url(file):
        # Download File
        with closing(urllib.request.urlopen(file)) as response:
            return response.read().decode('utf-8')
        return
    with open(file,'r') as f:
        return f.read()


def cli_warning(message):
    print("\x1b[31mWarning: {}\x1b[0m".format(message),file=sys.stderr)

def cli_cyan(message):
    print("\x1b[36m{}\x1b[0m".format(message),file=sys.stderr)

def cli_green(message):
    print("\x1b[32m{}\x1b[0m".format(message),file=sys.stderr)

def str_col(items,align='>'):
    # (> : right) (< : left) (^ : center)
    s = [str(i) for i in items]
    mx = max(len(x) for x in s)
    a = '{:%s%i}'%(align,mx)
    return [a.format(x) for x in s]

