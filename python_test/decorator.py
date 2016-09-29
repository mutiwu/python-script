#!/usr/bin/env python
# coding=utf-8

import datetime

def test_deco(fn):
    def new_fn():
        print datetime.datetime.now()
        fn()
        print datetime.datetime.now()
    new_fn.__name__ = fn.__name__
    new_fn.__doc__ = fn.__doc__
    return new_fn

def t2_d(fn):
    def newfn(*args, **kwargs):
        print datetime.datetime.now()
        tt = fn(*args, **kwargs)
        print tt
        print datetime.datetime.now()
        return tt
    return newfn



@test_deco
def Hello():
    print "Hello world"

@t2_d
def h2():
    return "hello2"

Hello()
c = h2()
print c
