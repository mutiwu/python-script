#!/usr/bin/env python
# coding=utf-8

import random

def changeMac():
    maclist = ["52", "54"]
    for i in range(1, 5):
        randstr = "".join(random.sample("0123456789abcdef", 2))
        maclist.append(randstr)
    randmac = ":".join(maclist)
    return randmac

print changeMac()
