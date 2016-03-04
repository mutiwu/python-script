#!/usr/bin/env python
# coding=utf-8
import sys
import commands
import getopt
import Defimg
import Defxml

class ctrVm(object):
    def __init__(self, user_name, img_path, baseimg):
	self.user_name = user_name
	self.img_path = img_path
	self.baseimg = baseimg
	self.simg = Defimg.Snapshot(self.user_name, img_path, baseimg)
	self.sn_name = self.simg.sn_name

    def MeCk(self):
	if self.user_name in self.simg.members:
	    return 0
	return 1

    def defvm(self, basexml, basemac):
        self.xml = Defxml.Defxml(basexml, self.sn_name)
        self.xml.modifyDomainName()
        self.xml.modifyUuid()
        self.xml.changeImage(self.img_path, self.baseimg)
        self.xml.changeMac(basemac)
        self.cmd = "virsh define %s" % self.xml.newxml
        self.status, self.output = commands.getstatusoutput(self.cmd)
        if self.status:
            print "define vm failed, the virsh print %s" % self.output
            sys.exit(1)

    def startvm(self):
        cmd = "virsh start %s" % self.sn_name
        self.status, self.output = commands.getstatusoutput(cmd)
        if self.status:
            print "start vm failed, the virsh print %s" % self.output
            sys.exit(1)
        print self.output

    def main(self):



def usage():
    pass

if __name__ == "__main__":
    user_name = "team"
    img_path = "/home/testimages"
    baseimg = "SecureOS_auto_win10_base_zh_en.qcow2"
    basemac = "52:54:00:9c:02:79"
    basexml = "win10base.xml"
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

vm = ctrVm(user_name, img_path, baseimg)


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




