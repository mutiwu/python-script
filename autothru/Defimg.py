#!/usr/bin/env python
# coding=utf-8
import commands
import sys
import time


class Snapshot(object):
    def __init__(self, user_name, img_path, baseimg):

        self.__c_time = time.strftime('%Y-%m-%d-%H-%M-%S',
                                    time.localtime(time.time()))
        self.img_path = img_path
        self.baseimg = self.img_path + baseimg
        self.user_name = user_name
        self.sn_name = user_name + self.__c_time
        self.__qimg_cmd = "qemu-img"
        self._args = {
            "create": "create -f qcow2 -b %s %s"
            % (self.baseimg, self.sn_name),
            "check_info": "info",
        }

    def CrSn(self):
        cmd = "cd %s ;" % self.img_path
        cmd = cmd + self.__qimg_cmd + " " + self._args["create"]
        status, output = commands.getstatusoutput(cmd)
        if status:
            print output
            sys.exit(1)
        return status
        cmd = self.__qimg_cmd + " " + self._args["check_info"]
        cmd = cmd + self.sn_name
        status, output = commands.getstatusoutput(cmd)
        if status:
            print output
            sys.exit(1)
        return output
