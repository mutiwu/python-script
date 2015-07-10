import pexpect
import sys

ip = "10.66.10.63"
dire = "/home/"
file_name = "easy_get.py"
user = "root"
pwd = "redhat"
path = ip + ":" + dire
p1 = r"(yes\/no)\?"
p2 = r"password\:"
test = "scp %s -l %s %s" % (file_name, user, path)
print test
child = pexpect.spawn("scp %s -l %s %s" % (file_name, user, path))
child.logfile = sys.stdout
index = child.expect([p1, p2], timeout=-1)
if index == 0:
    child.sendline("yes")
    child.expect(p2, timeout=-1)
    child.sendline(pwd)
if index == 1:
    child.sendline(pwd)

child.before
child.after
