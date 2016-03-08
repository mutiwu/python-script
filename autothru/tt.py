#!/usr/bin/env python
# coding=utf-8

import argparse
import sys


def test():
    print "that's ok"

parser = argparse.ArgumentParser()
parser.add_argument("-u", action="store", dest="test")

args = parser.parse_args(sys.argv[1:])

if args.test:
    test()
