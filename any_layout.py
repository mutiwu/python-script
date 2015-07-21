import re
import sys
import commands

iface = sys.argv[1]
cmd = "cat /sys/class/net/%s/device/features" % iface
status, output = commands.getstatusoutput(cmd)
print "# TOTAL %s bits." % len(output)
result = []
for i in range(len(output)):
    result.append(("Bit %s" % i, "value %s" % output[i]))
print "\n# They are:\n%s" % result
for name, value in result:
    if name == "Bit %s" % "26":
        print "\n# The 26th bit's  %s" % value

