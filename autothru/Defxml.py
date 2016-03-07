#!/usr/bin/env python
# coding=utf-8
import random
import uuid
import sys
import xml.etree.ElementTree as ET


class Defxml(object):
    def __init__(self, basexml, sn_name):
        self.sn_name = sn_name
        self.newxml = sn_name + ".xml"
        self.xmlpath = "/etc/libvirt/qemu/"
        self.basexml = self.xmlpath + basexml
        self.newxml = self.xmlpath + self.newxml
        self.xmltree = ET.parse(self.basexml)
        self.rootelement = self.xmltree.getroot()
        self.devices = self.rootelement.find("devices")

    def modifyNodeName(self, e_node, nodename):
        node = self.rootelement.find(e_node)
        node.text = nodename
        self.xmltree.write(self.newxml)

    def modifyDomainName(self):
        self.modifyNodeName("name", self.sn_name)

    def modifyUuid(self):
        newuuid = str(uuid.uuid1())
        self.modifyNodeName("uuid", newuuid)

    def changeAttr(self, baseattr, subelement, subattr, basevalue, newvalue):
        number = 0
        attrs = self.devices.findall(baseattr)
        for attr in attrs:
            for item in attr.iter(subelement):
                if item.attrib[subattr] == basevalue:
                    item.attrib[subattr] = newvalue
                    number = number +1
        if number == 0:
            print "Can not find %s in the xml." % basevalue
            sys.exit(1)
        elif number > 1:
            print "Error: %s %s valued %s." % (number, baseattr, basevalue)
            sys.exit(2)
        self.xmltree.write(self.newxml)

    def changeImage(self, img_path, baseimg):
        sn_img = img_path + self.sn_name
        baseimg = img_path + baseimg
        self.changeAttr("disk", "source", "file", baseimg, sn_img)

    def changeMac(self, basemac):
        maclist = ["52", "54"]
        for i in range(1, 5):
            randstr = "".join(random.sample("0123456789abcdef", 2))
            maclist.append(randstr)
        randmac = ":".join(maclist)
        self.changeAttr("interface", "mac", "address", basemac, randmac)