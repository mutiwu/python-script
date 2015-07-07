import re
import urllib
import urllib2
import os
import sys
import commands
import time

class Package(object):
    def __init__(self, p_name, build):
        self.p_name = p_name
        self.build = build
        self.p_dict = {
                "qemu-kvm-rhev":"35491",
                "qemu-kvm":"18283",
                "kernel":"1231",
                }
        self.b_dict = {
                "rhel7":r"buildID=(\d+).*?el7",
                "rhel6":r"buildID=(\d+).*?el6",
                }
        self.baseurl = "https://brewweb.devel.redhat.com/"
        self.packageinfo = "packageinfo?packageID="
        self.buildinfo = "buildinfo?buildID="

    def rpm_list(self):
        self.kernel_list = [
                "kernel",
                "kernel-debuginfo",
                "kernel-debuginfo-common",
                ]
        self.qemu_rhev_list = [
                "libcacard-devel-rhev",
                "libcacard-rhev",
                "libcacard-tools-rhev",
                "qemu-img-rhev",
                "qemu-kvm-common-rhev",
                "qemu-kvm-rhev",
                "qemu-kvm-tools-rhev",
                "qemu-kvm-rhev-debuginfo",
                ]
        self.qemu_list = [
                ""
                ]
        self.rpm_dict = {
                "kernel":self.kernel_list,
                "qemu-kvm-rhev":self.qemu_rhev_list,
                "qemu-kvm":self.qemu_list,
                }
        if self.p_name not in self.rpm_dict.keys():
            print "Only support qemu-kvm, qemu-kvm-rhev and kernel"
            sys.exit(1)
        return self.rpm_dict[self.p_name]

    def buildhtml(self):
        if self.p_name not in self.p_dict.keys():
            print "Only support qemu-kvm, qemu-kvm-rhev and kernel."
            sys.exit(1) 
        self.p_id = self.p_dict[self.p_name]
        self.packageurl = self.baseurl + self.packageinfo + self.p_id
        self.p_open = urllib2.urlopen(self.packageurl)
        self.p_html = self.p_open.read()
#        print self.p_html
        if self.build not in self.b_dict.keys():
            print "Only support rhel6, rhel7"
            sys.exit(1)
        self.p_build = self.b_dict[self.build]
#        print self.p_build
        self.buildid = re.search(self.p_build, self.p_html).groups()[0]   
        self.buildurl = self.baseurl + self.buildinfo + self.buildid
#        print self.buildurl
        self.b_open = urllib2.urlopen(self.buildurl)
        return self.b_open.read()
    
    def wget_rpms(self):
        for self.rpm in self.rpm_list():
            commands.getoutput("wget ")


    
if __name__ == "__main__":
    package = Package(sys.argv[1], sys.argv[2])
    print package.buildhtml()
