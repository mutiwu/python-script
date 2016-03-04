#!/usr/bin/env python
# coding=utf-8
import commands
import time

class Snapshot(object):
    def __init__(self, user_name, img_path, baseimg):
        self.members = [
            "team",
            "zhaoq",
            "wankh",
            "zhaoss",
            "guoq",
            "hanxm",
        ]
        self.c_time = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
        self.img_path = img_path
        self.baseimg = self.img_path + baseimg
        self.user_name = user_name
        self.sn_name = user_name + self.c_time
        self.qimg_cmd = "qemu-img"
        self.args = {
            "create": "create -f qcow2 -b %s %s" % (self.baseimg, self.sn_name),
            "check_info": "info",
        }
        self.alloutput = {
            "crsn": "",
            "info": "",
        }


    def CrSn(self):
        self.cmd = "cd %s \;" % self.img_path
        self.cmd = self.cmd + self.qimg_cmd + self.args["create"]
        self.status, self.output = commands.getstatusoutput(self.cmd)
        if self.status:
            self.alloutput["crsn"] = self.output
            return self.status
        return self.status

    def Ckinfo(self):
        self.cmd = self.qimg_cmd + self.args["check_info"]
        self.cmd = self.cmd + self.sn_name
        self.status, self.output = commands.getstatusoutput(self.cmd)
        if self.status:
            self.alloutput["info"] = self.output
            return self.status
        return self.status

