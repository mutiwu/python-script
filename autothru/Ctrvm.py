#!/usr/bin/env python
# coding=utf-8
import sys
import commands
import Defimg
import Defxml
import ConfigParser
import Config
import re


class ctrVm(object):
    def __init__(self, user_name):
        self.user_name = user_name
        self.__cfg = ConfigParser.ConfigParser()
        inicfg = Config.Config()
        self.__cfgfile = inicfg.inifile
        self.__cfg.read(self.__cfgfile)
        self.__schar = ","
        self.__base_img_cfg = "base_img_cfg"
        self.__user_dhcp = "user_dhcp"
        self.img_path = self.__optvalue(self.base_img_cfg, "img_path")
        self.baseimg = self.__optvalue(self.base_img_cfg, "baseimg")
        self.simg = Defimg.Snapshot(self.user_name,
                                    self.img_path, self.baseimg)
        self.sn_name = self.simg.sn_name

    def __optvalue(self, sect, opts):
        optvalue = self.__cfg.get(sect, opts)
        if self.__schar in optvalue:
            optvalue = optvalue.split(self.__schar)
        return optvalue

    def MeCk(self):
        teams = self.__cfg.options("members")
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

    def defvm(self):
        basexml = self.__optvalue(self.base_img_cfg, "basexml")
        basemac = self.__optvalue(self.base_img_cfg, "basemac")
        usermacip = self.__cfg.get(self.user_dhcp, self.user_name)
        if usermacip == "":
            print "No mac item belongs to %s." % self.user_name
            sys.exit(1)
        newmac = usermacip.split(" ")[0] 
        xml = Defxml.Defxml(basexml, self.sn_name)
        cmd = '''grep %s %s\*\.xml''' %(newmac, xml.xmlpath)
        status, output = commands.getstatusoutput(cmd)
        if status:
            print output
            sys.exit(1)
        if output:
            pobj = re.compile(r"^%s(.*?\.xml)\:" % xml.xmlpath)
            result_ptn = pobj.search(output)
            print "The mac %s is used by %s" % (newmac, result_ptn.groups()[0])
            sys.exit(1)
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

    def listvm(self):
        cmd = "virsh list %s" % self.sn_name
        status, output = commands.getstatusoutput(cmd)
        if status:
            print output
            sys.exit(1)
        print output
