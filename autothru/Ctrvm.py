#!/usr/bin/env python
# coding=utf-8
import sys
import commands
import Defimg
import Defxml
import ConfigParser


class ctrVm(object):
    def __init__(self, user_name):
        self.user_name = user_name
        self.cfg = ConfigParser.ConfigParser()
        self.cfgfile = "env.ini"
        self.cfg.read(self.cfgfile)
        self.schar = ","
        self.base_img_cfg = "base_img_cfg"
        self.img_path = self.optvalue(self.base_img_cfg, "img_path")
        self.baseimg = self.optvalue(self.base_img_cfg, "baseimg")
        self.simg = Defimg.Snapshot(self.user_name,
                                    self.img_path, self.baseimg)
        self.sn_name = self.simg.sn_name

    def optvalue(self, sect, opts):
        optvalue = self.cfg.get(sect, opts)
        if self.schar in optvalue:
            optvalue = optvalue.split(self.schar)
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
            print "The user should be in only one team,but %s is in %s." % (self.user, ",".join(uteam))
            sys.exit(2)
        print "User %s from team %s." % (self.user_name, uteam[0])

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
