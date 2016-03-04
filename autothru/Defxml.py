#!/usr/bin/env python
# coding=utf-8
import random
import commands
import uuid
import xml.etree.ElementTree as ET

class Defxml(object):
    def __init__(self, basexml, sn_name):
        self.sn_name = sn_name
        self.newxml = sn_name + ".xml"
        self.xmlpath = "/etc/libvirt/qemu/"
        self.basexml = self.xmlpath + basexml
        self.newxml = self.xmlpath + self.newxml
        self.cmd = "cp"
        self.cmd = self.cmd + " " + self.basexml + " " + self.newxml
        self.status, self.output = commands.getstatusoutput(self.cmd)
        self.xmltree = ET.parse(self.newxml)
        self.rootelement = self.xmltree.getroot()
        self.devices = self.rootelement.find("devices")
        
    def modifyNodeName(self, e_node, nodename):
        self.node = self.rootelement.find(e_node)
        self.node.text = nodename
        self.xmltree.write(self.newxml)

    def modifyDomainName(self):
        self.modifyNodeName("name", self.sn_name) 

    def modifyUuid(self):
        self.newuuid = str(uuid.uuid1())
        self.modifyNodeName("uuid", self.newuuid)
    
    def changeAttr(self, baseattr, subelement, subattr, basevalue, newvalue):
        self.number = 0
        self.attrs = self.devices.findall(baseattr)
        for attr in self.attrs:
            for item in attr.iter(subelement):
                value = item.attrib[subattr]
                if value == basevalue:
                    item.attrib[subattr] = newvalue
                    self.number = +1
        if self.number == 0:
            return 1
        if self.number > 0:
            return 2
        self.xmltree.write(self.newxml)

    def changeImage(self, img_path, baseimg):
        self.sn_img = img_path + self.sn_name
        self.changeAttr("disk", "source", "file", baseimg, self.sn_img)


#        if self.number == 0 :
#            print "Base image file name is wrong, check if %s is the right " %baseimg
#            return 1 
#        if self.number > 1:
#            print "%s images named %s in the vm xml file, need check." %(self.number, baseimg)
#            return 2

    def changeMac(self, basemac):
        self.maclist = []
        for i in range(1, 7):
            randstr = "".join(random.sample("0123456789abcdef", 2))
            self.maclist.append(randstr)
        self.randmac = ":".join(self.maclist)
        self.changeAttr("interfaces", "mac", "address", basemac, self.randmac)
        





    



