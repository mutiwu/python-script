#!/usr/bin/env python
# coding=utf-8
class a(object):
    def __init__(self):
        pass

    def test_a(self):
        print self.__class__.__name__




c = a()
c.test_a()
