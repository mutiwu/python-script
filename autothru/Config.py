#!/usr/bin/env python
# coding=utf-8

import ConfigParser
import sys
import random


class Config(object):
    def __init__(self, inifile="env.ini", img_path="/home/testimages/", baseimg="SecureOS_auto_win10_base_zh_en.qcow2", basexml="win10base.xml",basemac="52:54:00:9c:02:79"):
        self.inifile = inifile
        self.img_path = img_path
        self.baseimg = baseimg
        self.basexml = basexml
        self.basemac = basemac
        self.__cfg = ConfigParser.ConfigParser()
        self.__cfg_list = self.__cfg.read(self.inifile)
        if self.__cfg_list == []:
            self.__initial()

    def __initial(self):
        self.__cfg.add_section("members")
        self.__cfg.add_section("base_img_cfg")
        self.__cfg.add_section("user_dhcp")
        self.__cfg.set("base_img_cfg", "img_path", self.img_path)
        self.__cfg.set("base_img_cfg", "baseimg", self.baseimg)
        self.__cfg.set("base_img_cfg", "basemac", self.basemac)
        self.__cfg.set("base_img_cfg", "basexml", self.basexml)
        self.__cfg.create(open(self.inifile, "w"))

    def list_users_by_team(self):
        for tu_opts in self.__cfg.items("members"):
            team, users = tu_opts
            print "%s: %s\n" % (team, users)

    def __all_users(self):
        us = ""
        for tu_opts in self.__cfg.item("members"):
            team, users = tu_opts
            us = us + "," + users
        return us
            
    def __ck_user(self, user_name):
        us_list = self.__all_users().split(",")
        return (user_name in us_list)

    def __new_mac(self):
        maclist = ["52", "54"]
        for i in range(1, 5):
            randstr = "".join(random.sample("0123456789abcdef", 2))
            maclist.append(randstr)
        randmac = ":".join(maclist)
        return randmac
        
    def add_users(self, user_name, team_name, user_ip):
        if self.__ck_user(user_name):
            print "%s exists." % user_name
            self.list_users_by_team()
            sys.exit(1)
        user_mac = self.__new_mac()
        value = user_mac + "@" + user_ip
        origin_team_users = self.__cfg.get("members", team_name)
        new_users = origin_team_users + "," + user_name
        self.__cfg.set("members", team_name, new_users)
        if self.__cfg.has_option("user_dhcp", user_name):
            self.__cfg.remove_option("user_dhcp", user_name)
        self.__cfg.set("user_dhcp", user_name, value)
        self.__cfg.write(open(self.inifile, "w"))

    def del_users(self, user_name):
        teams = self.__cfg.options("members")
        if self.__ck_user(user_name):
            self.__cfg.remove_option("user_dhcp", user_name)
            for team in teams:
                tulist = self.__cfg.get("members", team).split(",")
                if user_name in tulist:
                    tulist.remove(user_name)
                    new_user_str = ",".join(tulist)
                    self.__cfg.set("members", team, new_user_str)
            self.__cfg.write(open(self.inifile, "w")) 
            return True
        return False

    def update


