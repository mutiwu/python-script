import os
import commands
import random
import socket
import argparse
import sys

class NewVM(object):
    def __init__(self, vm_name, switch, g_vnc):
        self.vm_name = vm_name
        self.vm_vnc = g_vnc
        self.switch = switch
        self.breakline = "*"

    def mtarg(self):
        chk_plat = "uname -i"
        status, output = commands.getstatusoutput(chk_plat)
        if status:
            print output
            print "Can not check the platform.\nquit"
            os.sys.exit(status)
        if output == "ppc64le" or output == "ppcle64":
            return " -machine pserise-rhel7.2.0,accel=kvm,usb=off -device spapr-vscsi,id=scsi0,reg=0x2000 "
        elif output == "x86_64":
            return " -machine pc-i440fx-rhel7.0.0,accel=kvm,usb=off -cpu host -device virtio-scsi-pci,id=scsi0,bus=pci.0,addr=0x9 "
        else:
            print "get wrong type %s, quit.\n" %output
            os.sys.exit(1)
    def new_mac(self):
        maclist = ['52', '54']
        for i in range(1, 5):
            randstr = ''.join(random.sample("0123456789abcdef", 2))
            maclist.append(randstr)
        randmac = ':'.join(maclist)
        return randmac


    def img_handle(self, vm_name):
        imgpath = "/var/vmimgs"
        vmimg = "%s/%s.qcow2" %(imgpath, vm_name)
        if not os.path.exists(imgpath):
            os.mkdir(imgpath)
        cic = {
            "Y":self.chc_y,
            "N":self.chc_n,
        }
        if os.path.exists(vmimg):
            chc = raw_input("%s exist, if will use this image as vm bootdisk.(Y/N)" %vmimg)
            newimg = self.chc_c(cic, chc, vmimg)
            return newimg, vm_name
        else:
            print "%s does not exist, please choose:\n" %vmimg
            newimg = self.chmenu(vmimg)
            return newimg, vm_name

    def chc_c(self, cic, chc,vmimg):
        try:
            cic[chc](vmimg)
            return vmimg 
        except KeyError:
            print "invalid input, quit.\n"
            os.sys.exit(1)
    def chmenu(self,vmimg):
        chc = raw_input('''
        1:  Copy from an exist IMG
        2:  create and install a new OS
        q:  quit
                        \n''') 
        cic = {
            "1":self.img_cp,
            "2":self.cre_img,
            "q":self.quit,
        }
        return self.chc_c(cic,chc,vmimg)

    def chc_y(self,vmimg):
        cmd = "ps aux |grep %s" %vmimg
        status, output = commands.getstatusoutput(cmd)
        if status:
            print output
            os.sys.exit(1)
        if "file=%s" %vmimg in output:
            print "The image %s is used by another activate guest, please check" %vmimg
            os.sys.exit(3)

    def chc_n(self,vmimg):
        print "Won't use the %s as the bootdisk, so " % vmimg
        vm_name = raw_input("please specify a new vm name:\n")
        return self.img_handle(vm_name)

    def img_cp(self,vmimg):   
        srcimg = raw_input("Please specify the base image:\n")
        if srcimg == "quit":
            os.sys.exit(0)
        if not os.path.exists(srcimg):
            print "%s does not exist. back to menu:\n" %srcimg
            return self.chmenu(vmimg)
        else:
            cmd = "cp %s %s" %(srcimg, vmimg)
            status, output = commands.getstatusoutput(cmd)
            if status:
                print "CMD cp failed\n"
                print output
                os.sys.exit(status)

    def cre_img(self,vmimg):
        imgsize = raw_input("Please input the size you want to use, e.g 50G, 100M, ...\n")
        cmd = "qemu-img create -f qcow2 %s %s" %(vmimg, imgsize)
        status, output = commands.getstatusoutput(cmd)
        if status:
            print output
            os.sys.exit(status)
        print "Creating the img..."
        print self.breakline
        print output
        print self.breakline
    def quit(self,vmimg):
        print "Do nothing with %s, just quit.\n" %vmimg
        os.sys.exit(0)

    def gen_vncp(self):
        new_p = random.randint(5900, 65535)
        res = self.__chk_vncp(new_p)
        if res == 303:
            print self.breakline
            print "The new vnc port is %s" %new_p
            print self.breakline
            return new_p
        elif res == 301:
            return self.gen_vncp()
        else:
            print "Generae vnc port faild.\n"
            print "Invalid code#%s, exit.\n" %res
            os.sys.exit(res)

    def vnc_port(self, vnc_p):
        if vnc_p is None:
            return self.gen_vncp()
        f_re = self.__chk_vncp(vnc_p)
        if f_re == 303:
          #  import pdb
          #  pdb.set_trace()
            return vnc_p
        elif f_re == 301:
            return self.input_p()
        else:
            print "Invalid code#%s, exit.\n" %f_re
            os.sys.exit(f_re)

    
    def input_p(self):
        new_p = raw_input("input a new port, or left to randomly specify:\n")
        try:
            int_p = int(new_p)
            return self.vnc_port(int_p)
        except ValueError:
            return self.vnc_port(new_p)


    def __chk_vncp(self, vnc_p):
        if type(vnc_p) != int:
            print "Invalid type, need an int"
            return 301
            
