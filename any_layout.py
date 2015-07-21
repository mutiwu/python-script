import re
import sys
import commands

iface = sys.argv[1]
any_layout_bit = "27"
cmd = "cat /sys/class/net/%s/device/features" % iface
status, output = commands.getstatusoutput(cmd)
print "# TOTAL %s bits." % len(output)
result = []
for i in range(len(output)):
    result.append(("Bit %s" % i, "value %s" % output[i]))
print "\n# They are:\n%s" % result
for name, value in result:
    if name == "Bit %s" % any_layout_bit:
        print "\n# The 27th bit's  %s" % value

