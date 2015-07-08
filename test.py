# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 21:29:58 2015

@author: qian
"""

import time
import commands

starttime = time.time()
commands.getstatusoutput("ping 192.168.122.37 -c 10")
endtime = time.time()
print endtime - starttime