#        cmd = "find /home/ -type f -name *.sh -exec grep 'vnc :%s' {} \;" %vnc_p
#            print "the vnc_p is %s"%vnc_p
#        status, output = commands.getstatusoutput(cmd)
#        if status:
#            print output
#            os.sys.exit(1)
#        if output:
#            return "Used by other script"
        if vnc_p < 5900:
            print "The vnc port must be 5900 ~ 65535"
            return 301
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            rt_value = s.connect_ex(('127.0.0.1', vnc_p))
            if rt_value == 0 :
                print "Used in system"
                return 301
            return 303
        except OverflowError:
            print "The vnc port must be 0-65535"
            return 301
    def create_switch(self, switch):
        ifsrppath = "/etc/qemu-%s-ifup" %switch
        ifscript = '''#!/bin/sh\nswitch=%s\nip link set $1 up\nbrctl addif ${switch} $1\n''' %switch
        if not os.path.exists(ifsrppath):
            iswrite = open(ifsrppath, 'w')
            iswrite.write(ifscript)
            iswrite.close()
            os.system("chmod +x %s" %ifsrppath)
        cmd = "ip link show  %s" %switch
        status, output = commands.getstatusoutput(cmd)
        if status:
            print output
            print "Creaing %s" %switch
            cmd = "brctl addbr %s" %switch
            status, output = commands.getstatusoutput(cmd)
            if status:
                print output
                print "brctl hit error, quit"
                os.sys.exit(status)
        cmd = "ip link set %s up" %switch
        status, output = commands.getstatusoutput(cmd)
        if status:
            print output
            print "setup %s failed" %switch
            os.sys.exit(status)
        return ifsrppath

    def VM_srp(self):
        vm_img, vm_name = self.img_handle(self.vm_name)
        cmdpath =  "/var/vmcli"
        gcmdpath = "%s/%s.sh" %(cmdpath, vm_name)
        if not os.path.exists(cmdpath):
            os.mkdir(cmdpath)
        if os.path.exists(gcmdpath):
            return 1, gcmdpath 
        vnarg = " -name %s" %vm_name
        mac_addr = self.new_mac()
        vport = self.vnc_port(self.vm_vnc)
        mtearg = self.mtarg()
        ifscript = self.create_switch(self.switch)

        vm_qemu = "/usr/libexec/qemu-kvm "
        vm_bsarg = " -m 16G -realtime mlock=off -smp 8,sockets=1,cores=8,threads=1 -no-user-config -nodefaults -rtc base=utc -boot menu=on -usb -device usb-kbd,id=input0 -device usb-mouse,id=input1 -vga std  -device scsi-cd,bus=scsi0.0,channel=0,scsi-id=0,lun=0,drive=drive-scsi0-0-0-0,id=scsi0-0-0-0,bootindex=2  -device virtio-blk-pci,scsi=off,bus=pci.0,addr=0x6,drive=drive-virtio-disk0,id=virtio-disk0,bootindex=1  -boot menu=on -drive if=none,id=drive-scsi0-0-0-0,readonly=on,format=raw  "
        imgarg = " -drive file=%s,if=none,id=drive-virtio-disk0,format=qcow2,cache=none" % vm_img
        vncarg = " -vnc :%s" % vport
        taparg = " -netdev tap,id=netdev,script=%s,vhost=on" %ifscript
        vnicarg = " -device virtio-net-pci,netdev=netdev,id=net1,mac=%s,bus=pci.0,addr=0x5" %mac_addr
        qmparg = " -qmp unix:/tmp/%sqmpsocket.sock,server,nowait" %vm_name
        hmparg = " -monitor unix:/tmp/%shmpsocket.sock,server,nowait" %vm_name
        vm_clilist = [
            vm_qemu,
            mtearg,
            vnarg,
            vm_bsarg,
            qmparg,
            hmparg,
            taparg,
            vnicarg,
            vncarg,
            imgarg,
        ]
        vm_cli = ''.join(vm_clilist)
        #return vm_cli
        f_vm = open(gcmdpath, 'w')
        f_vm.write(vm_cli)
        f_vm.close()
        return 0, gcmdpath


