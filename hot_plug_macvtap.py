import os
import sys
import re
import commands
try:
    p_if = sys.argv[1]
    m_name = sys.argv[2]
    m_mode = sys.argv[3]
except IndexError:
    print '''usage, python this_script.py\
    $physical_interface $name_macvtap $macvtap_mode'''
    os.sys.exit(0)
if commands.getstatusoutput('ip link add link %s name \
    %s type macvtap mode %s' %(p_if, m_name, m_mode))[0] == 0:
    print '%s is created ok' %m_name
else:
    print '%s is create failed' %m_name
    os.sys.exit(0)
if commands.getstatusoutput('ip link set %s add 54:52:00:0a:0b:1b up' %m_name)[0] == 0:
    print 'mac address is changed to 54:52:00:0a:0b:1b'
else:
    print 'mac address is not changed'
    os.sys.exit(0)
macvtap_interface = commands.getstatusoutput('ip l show %s' %m_name)
p = r'^(\d+):'
#print p
#print  re.findall(p, macvtap_interface[1])
macvtap_index = int(re.findall(p, macvtap_interface[1])[0])
cmd = '/usr/libexec/qemu-kvm -name rhel  -M rhel6.6.0 -enable-kvm -m 4096 \
    -realtime mlock=off -smp 1,sockets=1,cores=1,threads=1 \
    -uuid 6e5f004f-c5a9-38e6-2be2-091b08d2e2ac -nodefconfig -nodefaults  \
    -rtc base=utc  -device ich9-usb-ehci1,id=usb,bus=pci.0,addr=0x5.0x7 \
    -device ich9-usb-uhci1,masterbus=usb.0,firstport=0,bus=pci.0,multifunction=on,addr=0x5 \
    -device ich9-usb-uhci2,masterbus=usb.0,firstport=2,bus=pci.0,addr=0x5.0x1 \
    -device ich9-usb-uhci3,masterbus=usb.0,firstport=4,bus=pci.0,addr=0x5.0x2 \
    -drive file=/home/rhel67.raw,snapshot=on,if=none,id=drive-blk0,format=raw,cache=none \
    -device virtio-blk-pci,bus=pci.0,addr=0x6,drive=drive-blk0,id=blk0,bootindex=1  \
    -vnc :0 -vga cirrus -monitor stdio\
    '
fd = os.open('/dev/tap%s' %macvtap_index, os.O_RDWR)
vhostfd = os.open('/dev/vhost-net', os.O_RDWR)
print 'please hotplug in hmp/qmp with\
        fd=%s,vhost=on,vhostfd=%s' %(fd, vhostfd)
os.system(cmd)
if commands.getstatusoutput('ip link delete %s' %m_name)[0] == 0:
    print '\n %s is deleted ok' %m_name
else:
    print '\n ip link delete hits wrong'
