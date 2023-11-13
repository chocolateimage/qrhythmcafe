#!/usr/bin/python3
import sys

newversion = sys.argv[1]

with open("deb/qrhythmcafe/DEBIAN/control","r+") as f:
    l = f.read().split("\n")
    for i,v in enumerate(l):
        if v.startswith("Version: "):
            l[i] = "Version: " + newversion
    f.seek(0)
    f.write("\n".join(l))
    f.truncate()

with open("deb/qrhythmcafe.desktop","r+") as f:
    l = f.read().split("\n")
    for i,v in enumerate(l):
        if v.startswith("Version="):
            l[i] = "Version=" + newversion
    f.seek(0)
    f.write("\n".join(l))
    f.truncate()

with open("utils.py","r+") as f:
    l = f.read().split("\n")
    for i,v in enumerate(l):
        if v.startswith("VERSION_NUMBER = "):
            l[i] = "VERSION_NUMBER = \"" + newversion + "\""
    f.seek(0)
    f.write("\n".join(l))
    f.truncate()