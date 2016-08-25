import os
import commands
import random
import socket
import argparse
import sys
import re


class NewVM(object):
    def __init__(self, vm_name, switch, g_vnc):
        self.vm_name = vm_name
        self.vm_vnc = g_vnc
        self.switch = switch

    def bp(self, str):
        breakline = "*"
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
            return ('-machine pserise-rhel7.2.0,accel=kvm,usb=off'
                    '-device spapr-vscsi,id=scsi0,reg=0x2000 \\\n')
        elif output == "x86_64":
            return ('-machine pc-i440fx-rhel7.0.0,accel=kvm,usb=off \\\n'
                    '-cpu host \\\n'
                    '-device virtio-scsi-pci,id=scsi0,bus=pci.0,addr=0x9 \\\n')
        else:
            self.bp("get wrong type %s, quit.\n" % output)
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
        vmimg = "%s/%s.qcow2" % (imgpath, vm_name)
        if not os.path.exists(imgpath):
            os.mkdir(imgpath)
        cic = {
            "Y": self.chc_y,
            "N": self.chc_n,
        }
        if os.path.exists(vmimg):
            chc = raw_input("%s exist, if use this VM image.(Y/N)" % vmimg)
            newimg = self.chc_c(cic, chc, vmimg)
            return newimg, vm_name
        else:
            self.bp("%s does not exist, please choose:\n" % vmimg)
            newimg = self.chmenu(vmimg)
            return newimg, vm_name

    def chc_c(self, cic, chc, vmimg):
        try:
            cic[chc](vmimg)
            return vmimg
        except KeyError:
            self.bp("invalid input, quit.\n")
            os.sys.exit(1)

    def chmenu(self, vmimg):
        chc = raw_input('''
        1:  Copy from an exist IMG
        2:  create and install a new OS
        q:  quit
                        \n''')
        cic = {
            "1": self.img_cp,
            "2": self.cre_img,
            "q": self.quit,
        }
        return self.chc_c(cic, chc, vmimg)

    def chc_y(self, vmimg):
        cmd = "ps aux |grep %s" % vmimg
        status, output = commands.getstatusoutput(cmd)
        if status:
            self.bp(output)
            os.sys.exit(1)
        if "file=%s" % vmimg in output:
            self.bp(("The image %s is used by another activate guest,"
                    "please check") % vmimg)
            os.sys.exit(3)

    def chc_n(self, vmimg):
        self.bp("Won't use the %s as the bootdisk, so " % vmimg)
        vm_name = raw_input("please specify a new vm name:\n")
        return self.img_handle(vm_name)

    def img_cp(self, vmimg):
        srcimg = raw_input("Please specify the base image:\n")
        if srcimg == "quit":
            os.sys.exit(0)
        if not os.path.exists(srcimg):
            self.bp("%s does not exist. back to menu:\n" % srcimg)
            return self.chmenu(vmimg)
        else:
            cmd = "cp %s %s" % (srcimg, vmimg)
            status, output = commands.getstatusoutput(cmd)
            if status:
                self.bp("CMD cp failed\n")
                self.bp(output)
                os.sys.exit(status)

    def cre_img(self, vmimg):
        imgsize = raw_input(("Please input the size you want to use,"
                            "e.g. 50G, 100M, ...\n"))
        cmd = "qemu-img create -f qcow2 %s %s" % (vmimg, imgsize)
        status, output = commands.getstatusoutput(cmd)
        if status:
            self.bp(output)
            os.sys.exit(status)
        self.bp("Creating the img...")
        self.bp(output)

    def quit(self, vmimg):
        self.bp("Will not create %s, just quit.\n" % vmimg)
        os.sys.exit(0)

    def gen_vncp(self):
        new_p = random.randint(0, 59635)
        vnc_pt = new_p + 5900
        res = self.__chk_vncp(new_p)
        if res == 303:
            self.bp("The new vnc port is %s" % vnc_pt)
            return new_p
        elif res == 301:
            return self.gen_vncp()
        else:
            self.bp("Generae vnc port faild.\n")
            self.bp("Invalid code#%s, exit.\n" % res)
            os.sys.exit(res)

    def vnc_port(self, vnc_p):
        if vnc_p is None:
            return self.gen_vncp()
        f_re = self.__chk_vncp(vnc_p)
        if f_re == 303:
            return vnc_p
        elif f_re == 301:
            return self.input_p()
        else:
            self.bp("Invalid code#%s, exit.\n" % f_re)
            os.sys.exit(f_re)

    def input_p(self):
        new_p = raw_input("input a new port, or left to randomly specify:\n")
        try:
            int_p = int(new_p)
            return self.vnc_port(int_p)
        except ValueError:
            return self.vnc_port(new_p)

    def __chk_vncp(self, old_p):
        if type(old_p) != int:
            self.bp("Invalid type, need an int")
            return 301
        vnc_p = old_p + 5900
        if vnc_p < 5900:
            self.bp("The vnc port must be 0 ~ 59635")
            return 301
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            rt_value = s.connect_ex(('127.0.0.1', vnc_p))
            if rt_value == 0:
                self.bp("Used in system")
                return 301
            return 303
        except OverflowError:
            self.bp("The tcp port must be 0-65535")
            return 301

    def create_switch(self, switch):
        ifsrppath = "/etc/qemu-%s-ifup" % switch
        ifscript = '''#!/bin/show
        switch=%s
        ip link set $1 up
        brctl addif ${switch} $1
        ''' % switch
        if not os.path.exists(ifsrppath):
            iswrite = open(ifsrppath, 'w')
            iswrite.write(ifscript)
            iswrite.close()
            os.system("chmod +x %s" % ifsrppath)
        cmd = "ip link show  %s" % switch
        status, output = commands.getstatusoutput(cmd)
        if status:
            self.bp(output)
            self.bp("Creaing %s" % switch)
            cmd = "brctl addbr %s" % switch
            status, output = commands.getstatusoutput(cmd)
            if status:
                self.bp(output)
                self.bp("brctl hit error, quit")
                os.sys.exit(status)
        cmd = "ip link set %s up" % switch
        status, output = commands.getstatusoutput(cmd)
        if status:
            self.bp(output)
            self.bp("setup %s failed" % switch)
            os.sys.exit(status)
        return ifsrppath

    def VM_srp(self):
        vm_img, vm_name = self.img_handle(self.vm_name)
        cmdpath = "/var/vmcli"
        gcmdpath = "%s/%s.sh" % (cmdpath, vm_name)
        if not os.path.exists(cmdpath):
            os.mkdir(cmdpath)
        if os.path.exists(gcmdpath):
            return 1, gcmdpath, vm_name
        vnarg = "-name %s \\\n" % vm_name
        mac_addr = self.new_mac()
        vport = self.vnc_port(self.vm_vnc)
        mtearg = self.mtarg()
        ifscript = self.create_switch(self.switch)

        vm_qemu = "/usr/libexec/qemu-kvm \\\n"
        vm_bsarg = ('-m 16G -realtime mlock=off \\\n'
                    '-smp 8,sockets=1,cores=8,threads=1 \\\n'
                    '-no-user-config -nodefaults -rtc base=utc \\\n'
                    '-boot menu=on -usb -device usb-kbd,id=input0 \\\n'
                    '-device usb-mouse,id=input1 -vga std \\\n'
                    '-device scsi-cd,bus=scsi0.0,channel=0,scsi-id=0,'
                    'lun=0,drive=drive-scsi0-0-0-0,'
                    'id=scsi0-0-0-0,bootindex=2 \\\n'
                    '-device virtio-blk-pci,scsi=off,bus=pci.0,addr=0x6,'
                    'drive=drive-virtio-disk0,id=virtio-disk0,bootindex=1 \\\n'
                    '-boot menu=on \\\n'
                    '-drive if=none,id=drive-scsi0-0-0-0,readonly=on,'
                    'format=raw \\\n')
        imgarg = ('-drive file=%s,if=none,id=drive-virtio-disk0,'
                  'format=qcow2,cache=none \\\n') % vm_img
        vncarg = "-vnc :%s \\\n" % vport
        taparg = "-netdev tap,id=netdev,script=%s,vhost=on \\\n" % ifscript
        vnicarg = ('-device virtio-net-pci,netdev=netdev,id=net1,'
                   'mac=%s,bus=pci.0,addr=0x5 \\\n') % mac_addr
        qmparg = "-qmp unix:/tmp/%sqmpsocket.sock,server,nowait \\\n" % vm_name
        hmparg = ('-monitor unix:/tmp/%shmpsocket.sock,server,nowait '
                  '\\\n') % vm_name
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
        f_vm = open(gcmdpath, 'w')
        f_vm.write(vm_cli)
        f_vm.close()
        return 0, gcmdpath, vm_name


