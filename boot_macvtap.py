import os
import sys
import re
import commands
import getopt
def usage():
    return'''
    '''
    
try:
    opts, args = getopt.getopt(sys.argv[1:], "i:n:m:", ['help', 'maddr'])
    m_mac = "54:52:00:0a:0b:1a"
    m_name = "macvtap0"
    m_mode = "vepa"
    for name, value in opts:
        if name == "--help":
            print usage()
        if name == "-i":
            p_if = value
        if name == "-n":
            m_name = value
        if name == "-m":
            m_mode = value
        if name == "--maddr":
            m_mac = value
except getopt.GetoptError:
    print "Please check --help"
    print usage()
    sys.exit(0)
    
cmd = "ip link add link %s name %s"
cmd += " type macvtap mode %s" % (p_if, m_name, m_mode)
if commands.getstatusoutput(cmd)[0] == 0:
    print '%s is created ok' % m_name
else:
    print '%s is create failed' % m_name
    sys.exit(1)
cmd = "ip link set %s add %s up " % (m_name, m_mac)
if commands.getstatusoutput(cmd)[0] == 0:
    print 'mac address is changed to %s' % m_mac
else:
    print 'mac address is not changed'
    sys.exit(0)
cmd = "ip link show %s" % m_name
macvtap_interface = commands.getstatusoutput(cmd)
re_p = re.compile(r"^(\d+):")
index_list = re_p.findall(macvtap_interface[1])
macvtap_index = int(index_list[0])
cmd = '/usr/libexec/qemu-kvm -name rhel  -M rhel6.6.0 -enable-kvm -m 4096 \
    -realtime mlock=off -smp 1,sockets=1,cores=1,threads=1 \
    -uuid 6e5f004f-c5a9-38e6-2be2-091b08d2e2ac -nodefconfig -nodefaults  \
    -rtc base=utc  -device ich9-usb-ehci1,id=usb,bus=pci.0,addr=0x5.0x7 \
    -device ich9-usb-uhci1,masterbus=usb.0,firstport=0,bus=pci.0,multifunction=on,addr=0x5 \
    -device ich9-usb-uhci2,masterbus=usb.0,firstport=2,bus=pci.0,addr=0x5.0x1 \
    -device ich9-usb-uhci3,masterbus=usb.0,firstport=4,bus=pci.0,addr=0x5.0x2 \
    -drive file=/home/rhel67.raw,if=none,id=drive-blk0,format=raw,cache=none \
    -device virtio-blk-pci,bus=pci.0,addr=0x6,drive=drive-blk0,id=blk0,bootindex=1  \
    -netdev tap,fd=%s,vhostfd=%s,id=hostnet0 \
    -device virtio-net-pci,vectors=4,netdev=hostnet0,id=net0,mac=54:52:00:0a:0b:1a,bus=pci.0,addr=0x3 \
    -vnc :0 -vga cirrus -monitor stdio\
    '
fd = os.open('/dev/tap%s' % macvtap_index, os.O_RDWR)
vhostfd = os.open('/dev/vhost-net', os.O_RDWR)
os.system(cmd % (fd, vhostfd))
cmd = "ip link delete %s" % m_name
if commands.getstatusoutput(cmd)[0] == 0:
    print '%s is deleted ok' % m_name
else:
    print 'ip link delete hits wrong'
    sys.exit(1)
