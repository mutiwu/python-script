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
                    metavar="USER",
                    help="The one who start the vm."
                   )
parser.add_argument("-a",
                    action="store",
                    dest="new_info",
                    metavar="USER TEAM IP",
                    help="Add new user to the config file"
                   )
parser.add_argument("-s",
                    action="store",
                    dest="list_info",
                    metavar="USER",
                    help="Show uses and the corresponding ip."
                   )
parser.add_argument("-d",
                    action="store",
                    dest="del_user",
                    metavar="USER",
                    help="Remove user and the corresponding config."
                   )
parser.add_argument("--add-imgpath",
                    action="store",
                    dest="img_path",
                    metavar="PATH",
                    help="The base image and snapshot images path."
                   )
parser.add_argument("--add-base",
                    action="store",
                    dest="baseimg",
                    metavar="QCOW2 FILE",
                    help="The base image for the snapshot VMS."
                   )
parser.add_argument("--add-basexml",
                    action="store",
                    dest="basexml",
                    metavar="XML FILE",
                    help="The VM xml file, the xml dir is /etc/libvirt/qemu/ , do not provide the real path of the xml file, just provide the file name is ok."
                   )
parser.add_argument("--add-basemac",
                    action="store",
                    dest="basemac",
                    metavar="MAC ADDRESS",
                    help="The MAC ADDRESS of the base vm, can find it in the xml file."
                   )
args = parser.parse_args(sys.argv[1:])

if len(sys.argv[1:]) > 2:
    print "More than 1 args found, please give only one arg."
    parser.print_help()
    sys.exit(1)

inifile = "env.ini"
cfg = Config.Config(inifile)
if args.img_path:
    cfg.set_imgpath(args.img_path)

if args.baseimg:
    cfg.set_baseimg(args.baseimg)

if args.basexml:
    cfg.set_basexml(args.basexml)

if args.basemac:
    cfg.set_basemac(args.basemac)

if args.run:
    vm = Ctrvm.ctrVm(args.run)
    vm.MeCk()
    vm.simg.CrSn()
    vm.defvm()
    vm.startvm()

if args.new_info:
    try:
        pcom = re.compile(r"^(\w+)\s(\w+)\s(([0-9]{0,3}\.){0,3}[0-9])$")
        pobj = pcom.search(args.new_info)
        user_name = pobj.group(1)
        team_name = pobj.group(2)
        user_ip = pobj.group(3)
    except AttributeError:
    	print "Wrong fommat found"
        parser.print_help()
        sys.exit(1)
    cfg.add_users(user_name, team_name, user_ip)

if args.list_info:
    cfg.list_items_by_user(args.list_info)

if args.del_user:
   cfg.del_users(args.del_user)

