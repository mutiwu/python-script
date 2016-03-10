#!/usr/bin/env python
# coding=utf-8

import ConfigParser
import sys
import random
import re


class Config(object):
    def __init__(self, inifile="env.ini"):
        self.inifile = inifile
        self.__vaptn = re.compile(r"^(52\:54(\:[0-9a-fA-F]{2}){4}) (([0-9]{0,3}\.){0,3}[0-9])$")
        self.__cfg = ConfigParser.ConfigParser()
        self.__cfg_list = self.__cfg.read(self.inifile)
        if self.__cfg_list == []:
            self.__initial()

    def __initial(self):
        self.__cfg.add_section("members")
        self.__cfg.add_section("base_img_cfg")
        self.__cfg.add_section("user_dhcp")
        for i in ["img_path", "baseimg", "basexml", "basemac"]:
            self.__cfg.set("base_img_cfg", i)
        self.__cfg.write(open(self.inifile, "w"))

    def __add_val(self, option, value):
        def set():
            self.__cfg.set("base_img_cfg", option, value)

        def quit():
            sys.exit(1)
        c_val = self.__cfg.get("base_img_cfg", option)
        if c_val:
            try:
                warn = "The %s already has value %s, are you sure to overwrite?(yes/no)" % (option, c_val)
                select = {
                    "yes": set,
                    "no": quit
                }
                select[raw_input(warn)]()
            except KeyError:
                print "Invalid choice, please retry and only accept yes or no."
                sys.exit(2)
        set()
    
    def set_imgpath(self, value):
        self.__add_val("img_path", value)

    def set_baseimg(self, value):
        self.__add_val("baseimg", value)

    def set_basemac(self, value):
        self.__add_val("basemac", value)
        
    def set_basexml(self, value):
        self.__add_val("basexml", value)

    def __optlist_ofvar(self, section, val):
        opt_list = []
        for opt_value in self.__cfg.items(section):
            opt, values = opt_value
            valist = values.split(",")
            if val in valist:
                opt_list.append(opt)
        return opt_list

    def list_items_by_user(self, user_name):
        if self.__ck_values("members", user_name) == 0:
            print "No user named %s found." % user_name
            sys.exit(0)
        teamlist = self.__optlist_ofvar("members", user_name)
        mac_ip = self.__cfg.get("user_dhcp", user_name)
        print "%s is in %s, and the corresponding mac/ip is %s." % (user_name, " ".join(teamlist), mac_ip.replace(" ", "/"))

    def __all_values(self, section):
        us = ""
        for tu_opts in self.__cfg.items(section):
            opt, val = tu_opts
            us = val + "," + us
        return us.split(",")
            
    def __ck_values(self, section, val):
        return self.__all_values(section).count(val)

    def __new_mac(self):
        maclist = ["52", "54"]
        for i in range(1, 5):
            randstr = "".join(random.sample("0123456789abcdef", 2))
            maclist.append(randstr)
        randmac = ":".join(maclist)
        return randmac
        
    def add_users(self, user_name, team_name, user_ip):
        if self.__ck_values("members",user_name) == 1:
            print "%s exists." % user_name
            sys.exit(1)
        elif self.__ck_values("members", user_name) > 1:
            print "More than 1 user named %s, please remove invalid ones." %user_name
            sys.exit(2)
        if self.__cfg.has_option("members", team_name) is False:
            self.__cfg.set("members", team_name, "")
        origin_team_users = self.__cfg.get("members", team_name)
        new_users = user_name + "," + origin_team_users
        user_mac = self.__new_mac()
        all_mac_ip_list = self.__all_values("user_dhcp")
        ip_list = []
        for mac_ip in all_mac_ip_list:
            try:
                ipobj = self.__vaptn.search(mac_ip)
                ip_list.append(ipobj.groups()[2])
            except AttributeError:
                continue
        if ip_list.count(user_ip) == 1:
            print "The IP address %s already exists." % user_ip
            sys.exit(1)
        elif ip_list.count(user_ip) > 1:
            print "The IP address %s is assigned to more than 1 user, please remove invalid user." % user_ip
        value = user_mac + " " + user_ip
        self.__cfg.set("members", team_name, new_users)
        if self.__cfg.has_option("user_dhcp", user_name):
            self.__cfg.remove_option("user_dhcp", user_name)
        self.__cfg.set("user_dhcp", user_name, value)
        self.__cfg.write(open(self.inifile, "w"))

    def del_users(self, user_name):
        teams = self.__cfg.options("members")
        if self.__ck_values("members", user_name) > 0:
            self.__cfg.remove_option("user_dhcp", user_name)
            for team in teams:
                tulist = self.__cfg.get("members", team).split(",")
                if user_name in tulist:
                    tulist.remove(user_name)
                    new_user_str = ",".join(tulist)
                    self.__cfg.set("members", team, new_user_str)
            self.__cfg.write(open(self.inifile, "w")) 
            print "%s removed, also corresponding infos." %user_name
        else:
            print "No %s found, do nothing" % user_name  

    def update_dns(self, user_name):
        dnsfile = "dnsmasq.conf"
        cfgdns = ConfigParser.ConfigParser()
        mac_ip = self.__cfg.get("user_dhcp", user_name)
        try:
            ipobj = self.__vaptn.search(mac_ip)
        except AttributeError:
            print "No invalid mac/ip found for %s. " % user_name
        user_mac = ipobj.groups()[0]
        user_ip = ipobj.groups()[2]
        hostname = user_name
        dhcphost = user_mac + "," + user_ip + "," + hostname
        cfgdns.add_section("dhcp-host")
        cfgdns.set("dhcp-host", "dhcp-host", dhcphost)
        cfgdns.write(open(dnsfile, "a"))



        


