#!/usr/bin/env python
# coding=utf-8
import uuid
import sys
import xml.etree.ElementTree as ET
import os


class Defxml(object):
    def __init__(self, basexml, sn_name):
        self.__sn_name = sn_name
        self.__newxml = self.__sn_name + ".xml"
        self.xmlpath = "/etc/libvirt/qemu/"
        self.__basexml = os.path.join(self.xml.path, basexml)
        if os.path.exists(self.__basexml) is False:
            print "No %s found, please confirm." % self.__basexml
            sys.exit(1)
        self.__newxml = os.path.join(self.xmlpath, self.__newxml)
        self.__xmltree = ET.parse(self.__basexml)
        self.__rootelement = self.__xmltree.getroot()
        self.__devices = self.__rootelement.find("devices")

    def __modifyNodeName(self, e_node, nodename):
        node = self.rootelement.find(e_node)
        node.text = nodename
        self.__xmltree.write(self.__newxml)

    def modifyDomainName(self):
        self.__modifyNodeName("name", self.__sn_name)

    def modifyUuid(self):
        newuuid = str(uuid.uuid1())
        self.__modifyNodeName("uuid", newuuid)

    def __changeAttr(self, baseattr, subelement, subattr, basevalue, newvalue):
        number = 0
        attrs = self.__devices.findall(baseattr)
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
        self.__xmltree.write(self.__newxml)

    def changeImage(self, img_path, baseimg):
        sn_img = os.path.join(img_path, self.__sn_name)
        baseimg = os.path.join(img_path, baseimg)
        self.__changeAttr("disk", "source", "file", baseimg, sn_img)

    def changeMac(self, basemac, newmac):
        self.__changeAttr("interface", "mac", "address", basemac, newmac)
        

