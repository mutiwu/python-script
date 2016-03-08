#!/usr/bin/env python
# coding=utf-8
import argparse
import Ctrvm
import sys

class runthru(object):
    def __init__(self):
        self.__parser = argparse.ArgumentParser()
        self.__parser.add_argument("-u",
                                   action="store",
                                   dest="user_name",
                                   help="The one who start the vm."
                                  )
        self.__parser.add_argument("-a",
                                   action="store",
                                   dest="new_info",
                                   metavar="user@ip",
                                   help="Add new user to the config file"
                                  )
        self.__parser.add_argument("-l",
                                   action="store",
                                   dest="list_info",
                                   help="Show uses and the corresponding ip."
                                  )
        self.__parser.add_argument("-d",
                                   action="store",
                                   dest="del_user",
                                   help="Remove user and the corresponding config."
                                  )
        self.__args = parser.parse_args(sys.argv[1:])

    def run(self):
        
        if self.__args.user_name is None:
            print self.__parser.print_help()
            sys.exit(1)
        vm = Ctrvm.ctrVm(user_name)
        vm.MeCk()
        vm.simg.CrSn()
        vm.defvm()
        vm.startvm()

    def add(self):



if __name__ == "__main__":
    main()