def runvm(gcmdpath):
    shcmd = " sh %s & " % gcmdpath
    status = os.system(shcmd)
    if status:
        breakprint("the vm is not started, please check your cmdline.\n")
        readcmd(gcmdpath)
        os.sys.exit(status)


def changecd(vm_name):
    iso_path = raw_input("please provide the path of the iso:\n")
    if not os.path.exists(iso_path):
        chc = raw_input("the iso %s does not exist,if retry?(Y/N))" % iso_path)
        err = "no"
        while err == "no":
            if chc == "Y":
                err = "yes"
                return changecd(vm_name)
            elif chc == "N":
                breakprint("Will not change cdrom for %s" % vm_name)
                err = "yes"
                return 0
            else:
                chc = raw_input("invalid input, retry(Y/N):")
                err = "no"
    cmd = "change drive-scsi0-0-0-0 %s" % iso_path
    hmpcmd(cmd, vm_name)


def hmpcmd(hmpcli, vm_name):
    cmd = '''echo "%s"|nc -U /tmp/%shmpsocket.sock''' % (hmpcli, vm_name)
    status, output = commands.getstatusoutput(cmd)
    if status:
        breakprint(output)
        breakprint("failed to commands the qemu.\n")
        os.sys.exit(status)


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


def breakprint(cmd):
    breakline = "*"
    print breakline
    print cmd
    print breakline


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i",
                        action="store",
                        dest="vm_name",
                        metavar="VM NAME",
                        help="The vm name and the dst img name.",)
    parser.add_argument("-p",
                        action="store",
                        dest="vnc_p",
                        type=int,
                        metavar="TCP PORT",
                        help="If not assign a port, will assign random.")
    parser.add_argument("-s",
                        action="store",
                        dest="switch",
                        default="switch",
                        metavar="LINUX BRIDGE",
                        help="specify the linux bridge you want to use.")
    parser.add_argument("--run",
                        nargs='?',
                        action="store",
                        dest="vmrun",
                        const='true',
                        default='false',
                        help="run the specified vm")
    parser.add_argument("--iso",
                        nargs='?',
                        action="store",
                        dest="vmcdrom",
                        const="true",
                        default='false',
                        help="if insert a cdrom(an iso) to the vm.")
    parser.add_argument("--snapshot",
                        nargs='?',
                        action='store',
                        dest='snswitch',
                        const='true',
                        default='false',
                        help='Start a vm in snapshot mode')
    args = parser.parse_args(sys.argv[1:])

    if args.vm_name is None:
        print "Please provide the vm name you want to use."
        parser.print_help()
        os.sys.exit(0)

    vm_name = args.vm_name
    g_vnc = args.vnc_p
    ifrun = args.vmrun
    switch = args.switch
    vmcdrom = args.vmcdrom
    snswitch = args.snswitch
    if ifrun == "true" and snswitch == "true":
        new_vm = NewVM(vm_name, switch, g_vnc)
        status, gcmdpath, vm_name = new_vm.VM_srp()
        cmdtext, vnc_port = readcmd(gcmdpath)
        tmpcmd = cmdtext + " -snapshot"
        breakprint(tmpcmd)
        status = os.system("%s &" % tmpcmd)
        if status:
            breakprint("the vm is not started, please check your cmdline.\n")
            readcmd(gcmdpath)
            os.sys.exit(status)
        if vmcdrom == 'true':
            changecd(vm_name)
        breakprint("Connect the vnc with vnc port %s" % vnc_port)
        os.sys.exit(0)

    if ifrun == "false" and vmcdrom == "true":
        cmd = "ps -aux |grep %s" % vm_name
        status, output = commands.getstatusoutput(cmd)
        if status:
            breakprint(output)
            os.sys.exit(status)
        if "-name %s" % vm_name not in output:
            breakprint("VM %s is not running, will do nothing." % vm_name)
            os.sys.exit(status)
            breakprint(('WARN: Only insert iso to the running VM,'
                        'no need specify -s, -p\n'))
        changecd(vm_name)
        os.sys.exit(0)

    new_vm = NewVM(vm_name, switch, g_vnc)
    status, gcmdpath, vm_name = new_vm.VM_srp()
    if ifrun == "true":
        if status == 1:
            vmfcmd, vnc_port = readcmd(gcmdpath)
            breakprint(("the qemu script exist, -s and -p won't work."
                        'the cmdline is  like this:\n'))
            breakprint(vmfcmd)
            ch = raw_input("\n if direct run it?(Y/N)")
            if ch == "Y":
                runvm(gcmdpath)
                if vmcdrom == "true":
                    changecd(vm_name)
                breakprint("Connect vnc port %s, if you like." % vnc_port)
                os.sys.exit(0)
            elif ch == "N":
                breakprint(('WARN: %s exist,'
                            'you can start the script by shell,'
                            'and remove it if you like.\n') % gcmdpath)
                os.sys.exit(0)
            else:
                breakprint("wrong input, just quit.\n")
                os.sys.exit(1)
        elif status == 0:
            vmfcmd, vnc_port = readcmd(gcmdpath)
            breakprint("The cmdline is like this:\n")
            breakprint(vmfcmd)
            runvm(gcmdpath)
            if vmcdrom == "true":
                changecd(vm_name)
            breakprint("Connect vnc port %s, if you like" % vnc_port)
            os.sys.exit(0)
        else:
            breakprint("got wrong code#%s, quit.\n" % status)
            os.sys.exit(status)
    elif ifrun == "false" and vmcdrom == "false":
        if status == 1:
            vmfcmd, vmc_port = readcmd(gcmdpath)
            breakprint(('%s exists, and no script created,'
                        'please check if the script is the one you want,'
                        'you can start with --run or use shell to run it,'
                        'if you are to run with the shell script,'
                        'use %s as the'
                        'vnc port to connect.\n') % (gcmdpath, vmc_port))
            breakprint(vmfcmd)
        elif status == 0:
            vmfcmd, vnc_port = readcmd(gcmdpath)
            breakprint(('Your script %s is ready,'
                        'you can start it next time with --run'
                        'or use shell to run it,'
                        'if you are to run with the shell script,'
                        'use %s as the vnc port to'
                        'connect.\n') % (gcmdpath, vnc_port))
            breakprint(vmfcmd)
        else:
            breakprint("got wrong code#%s, quit.\n" % status)
