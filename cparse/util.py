import pydecorator
from datetime import datetime

__all__ = ['extract','iter_reduce','timestamp']

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

def timestamp(ts):
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
