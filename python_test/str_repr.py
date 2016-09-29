#!/usr/bin/env python
# coding=utf-8

import datetime

class Hello(object):
#    def __init__(self, name):
#        self.name = name 
    def __str__(self):
 #       return str(datetime.datetime.now()) + ":" +  self.name
        return ""
    def __repr__(self):
        # debug用，只显示，通过ipython声明实例后
        # 实例对象的字符串表示，能够通过evea还原为对象
        return "class __repr__"

if __name__ == "__main__":
    #hello = Hello('guoqian')
    hello = Hello()
    print hello
    hello
