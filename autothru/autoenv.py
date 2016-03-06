#!/usr/bin/env python
# coding=utf-8
import argparse
import Ctrvm
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u",
                        action="store",
                        dest="user_name",
                        help="The one who start the vm."
                        )
    args = parser.parse_args(sys.argv[1:])
    if args.user_name is None:
        print parser.print_help()
        sys.exit(1)
    user_name = args.user_name
    vm = Ctrvm.ctrVm(user_name)
    vm.MeCk()
    vm.simg.CrSn()
    vm.defvm()
    vm.startvm()

if __name__ == "__main__":
    main()
