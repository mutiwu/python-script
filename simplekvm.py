#!/usr/bin/env python
# coding=utf-8
'''
Created on Oct 13, 2016

@author: Qian Guo
'''

import os
import commands
import random
import socket
import argparse
import sys
import re


class NewVM(object):
    def __init__(self,
                 vm_name,
                 switch,
                 m_size,
                 c_nums,
                 imgpath,
                 cmdpath,
                 g_vnc,
                 flag,
                 vid):
        self.imgpath = imgpath
        self.cmdpath = cmdpath
        self.vm_name = vm_name
        self.m_size = m_size
        self.c_nums = c_nums
        self.vm_vnc = g_vnc
        self.switch = switch
        self.flag = flag
        self.vid = vid

    def bp(self, str):
        breakline = '>' + "." * 29
        print breakline
        print str
        print breakline

    def mtarg(self):
        chk_plat = "uname -i"
        status, output = commands.getstatusoutput(chk_plat)
        if status:
            self.bp(output)
            self.bp("Can not check the platform.\nquit")
            os.sys.exit(status)
        if output == "ppc64le" or output == "ppcle64":
            return ('-machine pseries-rhel7.2.0,accel=kvm,usb=off \\\n'
                    '-device spapr-vscsi,id=scsi0,reg=0x2000 \\\n')
        elif output == "x86_64":
            return ('-machine pc-i440fx-rhel7.0.0,accel=kvm,usb=off \\\n'
                    '-cpu host \\\n'
                    '-device virtio-scsi-pci,id=scsi0,bus=pci.0,addr=0x9 \\\n')
        else:
            self.bp("Get wrong type %s, quit.\n" % output)
            os.sys.exit(1)

    def new_mac(self):
        maclist = ['52', '54']
        for i in range(1, 5):
            randstr = ''.join(random.sample("0123456789abcdef", 2))
            maclist.append(randstr)
        randmac = ':'.join(maclist)
        return randmac

    def img_handle(self, vm_name):
        vmimg = "%s/%s.qcow2" % (self.imgpath, vm_name)
        if not os.path.exists(self.imgpath):
            os.mkdir(self.imgpath)
        if os.path.exists(vmimg):
            cic = {
                    "Y": self.chc_y,
                    "y": self.chc_y,
                    "N": self.chc_n,
                    "n": self.chc_n,
                }
            chc = raw_input("%s exist, if use this VM image.(Y/N)\n>" % vmimg)
            newimg = self.chc_c(cic, chc, vmimg)
            return newimg, vm_name
        else:
            self.bp("%s does not exist, please choose:" % vmimg)
            newimg = self.chmenu(vmimg)
            return newimg, vm_name

    def chc_c(self, cic, chc, vmimg):
        try:
            cic[chc](vmimg)
            return vmimg
        except KeyError:
            self.bp("Invalid input, quit.")
            os.sys.exit(1)

    def chmenu(self, vmimg):
        chc = raw_input(('1: Copy from an exist IMG\n'
                         '2: Create a new IMG\n'
                         'q: Quit\n>'))
        cic = {
            "1": self.img_cp,
            "2": self.cre_img,
            "q": self.quit,
        }
        return self.chc_c(cic, chc, vmimg)

    def chc_y(self, vmimg):
        cmd = (''' ps -ef |grep %s/%s.qcow2 '''
               '''|grep -v 'grep'|awk '{print $2}' '''
               % (self.imgpath, vm_name))
        status, output = commands.getstatusoutput(cmd)
        if status:
            self.bp(output)
            os.sys.exit(1)
        if output:
            self.bp(("The image %s is used by another running guest,"
                     "please check, and "
                     "the pid of the running vm is %s ") % (vmimg, output))
            os.sys.exit(3)

    def chc_n(self, vmimg):
        vm_name = raw_input(("Won't use the %s as the bootdisk,"
                             "so please specify a new vm name:\n>") % vmimg)
        return self.img_handle(vm_name)

    def img_cp(self, vmimg):
        self.bp('Please choose what images you need to copy.')
        choice = raw_input('1: Copy from current vms.\n'
                           '2: Copy from other images.\n'
                           '3: Back to the pre menu.\n>')
        if choice == '3':
            return self.chmenu(vmimg)
        if choice == '1':
            srcvm = raw_input('Please specify the src vm name.\n>')
            srcimg = '%s/%s.qcow2' % (self.imgpath, srcvm)
        elif choice == '2':
            srcimg = raw_input("Please specify the base image:\n>")
        else:
            self.bp('Invalid input, please follow the menu.')
            return self.img_cp(vmimg)
        return self.cp_chk(srcimg, vmimg)

    def cp_chk(self, srcimg, vmimg):
        if not os.path.exists(srcimg):
            self.bp("%s does not exist. back to menu:" % srcimg)
            return self.chmenu(vmimg)
        else:
            cmd = "cp %s %s" % (srcimg, vmimg)
            status, output = commands.getstatusoutput(cmd)
            if status:
                self.bp("Command cp hit error")
                self.bp(output)
                os.sys.exit(status)

    def cre_img(self, vmimg):
        imgsize = raw_input(("Please input the size you want to use,"
                             "e.g. 50G, 100M, ...\n>"))
        cmd = "qemu-img create -f qcow2 %s %s" % (vmimg, imgsize)
        status, output = commands.getstatusoutput(cmd)
        if status:
            self.bp(output)
            os.sys.exit(status)
        self.bp("Creating the img...")
        self.bp(output)

    def quit(self, vmimg):
        self.bp("Will not create %s, just quit." % vmimg)
        os.sys.exit(0)

    def gen_vncp(self):
        new_p = random.randint(5900, 65535)
        res, res1 = self.__chk_vncp(new_p)
        if res == 303:
            self.bp("The new vnc port is %s" % new_p)
            return res1
        elif res == 301:
            return self.gen_vncp()
        else:
            self.bp("Invalid ErrorCode#%s, exit." % res)
            self.bp("Generae vnc port faild.")
            os.sys.exit(res)

    def vnc_port(self, vnc_p):
        if vnc_p is None:
            return self.gen_vncp()
        f_re, res1 = self.__chk_vncp(vnc_p)
        if f_re == 303:
            return res1
        elif f_re == 301:
            return self.input_p()
        else:
            self.bp("Invalid code#%s, exit." % f_re)
            os.sys.exit(f_re)

    def input_p(self):
        new_p = raw_input("Input a new port, or left to randomly specify:\n>")
        try:
            int_p = int(new_p)
            return self.vnc_port(int_p)
        except ValueError:
            if new_p == '':
                return self.gen_vncp()
            else:
                return self.vnc_port(new_p)

    def __chk_vncp(self, old_p):
        if type(old_p) != int:
            self.bp("Invalid type, port id should be in int type.")
            return 301, 3001
        vnc_p = old_p - 5900
        if vnc_p <= 0:
            self.bp(('The vnc port must be 5900 ~ 65535'))
            return 301, 3002
        elif vnc_p >= 59635:
            self.bp(('The vnc port must be 5900 ~ 65535'))
            return 301, 3003
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                rt_value = s.connect_ex(('127.0.0.1', old_p))
                if rt_value == 0:
                    self.bp("%s is in use of this host" % old_p)
                    return 301, 3003
                return 303, vnc_p
            except OverflowError:
                self.bp("The tcp port must be 0-65535")
                return 301, 3004

    def create_switch(self, switch):
        ifdsrppath = '/etc/qemu-%s-ifdown' % switch
        tulist = []
        if self.flag == 'o':
            ifsrppath = '/etc/qemu-%s-%s-ifup' % (switch, self.vid)
            ifdscript = ('#!/bin/sh\n'
                         'switch=%s\n'
                         'ip link set $1 down\n'
                         'ovs-vsctl del-port ${switch} $1' % switch)
            ifscript = ('#!/bin/sh\n'
                        'switch=%s\n'
                        'ip link set $1 up\n'
                        'ovs-vsctl add-port ${switch} $1' % switch)
            if self.vid == '0':
                ifscript += '\n'
            else:
                tagstr = ' tag=%s\n' % self.vid
                ifscript += tagstr
        elif self.flag == 's':
            ifsrppath = "/etc/qemu-%s-lbr-ifup" % switch
            ifscript = ('#!/bin/sh\n'
                        'switch=%s\n'
                        'ip link set $1 up\n'
                        'brctl addif ${switch} $1\n') % switch
            ifdscript = ('#!/bin/sh\n'
                         'switch=%s\n'
                         'ip link set $1 down\n'
                         'brctl delif ${switch} $1\n') % switch
        else:
            self.bp('The bridge flag %s is invalid.' % self.flag)
            os.sys.exit(1)
        tulist.append((ifsrppath, ifscript))
        tulist.append((ifdsrppath, ifdscript))
        for list in tulist:
            path, script = list
            if not os.path.exists(path):
                iswrite = open(path, 'w')
                iswrite.write(script)
                iswrite.close()
                os.system("chmod +x %s" % path)
        cmd = "ip link show  %s" % switch
        status, output = commands.getstatusoutput(cmd)
        if status:
            self.bp(output)
            self.bp("Creating %s" % switch)
            if self.flag == 's':
                cmd = "brctl addbr %s" % switch
            elif self.flag == 'o':
                cmd = "ovs-vsctl add-br %s" % switch
            else:
                self.bp('The bridge flag %s is invalid.' % self.flag)
                os.sys.exit(1)
            status, output = commands.getstatusoutput(cmd)
            if status:
                self.bp(output)
                self.bp("%s created failed, quit" % switch)
                os.sys.exit(status)
        cmd = "ip link set %s up" % switch
        print cmd
        status, output = commands.getstatusoutput(cmd)
        if status:
            self.bp(output)
            self.bp("Setup %s failed" % switch)
            os.sys.exit(status)
        return ifsrppath, ifdsrppath

    def VM_srp(self):
        vm_img, vm_name = self.img_handle(self.vm_name)
        gcmdpath = "%s/%s.sh" % (self.cmdpath, vm_name)
        if not os.path.exists(self.cmdpath):
            os.mkdir(self.cmdpath)
        if os.path.exists(gcmdpath):
            return 1, gcmdpath, vm_name
        vnarg = "-name %s \\\n" % vm_name
        mac_addr = self.new_mac()
        vport = self.vnc_port(self.vm_vnc)
        mtearg = self.mtarg()
        ifs, ifds = self.create_switch(self.switch)
        vm_qemu = "/usr/libexec/qemu-kvm \\\n"
        vm_bsarg = ('-realtime mlock=off \\\n'
                    '-no-user-config -nodefaults -rtc base=utc \\\n'
                    '-boot menu=on -usb -device usb-kbd,id=input0 \\\n'
                    '-device usb-mouse,id=input1 -vga std \\\n'
                    '-device scsi-cd,bus=scsi0.0,channel=0,scsi-id=1,'
                    'lun=0,drive=drive-scsi0-0-0-1,'
                    'id=scsi0-0-0-1,bootindex=2 \\\n'
                    '-device scsi-cd,bus=scsi0.0,channel=0,scsi-id=2,'
                    'lun=0,drive=drive-scsi0-0-0-2,'
                    'id=scsi0-0-0-2 \\\n'
                    '-device scsi-hd,bus=scsi0.0,channel=0,'
                    'scsi-id=0,lun=0,drive=drive-scsi0-0-0-0,'
                    'id=scsi0-0-0-0,bootindex=1 \\\n'
                    '-boot menu=on \\\n'
                    '-drive if=none,id=drive-scsi0-0-0-1,readonly=on,'
                    'format=raw \\\n'
                    '-drive if=none,id=drive-scsi0-0-0-2,readonly=on,'
                    'format=raw \\\n')
        memarg = '-m %s \\\n' % self.m_size
        cpuarg = ('-smp %s,sockets=1,cores=%s,threads=1 '
                  '\\\n') % (self.c_nums, self.c_nums)
        imgarg = ('-drive file=%s,if=none,id=drive-scsi0-0-0-0,'
                  'format=qcow2,cache=none \\\n') % vm_img
        vncarg = "-vnc :%s \\\n" % vport
        taparg = ("-netdev tap,id=netdev,script=%s,"
                  "downscript=%s,vhost=on \\\n") % (ifs, ifds)
        vnicarg = ('-device virtio-net-pci,netdev=netdev,id=net1,'
                   'mac=%s,bus=pci.0,addr=0x5 \\\n') % mac_addr
        qmparg = "-qmp unix:/tmp/qmp%ssocket.sock,server,nowait \\\n" % vm_name
        hmparg = ('-monitor unix:/tmp/hmp%ssocket.sock,server,nowait '
                  '\\\n') % vm_name
        vm_clilist = [
            vm_qemu,
            mtearg,
            memarg,
            cpuarg,
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
        f_vm = open(gcmdpath, 'w')
        f_vm.write(vm_cli)
        f_vm.close()
        return 0, gcmdpath, vm_name


def runvm(gcmdpath, vmcdrom, vm_name, vnc_port):
    shcmd = " sh %s & " % gcmdpath
    status = os.system(shcmd)
    if status:
        breakprint("The vm is not started, please check your cmdline.")
        readcmd(gcmdpath)
        os.sys.exit(status)
    breakprint("Connect vnc port %s, if you like" % vnc_port)
    if vmcdrom == "true":
        changecd(vm_name)
    os.sys.exit(0)


def changecd(vm_name):
    cd_dir = {
        '1': 'drive-scsi0-0-0-1',
        '2': 'drive-scsi0-0-0-2',
        'q': '0'
        }
    cd_id = raw_input(('Please input which cdrom to use:\n'
                       '1: CDROM1\n'
                       '2: CDROM2\n'
                       'q: Will not change cdrom for %s\n>') % vm_name)
    try:
        cd = cd_dir[cd_id]
    except KeyError:
        breakprint('Invalid input, please follow the menu prompts.')
        return changecd(vm_name)
    if cd == '0':
        os.sys.exit(0)
    iso_path = retry_iso(vm_name)
    ejectcmd = 'eject -f %s' % cd
    hmpcmd(ejectcmd, vm_name)
    cmd = 'change %s %s' % (cd, iso_path)
    hmpcmd(cmd, vm_name)
    ckcmd = "info block"
    choutput = hmpcmd(ckcmd, vm_name)
    ck_pn = re.compile(r"%s: (.*?) \(raw, read-only\)" % cd)
    if ck_pn.findall(choutput)[0] == iso_path:
        breakprint("Insert %s succeed." % iso_path)
        os.sys.exit(0)
    breakprint("Insert %s failed." % iso_path)
    os.sys.exit(1)


def retry_iso(vm_name):
    iso_path = raw_input("Please provide the path of the iso:\n>")
    if not os.path.exists(iso_path):
        chc = raw_input(('The iso %s does not exist,'
                         'if retry?(Y/N)\n>') % iso_path)
        if chc == "Y" or chc == "y":
            return retry_iso(vm_name)
        elif chc == "N" or chc == "n":
            breakprint("Will not change cdrom for %s" % vm_name)
            os.sys.exit(0)
        else:
            breakprint("Invalid input, quiting.")
            os.sys.exit(1)
    return iso_path


def hmpcmd(hmpcli, vm_name):
    cmd = '''echo "%s"|nc -U /tmp/hmp%ssocket.sock''' % (hmpcli, vm_name)
    status, output = commands.getstatusoutput(cmd)
    if status:
        breakprint(output)
        breakprint("Failed to commands the qemu.")
        os.sys.exit(status)
    return output


def readcmd(gcmdpath):
    f_vm = open(gcmdpath)
    try:
        cmdtext = f_vm.read()
    finally:
        f_vm.close()
    vncptn = re.compile(r'\-vnc \:(\d+) ')
    o_p = vncptn.findall(cmdtext)[0]
    vnc_p = int(o_p) + 5900
    return cmdtext, vnc_p


def readtag(vmcli):
    f_vm = open(vmcli)
    try:
        cmdtext = f_vm.read()
    finally:
        f_vm.close()
    tagptn = re.compile(r"script=/etc/qemu\-.*?\-(.*?)-ifup")
    vmtag = tagptn.findall(cmdtext)[0]
    return vmtag


def listvms(imgpath):
    cmd = "ps aux |grep qemu"
    if not os.path.isdir(imgpath):
        breakprint("No images found, please try to define a new vm.")
        os.sys.exit(1)
    img_ptn = re.compile(r"(.*?).qcow2")
    vmname_ptn = re.compile(r"\-name (.*?) \-.*? \-vnc \:(\d+) ")
    tag_ptn = ("\-name (.*?) .*? "
               "\-netdev tap,id=netdev,"
               "script=/etc/qemu-(.*?)-(.*?)-ifup")
    vm_tag_ptn = re.compile(r"%s" % tag_ptn)
    status, output = commands.getstatusoutput(cmd)
    if status:
        breakprint(output)
        os.sys.exit(status)
    nm_pt_list = vmname_ptn.findall(output)
    nm_tag_list = vm_tag_ptn.findall(output)
    print nm_tag_list
    breakprint(("The running vms and their corresponding vnc ports:\n\n"
                '\tGuest\t\tVNC ports:'))
    for vm_name, port in nm_pt_list:
        vnc_p = int(port) + 5900
        print ">\t%s\t\t%s" % (vm_name, vnc_p)
    breakprint("Please connect with the right port")
    breakprint(("The running vms and their corresponding VLAN ID(TAG):\n\n"
                "\tGuset\t\tOVS BR\t\tVLANID:"))
    for vm_name, ovs, tag in nm_tag_list:
        if tag == 'lbr':
            tag = "linux bridge, no VLAN configured"
        print ">\t%s\t\t%s\t\t%s" % (vm_name, ovs, tag)
    breakprint(("Configure inside guest with "
                "right IP address of the right vlan."))
    imgslist = os.listdir(imgpath)
    all_names = [img_ptn.findall(img)[0] for img in imgslist]
    all_imgs = '\n>\t'.join(all_names)
    print('All the vms that have imgs list below:\n\n\tGuest')
    breakprint('>\t%s' % all_imgs)


def removevm(imgpath, cmdpath):
    vm_name = raw_input(("Please specify the vm name "
                         "that you want to remove.\n>"))
    vmimg = os.path.join(imgpath, vm_name + '.qcow2')
    vmcli = os.path.join(cmdpath, vm_name + '.sh')
    cmd = (("ps -ef |grep %s"
            "|grep -v 'grep'|awk '{print $2}' ") % vmimg)
    status, output = commands.getstatusoutput(cmd)
    if status:
        breakprint(output)
        os.sys.exit(status)
    if output:
        breakprint(('The vm is running, won\'t remove it.\n'
                    'The pid of the vm is %s, if the vm has '
                    'not a system installed, you can use kill -9 %s '
                    'to shutdown the vm.\n'
                    'But if the vm has a system started, '
                    'please shutdown it inside the system.')
                   % (output, output))
        os.sys.exit(0)
    if not os.path.isfile(vmimg) and not os.path.isfile(vmcli):
        breakprint(('%s does not exist, will do nothing') % vm_name)
        os.sys.exit(0)
    elif not os.path.isfile(vmimg) and os.path.isfile(vmcli):
        breakprint(('%s has not image found,'
                    'will delete the script %s') % (vm_name, vmcli))
        if_rm(vmcli)
        os.sys.exit(0)
    elif os.path.isfile(vmimg) and not os.path.isfile(vmcli):
        breakprint(('%s has not script found, '
                    'will delete the vm image %s.') % (vm_name, vmimg))
        if_rm(vmimg)
        os.sys.exit(0)
    else:
        if_rm(vmimg)
        if_rm(vmcli)
        os.sys.exit(0)


def if_rm(file):
    chc = raw_input(('Are you sure to delete the %s?'
                     '(Y/N)\n>') % file)
    if chc == 'Y' or chc == 'y':
        os.remove(file)
    elif chc == 'N' or chc == 'n':
        breakprint(('Do nothing, just quit.'))
        os.sys.exit(0)
    else:
        breakprint(('Invalid input, please Input Y/N.'))
        return if_rm(file)


def vid(cmdpath, vm_name):
    vmcli = os.path.join(cmdpath, vm_name + '.sh')
    if os.path.isfile(vmcli):
        tag = readtag(vmcli)
        breakprint('%s has configuration, checking tag.' % vm_name)
        if tag == 'lbr':
            breakprint(('%s is under a linux bridge,'
                        'does not support vlan.') % vm_name)
            newtag = inputtag()
            if_rm(vmcli)
        else:
            newtag = taghandle(tag)
    else:
        newtag = inputtag()
    return newtag


def inputtag():
    chc = raw_input('If to build the vm to use the ovs?(Y/N)\n>')
    if chc == 'Y' or chc == 'y':
        intag = raw_input('Please input the vlan id:\n>')
        newtag = taghandle(intag)
    elif chc == 'N' or chc == 'n':
        breakprint('Do nothing, just quit.')
        os.sys.exit(0)
    else:
        breakprint('Invalid input, just quit.')
        os.sys.exit(2)
    return newtag


def taghandle(tag):
    if tag == '' or tag == '0':
        breakprint('Using default vlan')
        newtag = '0'
    else:
        try:
            newtag = int(tag)
            if newtag > 4096 or newtag < 0:
                breakprint(("Invaid vlan id %s, should "
                            "less than 4096, and more than 0") % tag)
                os.sys.exit(1)
        except ValueError:
            breakprint("Invalid tag %s , tag must be a number." % tag)
            os.sys.exit(1)
    return newtag


def breakprint(cmd):
    breakline = ">" + "." * 29
    print breakline
    print cmd
    print breakline


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='simplekvm')
    parser.add_argument("-i",
                        dest="vm_name",
                        action="store",
                        metavar="VM NAME",
                        help="The vm name and the dst img name.",)
    parser.add_argument("-p",
                        action="store",
                        dest="vnc_p",
                        type=int,
                        metavar="TCP PORT",
                        help="If not assign a port, will assign random.")
    parser.add_argument("-m",
                        action="store",
                        dest="m_size",
                        metavar="MEM SIZE",
                        default="4G",
                        help="Specify the memory you want to use, default 4G")
    parser.add_argument("-c",
                        action="store",
                        dest="c_nums",
                        metavar="CPU NUMS",
                        default="4",
                        help="Specify the CPU numbers to the vm, default '4'")
    parser.add_argument("-s",
                        action="store",
                        dest="switch",
                        default="switch",
                        metavar="BRIDGE NAME",
                        help="specify the bridge(ovs/bridge) you want to use.")
    parser.add_argument("--run",
                        action="store_const",
                        dest="vmrun",
                        const='true',
                        default='false',
                        help="run the specified vm")
    parser.add_argument("--iso",
                        action="store_const",
                        dest="vmcdrom",
                        const="true",
                        default='false',
                        help="if insert a cdrom(an iso) to the vm.")
    parser.add_argument("--list",
                        action="store_const",
                        dest="lavms",
                        const='true',
                        default='false',
                        help="list the running vm infos")
    parser.add_argument('--remove',
                        action="store_const",
                        dest='ifrm',
                        const='true',
                        default='false',
                        help="Remove the image and script of the vm.")
    parser.add_argument("--snapshot",
                        action='store_const',
                        dest='snswitch',
                        const='true',
                        default='false',
                        help='Start a vm in snapshot mode')
    parser.add_argument("--ovs",
                        action='store_const',
                        dest='is_ovs',
                        const='true',
                        default='false',
                        help='Start a vm under ovs bridge')
    parser.add_argument("--version",
                        action="version",
                        version="%(prog)s 0.38")
    args = parser.parse_args(sys.argv[1:])
    progpath = '/var'
    imgdst = 'vmimgs'
    cmddst = 'vmcli'
    imgpath = os.path.join(progpath, imgdst)
    cmdpath = os.path.join(progpath, cmddst)

    if ''.join(sys.argv[1:]) == '--list':
        listvms(imgpath)
        os.sys.exit(0)
    elif args.lavms == 'true' and sys.argv[1:].remove("--list") != []:
        breakprint("Please do not use --list with other args.")
        os.sys.exit(1)

    if ''.join(sys.argv[1:]) == '--remove':
        removevm(imgpath, cmdpath)
    elif args.ifrm == 'true' and sys.argv[1:].remove('--remove') != []:
        breakprint('Please do not use --remove with other args.')
        os.sys.exit(1)

    if args.vm_name is None:
        print "Please provide the vm name you want to use."
        parser.print_help()
        os.sys.exit(0)

    vm_name = args.vm_name
    m_size = args.m_size
    c_nums = args.c_nums
    o_vnc = args.vnc_p
    g_vnc = o_vnc
    ifrun = args.vmrun
    switch = args.switch
    vmcdrom = args.vmcdrom
    snswitch = args.snswitch
    is_ovs = args.is_ovs
    if is_ovs == 'true':
        flag = 'o'
        breakprint('You are to use ovs as the bridge')
        vid = vid(cmdpath, vm_name)
    else:
        flag = 's'

    if ifrun == "true" and snswitch == "true":
        new_vm = NewVM(vm_name,
                       switch,
                       m_size,
                       c_nums,
                       imgpath,
                       cmdpath,
                       g_vnc,
                       flag,
                       vid)
        status, gcmdpath, vm_name = new_vm.VM_srp()
        cmdtext, vnc_port = readcmd(gcmdpath)
        tmpcmd = cmdtext + "-snapshot \\\n"
        breakprint('Snapshot of %s is to run' % vm_name)
        breakprint(tmpcmd)
        status = os.system("%s &" % tmpcmd)
        if status:
            breakprint("The vm is not started, please check your cmdline.")
            readcmd(gcmdpath)
            os.sys.exit(status)
        if vmcdrom == 'true':
            changecd(vm_name)
        breakprint("Connect the vnc with vnc port %s" % vnc_port)
        os.sys.exit(0)

    elif ifrun == "true" and snswitch == "false":
        new_vm = NewVM(vm_name,
                       switch,
                       m_size,
                       c_nums,
                       imgpath,
                       cmdpath,
                       g_vnc,
                       flag,
                       vid)
        status, gcmdpath, vm_name = new_vm.VM_srp()
        if status == 1:
            vmfcmd, vnc_port = readcmd(gcmdpath)
            breakprint(("The qemu script exist,"
                        'other configuraton args won\'t work.'
                        'the cmdline is  like this:'))
            breakprint(vmfcmd)
            ch = raw_input("If direct to start it?(Y/N)\n>")
            if ch == "Y" or ch == 'y':
                runvm(gcmdpath, vmcdrom, vm_name, vnc_port)
            elif ch == "N" or ch == 'n':
                breakprint(('WARN: %s exist,'
                            'you can start the script by shell,'
                            'and remove it if you like.') % gcmdpath)
                os.sys.exit(0)
            else:
                breakprint("Wrong input, just quit.")
                os.sys.exit(1)
        elif status == 0:
            vmfcmd, vnc_port = readcmd(gcmdpath)
            breakprint("The cmdline is like this:")
            breakprint(vmfcmd)
            runvm(gcmdpath, vmcdrom, vm_name, vnc_port)
        else:
            breakprint("Got wrong code#%s, quit." % status)
            os.sys.exit(status)

    elif ifrun == "false" and vmcdrom == "true":
        cmd = "ps -aux |grep %s" % vm_name
        status, output = commands.getstatusoutput(cmd)
        if status:
            breakprint(output)
            os.sys.exit(status)
        if "-name %s" % vm_name in output:
            breakprint(('WARN: Only insert iso to the running VM,'
                        'other arguments won\'t work.'))
            changecd(vm_name)
            os.sys.exit(0)
        else:
            breakprint("VM %s is not running, will do nothing." % vm_name)
            os.sys.exit(status)

    elif ifrun == "false" and vmcdrom == "false":
        new_vm = NewVM(vm_name,
                       switch,
                       m_size,
                       c_nums,
                       imgpath,
                       cmdpath,
                       g_vnc,
                       flag,
                       vid)
        status, gcmdpath, vm_name = new_vm.VM_srp()
        if status == 1:
            vmfcmd, vmc_port = readcmd(gcmdpath)
            breakprint(('%s exists, and no script will be created,'
                        'please check if the script is the one you want,'
                        'you can start with --run or use shell to run it,'
                        'if you are to run with the shell script,'
                        'use %s as the '
                        'vnc port to connect.') % (gcmdpath, vmc_port))
            breakprint(vmfcmd)
        elif status == 0:
            vmfcmd, vnc_port = readcmd(gcmdpath)
            breakprint(('Your script %s is ready,'
                        'you can start it next time with --run '
                        'or use shell to run it,'
                        'if you are to run with the shell script,'
                        'use %s as the vnc port to '
                        'connect.') % (gcmdpath, vnc_port))
            breakprint(vmfcmd)
        else:
            breakprint("Got wrong code#%s, quit." % status)
