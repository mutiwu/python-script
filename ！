import os
import commands
import random
import socket
import argparse
import sys

class NewVM(object):
    def __init__(self, vm_name, vm_srcimg, g_vnc):
        self.vm_img = "/home/%s.qcow2" %vm_name
        self.vm_srcimg = vm_srcimg
        self.vm_vnc = g_vnc
        self.vm_cmd = "/usr/libexec/qemu-kvm"
        self.vm_bsarg = "-machine pseries-rhel7.2.0,accel=kvm,usb=off -m 16G -realtime mlock=off -smp 8,sockets=1,cores=8,threads=1 -no-user-config -nodefaults -rtc base=utc -boot menu=on -device spapr-vscsi,id=scsi0,reg=0x2000 -usb -device usb-kbd,id=input0 -device usb-mouse,id=input1 -vga std -monitor stdio -device scsi-cd,bus=scsi0.0,channel=0,scsi-id=0,lun=0,drive=drive-scsi0-0-0-0,id=scsi0-0-0-0,bootindex=2 -drive file=/root/iso/Asianux-DVD-ppc64le-7SP2-20160330.iso,if=none,id=drive-scsi0-0-0-0,readonly=on,format=raw -device virtio-blk-pci,scsi=off,bus=pci.0,addr=0x2,drive=drive-virtio-disk0,id=virtio-disk0,bootindex=1 -netdev tap,id=netdev,script=/etc/qemu-ifup "
        self.vnarg = "-name %s" %vm_name

    def new_mac(self):
        maclist = ['52', '54']
        for i in range(1, 5):
            randstr = ''.join(random.sample("0123456789abcdef", 2))
            maclist.append(randstr)
        randmac = ':'.join(maclist)
        return randmac

    def chk_img(self):
        if os.path.exists(self.vm_img):
            print "%s exist, will use this image as vm bootdisk." %self.vm_img
            return 0 
        while self.vm_srcimg == None:
            self.vm_srcimg = raw_input("You need specify the Base IMG:")
            if os.path.exists(self.vm_srcimg):
                break
            print "Please specify an existing img. please try again.\n"
            self.vm_srcimg = None
        cp_choice = ""
        while cp_choice != "N" or cp_choice != "Y":
            cp_choice = raw_input('%s  does not exist, need make a copy from RF_base?(Y/N)' %self.vm_img)
            if cp_choice == "N":
                print "%s will not be created, exit." %self.vm_img
                os.sys.exit(0)
            elif cp_choice == "Y":
                cmd = "cp %s %s" %(self.vm_srcimg, self.vm_img)
                status, output = commands.getstatusoutput(cmd)
                if status:
                    print "CMD cp failed\n"
                    print output
                    os.sys.exit(1)
                return 0
            else:
                print "invalid input.\n"

    def gen_vncp(self):
        new_p = random.randint(1, 59000)
        print new_p
        str_res = self.__chk_vncp(new_p)
        if str_res == "Used by other script" or str_res == "Used in system":
            self.gen_vncp()
        if str_res == "OK":
            return new_p

    def vnc_port(self, vnc_p):
        if vnc_p != None:
            f_re = self.__chk_vncp(vnc_p)
            if f_re == "OK":
                return vnc_p
            else:
                print f_re
                new_p =raw_input("input a new port, or left to randomly specify.")
                try:
                    int_p = int(new_p)
                    self.vnc_port(int_p)
                except ValueError:
                    self.vnc_port(new_p)
        return self.gen_vncp()


    def __chk_vncp(self, vnc_p):
        if type(vnc_p) != int:
            return "Invalid type, need an int"
        cmd = "find /home/ -type f -name *.sh -exec grep 'vnc :%s' {} \;" %vnc_p
        status, output = commands.getstatusoutput(cmd)
        if status:
            print output
            os.sys.exit(1)
        if output:
            return "Used by other script"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rt_value = s.connect_ex(('127.0.0.1', vnc_p))
        if rt_value == 0 :
            return "Used in system"
        return "OK"

    def vm_cmd(self):
        self.chk_img()
        mac_addr = self.new_mac()
        new_port = self.vnc_port(self.vm_vnc)
        imgarg = "-drive file=/home/%s,if=none,id=drive-virtio-disk0,format=qcow2,cache=none"
        vncarg = "-vnc :%s" %new_port
        vnicarg = "-device virtio-net-pci,netdev=netdev,id=net1,mac=%s,bus=pci.0,addr=0x5" %mac_addr
        vm_cli = self.vm_cmd + self.vm_bsarg + vnicarg + vncarg + imgarg 
        return vm_cli


parser = argparse.ArgumentParser()
parser.add_argument("-i",
                    action="store",
                    dest="vm_name",
                    metavar="VM NAME",
                    help="The vm name and the dst img name."
                   )

parser.add_argument("-s",
                    action="store",
                    dest="srcimg",
                    metavar="BASE IMG",
                    help="specify the base img."
                   )
parser.add_argument("-p",
                    action="store",
                    dest="vnc_p",
                    type="int",
                    metavar="TCP PORT",
                    help="If not assign a port, will assign random." 
                   )
args = parser.parse_args(sys.argv[1:])
if  args.vm_name == None:
    print parser.print_help()
    os.sys.exit(1)
vm_name = args.vm_name
vm_srcimg  = args.srcimg
g_vnc = args.vnc_p
new_vm = NewVM(vm_name, vm_srcimg, g_vnc)
print new_vm.new_mac()
print new_vm.vm_cmd
print new_vm.vm_bsarg
print new_vm.vnarg
new_vm.chk_img()
print new_vm.vnc_port(g_vnc)
