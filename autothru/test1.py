#!/usr/bin/env python
# coding=utf-8

import ConfigParser
import exceptions


cfg = ConfigParser.ConfigParser()
cfg.read("env.ini")

def mac(user):

    users = cfg.options("user_mac")
    if user in users:
        mac = cfg.get("user_mac", user)
        return mac

print mac("guoqian")
print mac("test")

