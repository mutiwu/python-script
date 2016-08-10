#!/usr/bin/env python
# coding=utf-8
import commands
import sys

for i in range(1, 31):
    irqs = range(35, 65)
    status, output = commands.getstatusoutput("echo %s > /proc/irq/%s/smp_affinity" %(i, irqs[i]) )
    if status:
        print output
        sys.exit(1)
    status, output = commands.getstatusoutput("cat /proc/irq/%s/smp_affinity" %irqs[i])

