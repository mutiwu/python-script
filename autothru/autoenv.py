#!/usr/bin/env python
# coding=utf-8
import sys
import commands
import getopt
import Defimg
import Defxml

def usage():
    pass

if __name__ == "__main__":
    img_path = "/home/testimages"
    baseimg = "SecureOS_auto_win10_base_zh_en.qcow2"
    user_name = "team"
    try:
        options, args = getopt.getopt(sys.argv[1:], "p:b:u:",
                                      [
                                          'help',
                                      ]
                                     )
    except getopt.GetoptError:
        print usage()
        sys.exit(0)
    for key, value in options:
        if key == "--help":
            print usage()
            sys.exit(0)
        if key == "-p":
            img_path = value
        if key == "-b":
            baseimg = value
        if key == "-u":
            user_name = value
            
if len(sys.argv) == 1:
    print usage()
    sys.exit(0)
test = Defimg.Snapshot(user_name=user_name, img_path=img_path, baseimg=baseimg, )
sn_name = test.sn_name
print 
if test.MeCk():
    print "%s is not in the member list, try the user in %s" %(user_name , " ".join(test.members)) 
    sys.exit(1)
if test.CrSn():
    print "Create Snapshot image failed, and the cmd prints %s" %test.alloutput["CrSn"]
    sys.exit(1)
#if test.Ckinfo():
#    print "check info failed, cmd print %s" %test.alloutput["info"]
#    sys.exit(1)

xml = Defxml.Defxml("win10base.xml", sn_name)
xml.modifyDomainName()
xml.modifyUuid()
xml.changeImage(img_path=img_path, baseimg=baseimg)
xml.changeMac("52:54:00:9c:02:79")
cmd = "virsh define %s" %xml.newxml
status, output = commands.getstatusoutput(cmd)
if status:
    print "define vm failed, the virsh print %s" % output
    sys.exit(1)
cmd = "virsh start %s" %sn_name
status, output = commands.getstatusoutput(cmd)
if status:
    print "start vm failed, the virsh print %s" % output
    sys.exit(1)
cmd = "virsh list --all"
status, output = commands.getstatusoutput(cmd)
print output