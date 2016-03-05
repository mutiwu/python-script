#!/usr/bin/env python
# coding=utf-8
import sys
import commands
import getopt
import Defimg
import Defxml
import ConfigParser

class ctrVm(object):
    def __init__(self, user_name):
        self.user_name = user_name
        self.cfg = ConfigParser.ConfigParser()
        self.cfgfile = "env.cfg"
        self.schar = ","
        self.base_img_cfg = "base_img_cfg"
        self.img_path = self.optvalue(self.base_img_cfg, "img_path")
        self.baseimg = self.optvalue(self.base_img_cfg, "baseimg")
        self.simg = Defimg.Snapshot(self.user_name, self.img_path, self.baseimg)
        self.sn_name = self.simg.sn_name

    def optvalue(self, sect, opts):
        optvalue = self.cfg.get(sect, opt)
        if self.schar in optvalue:
            optvalue = optvalue.split{self.schar}
        return optvalue

    def MeCk(self):
        teams = self.cfg.options("members")
        count = 0
        uteam = []
        for team in teams:
            teammembers = self.optvalue("members", team)
            if self.user_name in teammembers:
                uteam.append(team)
	            count = +1
	    if count == 0:
            print "Invalid user. Exit."
	        sys.exit(1)
        elif count > 1:
            print "The user should be in only one team, but %s is in %s, exit." %(self.user, ",".join(uteam))
            sys.exit(2)
        print "User %s from team %s." %(self.user_name, uteam[0])

    def defvm(self):
        basexml = self.optvalue(self.base_img_cfg, "basexml")
        basemac = self.optvalue(self.base_img_cfg, "basemac")
        xml = Defxml.Defxml(basexml, self.sn_name)
        xml.modifyDomainName()
        xml.modifyUuid()
        xml.changeImage(self.img_path, self.baseimg)
        xml.changeMac(basemac)
        cmd = "virsh define %s" % xml.newxml
        status, output = commands.getstatusoutput(cmd)
        if status:
            print output
            sys.exit(1)

    def startvm(self):
        cmd = "virsh start %s" % self.sn_name
        status, output = commands.getstatusoutput(cmd)
        if status:
            print output
            sys.exit(1)
        print output

def usage():
    pass

if __name__ == "__main__":
    shotargs = "p:b:u:"
    longargs = ['help',]
    if len(sys.argv) == 1:
        usage()
        sys.exit(0)
    try:
        options, args = getopt.getopt(sys.argv[1:], shotargs, longargs)
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)
    for key, value in options:
        if "-u" not in options.keys():
            print "please input the user name."
        if key == "--help":
            usage()
            sys.exit(0)
        elif key == "-p":
            img_path = value
        elif key == "-b":
            baseimg = value
        elif key == "-u":
            user_name = value
        else:
            assert False, "unhandled option"
            
vm = ctrVm(user_name, img_path, baseimg)
vm.MeCk()
vm.simg.CrSn()
vm.define()
vm.startvm()