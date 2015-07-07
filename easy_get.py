import re
import urllib2
import os
import sys
import commands
import getopt

class Package(object):
    def __init__(self, p_name="qemu-kvm-rhev", build="rhel7", direc="/opt/"):
        self.p_name = p_name
        self.build = build
        self.direc = direc
        self.__p_dict = {
                "qemu-kvm-rhev":"35491",
                "qemu-kvm":"18283",
                "kernel":"1231",
                }
        self.__b_dict = {
                "rhel7":r"buildID=(\d+).*?el7",
                "rhel6":r"buildID=(\d+).*?el6",
                }
        self.__kernel_list = [
                "kernel",
                "kernel-debuginfo",
                "kernel-debuginfo-common",
                ]
        self.__qemu_rhev_list = [
                "qemu-img-rhev",
                "libcacard-devel-rhev",
                "libcacard-rhev",
                "libcacard-tools-rhev",
                "qemu-kvm-common-rhev",
                "qemu-kvm-rhev",
                "qemu-kvm-tools-rhev",
                "qemu-kvm-rhev-debuginfo",
                ]
        self.__qemu_list = [
                ""
                ]
        self.__rpm_dict = {
                "kernel":self.__kernel_list,
                "qemu-kvm-rhev":self.__qemu_rhev_list,
                "qemu-kvm":self.__qemu_list,
                }
        self.__pattern_rpm = r"href=\"(.*?%s.*?)\.x86_64\.rpm"
        self.__baseurl = "https://brewweb.devel.redhat.com/"
        self.__packageinfo = "packageinfo?packageID="
        self.__buildinfo = "buildinfo?buildID="
        self.__errormsg = "Only support qemu-kvm, qemu-kvm-rhev and kernel"
                
    def __rpm_list(self):
        if self.p_name not in self.__rpm_dict.keys():
            print self.__errormsg
            sys.exit(1)
        return self.__rpm_dict[self.p_name]

    def __buildhtml(self):
        if self.p_name not in self.__p_dict.keys():
            print self.__errormsg
            sys.exit(1) 
        self.p_id = self.__p_dict[self.p_name]
        self.packageurl = self.__baseurl + self.__packageinfo + self.p_id
        self.p_open = urllib2.urlopen(self.packageurl)
        self.p_html = self.p_open.read()
#        print self.p_html
        if self.build not in self.__b_dict.keys():
            print "Only support rhel6, rhel7"
            sys.exit(1)
        self.p_build = self.__b_dict[self.build]
#        print self.p_build
        self.buildid = re.search(self.p_build, self.p_html).groups()[0]   
        self.buildurl = self.__baseurl + self.__buildinfo + self.buildid
#        print self.buildurl
        self.b_open = urllib2.urlopen(self.buildurl)
        return self.b_open.read(), self.buildid
    
    def wget_rpms(self):
        self.r_list = self.__rpm_list()
        self.direcname = self.r_list[0]
        self.b_html, self.buildid = self.__buildhtml()
        self.path = self.direc
        self.path += "%s%s" % (self.direcname, self.buildid)
        if os.path.exists(self.path):
            print "The directory exists, please choose another directory."
            sys.exit(3)
        os.mkdir(self.path)
        os.chdir(self.path)
        for self.rpm in self.r_list:
            self.p_rpm = re.compile(self.__pattern_rpm %self.rpm)
            self.rpm_url = self.p_rpm.findall(self.b_html)[0]
            if not commands.getstatusoutput("wget %s" % self.rpm_url)[0]:
                print "wget hit error, need check"
                sys.exit(2)
            print "%s is downloaded" % self.rpm
        return self.path
    
    def install_rpms(self):
        self.path = self.wget_rpms()
        os.chdir(self.path)
        self.cmd = {
                "qemu-kvm-rhev":"yum install * -y",
                "qemu-kvm":"yum install * -y",
                "kernel":"rpm -ivh *",
                }
        if self.p_name not in self.cmd.keys():
            print self.__errormsg
        if not commands.getstatusoutput(self.cmd[self.p_name])[0]:
            print "Install hit error, need check"
            sys.exit(4)
        print "the packages in %s is installed well" % self.p_name
            
            
if __name__ == "__main__":
    def usage():
        return """
        python easy_get.py -p $package -b $build -d $dir.
        default value:
        -p qemu-kvm-rhev -b rhel7 -d /opt/ --download.
        -h\t--help\tprint the usage.
        -p\t--package\tthe package name, support ones:qemu-kvm-rhev, qemu-kvm, kernel.
        -b\t--build\tthe build, support ones:rhel6, rhel7.
        -d\t--directory\tthe directory that you want to wget the packages, default is /opt/.
        \n\n
        --install\tdownload and install the corresponding packages.
        """
        
    try:
        options, args = getopt.getopt(sys.argv[1:], "h:p:b:d:", 
                                      [
                                      'help',
                                      'package',
                                      'build',
                                      'directory',
                                      'install',
                                      ])
    except getopt.GetoptError:
        usage()
        sys.exit(1)
    for name, value in options:
        if name in ("-h", "--help"):
            usage()
        if name in ("-p", "--package"):
            p_name = value
        else:
            p_name = "qemu-kvm-rhev"
        if name in ("-b", "--build"):
            build = value
        else:
            build = "rhel7"
        if name in ("-d", "--directory"):
            direc = value
        else:
            direc = "/opt/"
    
    f = Package(p_name, build, direc)
    if ('--install', '') in options: 
       f.install_rpms()           
       sys.exit(0)
    f.wget_rpms()

            
            
    
