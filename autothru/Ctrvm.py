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
        self.user_mac = "user_mac"
        self.img_path = self.__optvalue(self.base_img_cfg, "img_path")
        self.baseimg = self.__optvalue(self.base_img_cfg, "baseimg")
        self.simg = Defimg.Snapshot(self.user_name,
                                    self.img_path, self.baseimg)
        self.sn_name = self.simg.sn_name

    def __optvalue(self, sect, opts):
        optvalue = self.cfg.get(sect, opts)
        if self.schar in optvalue:
            optvalue = optvalue.split(self.schar)
        return optvalue

    def MeCk(self):
        teams = self.cfg.options("members")
        count = 0
        uteam = []
        for team in teams:
            teammembers = self.__optvalue("members", team)
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

    def __newmac(self):
        users = self.cfg.options(self.user_mac)
        if self.user_name in users:
            usermac = self.__optvalue(self.user_mac, self.user_name)
            return usermac

    def defvm(self):
        basexml = self.__optvalue(self.base_img_cfg, "basexml")
        basemac = self.__optvalue(self.base_img_cfg, "basemac")
        newmac = self.__newmac
        if newmac == "":
            print "No mac address belongs to %s" % self.user_name
        xml = Defxml.Defxml(basexml, self.sn_name)
        xml.modifyDomainName()
        xml.modifyUuid()
        xml.changeImage(self.img_path, self.baseimg)
        xml.changeMac(basemac, newmac)
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
