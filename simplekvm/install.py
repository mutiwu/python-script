#!/usr/bin/env python
# coding=utf-8

import os
import stat
import shutil

syspath = '/usr/bin'
sharepath = '/usr/share/simplekvm'
filename = 'simplekvm'
wfilename = 'w' + filename
novncfiles = 'noVNC'
bkvncfile = 'bakvnc'
dstvncpath = os.path.abspath(os.path.join(sharepath, novncfiles))
dstbkvncpath = os.path.abspath(os.path.join(sharepath, bkvncfile))
execfile = os.path.join(syspath, filename)
wexecfile = os.path.join(syspath, wfilename)
toexefile = os.path.abspath(os.path.join(os.path.curdir, filename))
wtoexefile = os.path.abspath(os.path.join(os.path.curdir, wfilename))
novncdir = os.path.abspath(os.path.join(os.path.curdir, novncfiles))


if __name__ == "__main__":

    if not os.path.isdir(syspath):
        print '%s does not exist' % syspath
        os._exit(1)
    for file in execfile, wexecfile:
        if os.path.isfile(file):
            bk = file + '.bak'
            backupfile = os.path.join(syspath, bk)
            print("%s already exist, will backup it as %s"
                  % (file, bk))
            if os.path.isfile(backupfile):
                os.remove(backupfile)
            os.rename(file, backupfile)
            os.chmod(backupfile, stat.S_IREAD)
    for file in toexefile, wtoexefile:
        if not os.path.isfile(file):
            print "No %s found here, the script will not work." % file
            os._exit(1)
        if not os.path.isdir(novncdir):
            print "No %s found here, the script will not work." % novncdir
            os._exit(1)
    if not os.path.isdir(sharepath):
        print '%s does not exist, creating it' % sharepath
        os.makedirs(sharepath)

    if os.path.isdir(dstvncpath):
        print "%s already exist, will backup it" % dstvncpath
        if os.path.isdir(dstbkvncpath):
            shutil.rmtree(dstbkvncpath)
        os.rename(dstvncpath, dstbkvncpath)

    shutil.copyfile(toexefile, execfile)
    os.chmod(execfile, stat.S_IRWXU)
    shutil.copyfile(wtoexefile, wexecfile)
    os.chmod(wexecfile, stat.S_IRWXU)
    shutil.copytree(novncdir, dstvncpath)
