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
    modes = ["vepa", "bridge", "passthru", "private",]
    m_mode = modes[0]
    p_if = "eth0"
    pmac = re.compile(r"link/ether ([0-9a-fA-F]{2}([/\s:-][0-9a-fA-F]{2}){5})")
    for name, value in opts:
        if name == "--help":
            print usage()
        if name == "-i":
            p_if = value
        if name == "-n":
            m_name = value
        if name == "-m":
            if value not in modes:
                print "only support following modes %s" % ','.join(modes)
            m_mode = value
        if name == "--maddr":
            m_mac = value
    f_mac = pmac.findall(p_if)[0]
except getopt.GetoptError:
    print "Please check --help"
    print usage()
    sys.exit(0)

cmd = "ip link add link %s name %s" % (p_if, m_name)
cmd += " type macvtap mode %s" % m_mode
if commands.getstatusoutput(cmd)[0]:
    print '%s is create failed' % m_name
    sys.exit(1)
print '%s is created ok' % m_name

if m_mode == modes[2]:
    m_mac = f_mac
    print "The mode is %s, will use the mac of %s: %s " % (m_mode, p_if, m_mac)
    cmd = "ip link set %s up" % m_name
else:
    cmd = "ip link set %s add %s up " % (m_name, m_mac)
if commands.getstatusoutput(cmd)[0]:
    print 'mac address is not changed, cmd hit error.'
    sys.exit(0)
print 'mac of the macvtap interface now: %s' % m_mac
cmd = "ip link show %s" % m_name
macvtap_interface = commands.getstatusoutput(cmd)[1]
re_p = re.compile(r"^(\d+):")
index_list = re_p.findall(macvtap_interface)
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
    -device virtio-net-pci,vectors=4,netdev=hostnet0,id=net0,mac=%s,bus=pci.0,addr=0x3 \
    -vnc :0 -vga cirrus -monitor stdio\
    '
fd = os.open('/dev/tap%s' % macvtap_index, os.O_RDWR)
vhostfd = os.open('/dev/vhost-net', os.O_RDWR)
os.system(cmd % (fd, vhostfd, m_mac))
cmd = "ip link delete %s" % m_name
if commands.getstatusoutput(cmd)[0]:
    print 'ip link delete hits wrong'
    sys.exit(1)
print '%s is deleted ok' % m_name

