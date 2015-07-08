import os, sys

class Vlan(object):
    def __init__(self, interface='eth0', vlan_name='v20', vlanid=20, ipd=11):
        self.vlanid = vlanid
        self.interface = interface
        self.vlan_name = vlan_name
        self.ipd = ipd
        self.ip = '192.168.%s.%s/24' % (self.vlanid, self.ipd)

    def create_vlan(self):
        cmd = 'modprobe -r 8021q; modprobe 8021q'
        os.system(cmd)
        cmd = 'ip link add link %s name %s type vlan id %s'
        os.system(cmd % (self.interface, self.vlan_name, int(self.vlanid)))
        cmd = 'ip link set %s add 54:52:00:1a:20:01 up'
        os.system(cmd % self.vlan_name) 
        self.__set_ip()

    def delete_vlan(self):
        cmd = 'ip link delete %s'
        os.system(cmd % self.vlan_name)
    
    def __set_ip(self):
        cmd = 'ifconfig %s %s up' % (self.vlan_name, self.ip)
        os.system(cmd)


if __name__ == '__main__':
    try:
        interface = sys.argv[1]
        vlan_name = sys.argv[2]
        vlanid = int(sys.argv[3])
        ipd = int(sys.argv[4])
    except IndexError:
        print 'usage python xx.py interface vlan_name vlanid latest_bit_ip'
    test1 = Vlan(interface, vlan_name, vlanid, ipd)
    test1.create_vlan()
    vlan ={
        'vlan_name':test1.vlan_name,
        'interface':test1.interface,
        'vlanid':test1.vlanid,
        'ip address':test1.ip,
        
        }
    for x in vlan:
        print x+':'+str(vlan[x])
    #test1.delete_vlan()
#    print 'vlan name is %s, '
#    print test1.vlanid
#    print test1.interface
#    print test1.vlan_name