parser = argparse.ArgumentParser()
parser.add_argument("-i",
                    action="store",
                    dest="vm_name",
                    metavar="VM NAME",
                    help="The vm name and the dst img name."
                   )

parser.add_argument("-p",
                    action="store",
                    dest="vnc_p",
                    type=int,
                    metavar="TCP PORT",
                    help="If not assign a port, will assign random." 
                   )
parser.add_argument("--run",
                    nargs = '?',
                    action="store",
                    dest="vmrun",
                    const = 'true',
                    default = 'false',
                    metavar="VM NAME",
                    help="run the specified vm"
                   )
parser.add_argument("-s",
                    action="store",
                    dest="switch",
                    default="switch",
                    metavar="LINUX BRIDGE",
                    help="specify the linux bridge you want to use."
                   )
args = parser.parse_args(sys.argv[1:])



def runvm(gcmdpath):
    shcmd = " sh %s & " %gcmdpath
    status  = os.system(shcmd)
    if status:
        print "the vm is not started, please check your cmdline.\n"
        readcmd(gcmdpath)
        os.sys.exit(status)
    os.sys.exit(0)

def readcmd(gcmdpath):
    f_vm = open(gcmdpath)
    try:
        cmdtext = f_vm.read()
        print cmdtext
    finally:
        f_vm.close()

if  args.vm_name == None:
    print "Please provide the vm name you want to use."
    parser.print_help()
    os.sys.exit(0)


vm_name = args.vm_name
g_vnc = args.vnc_p
ifrun = args.vmrun
switch = args.switch
new_vm = NewVM(vm_name, switch, g_vnc)
status, gcmdpath = new_vm.VM_srp()
if ifrun == "true":
    if status == 1:
        print "the qemu script exist, -s and -p won't work. the cmdline is  like this:\n"
        readcmd(gcmdpath)
        ch = raw_input("\n if direct run it?(Y/N)")
        if ch == "Y":
            runvm(gcmdpath)
            os.sys.exit(0)
        elif ch == "N":
            print "WARN: %s exist, you can start the script by shell, and remove it if you like.\n" %gcmdpath
            os.sys.exit(0)
        else:
            print "wrong input, just quit.\n"
            os.sys.exit(1)
    elif status == 0:
        print "The cmdline is like this:\n"
        readcmd(gcmdpath)
        runvm(gcmdpath)
        os.sys.exit(0)
    else:
        print "got wrong code#%s, quit.\n" %status
        os.sys.exit(status)
elif ifrun == "false":
    if status == 1:
        print "%s exists, and no script created, please check if the script is the one you want, you can start with --run or use shell to run it.\n" %gcmdpath
        readcmd(gcmdpath)
    elif status == 0:
        print "Your script %s is ready, you can start it next time with --run or use shell to run it.\n" %gcmdpath
        readcmd(gcmdpath)
    else:
        print "got wrong code#%s, quit.\n" %status

