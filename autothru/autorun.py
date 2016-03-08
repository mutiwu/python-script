#!/usr/bin/env python
# coding=utf-8

import argparse
import Ctrvm
import sys
import Config
import re

parser = argparse.ArgumentParser()

parser.add_argument("-u",
                    action="store",
                    dest="run",
                    help="The one who start the vm."
                   )
parser.add_argument("-a",
                    action="store",
                    dest="new_info",
                    metavar="user team ip",
                    help="Add new user to the config file"
                   )
parser.add_argument("-l",
                    action="store",
                    dest="list_info",
                    help="Show uses and the corresponding ip."
                   )
parser.add_argument("-d",
                    action="store",
                    dest="del_user",
                    help="Remove user and the corresponding config."
                   )
args = parser.parse_args(sys.argv[1:])

if len(sys.argv[1:]) > 1:
    print "More than 1 args found, please give only one arg."
    parser.print_help()
    sys.exit(1)

cfg = Config.Config()
if args.run:
    vm = Ctrvm.ctrVm(args.run)
    vm.MeCk()
    vm.simg.CrSn()
    vm.defvm()
    vm.startvm()

if args.new_info:
    pcom = re.compile(r"^(\w+)\s(\w+)\s(([0-9]{0,3}\.){0,3}[0-9])$")
    pobj = pcom.search(args.new_info)
    user_name = pobj.group(1)
    team_name = pobj.group(2)
    user_ip = pobj.group(3)
    cfg.add_users(user_name, team_name, user_ip)

if args.list_info:
    cfg.list_users_by_team()

if args.del_user:
    if cfg.del_users(args.del_user):
        print "User %s deleted, also corresponding infos." % args.del_user
        sys.exit(0)
    print "No user %s found in the configuration file." % args.del_user
    sys.exit(1)

