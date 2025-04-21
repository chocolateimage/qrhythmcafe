#!/usr/bin/python3
import sys

newversion = sys.argv[1]

with open("deb/qrhythmcafe/DEBIAN/control", "r+") as f:
    lines = f.read().split("\n")
    for i, v in enumerate(lines):
        if v.startswith("Version: "):
            lines[i] = "Version: " + newversion
    f.seek(0)
    f.write("\n".join(lines))
    f.truncate()

with open("deb/qrhythmcafe.desktop", "r+") as f:
    lines = f.read().split("\n")
    for i, v in enumerate(lines):
        if v.startswith("Version="):
            lines[i] = "Version=" + newversion
    f.seek(0)
    f.write("\n".join(lines))
    f.truncate()

with open("utils.py", "r+") as f:
    lines = f.read().split("\n")
    for i, v in enumerate(lines):
        if v.startswith("VERSION_NUMBER = "):
            lines[i] = 'VERSION_NUMBER = "' + newversion + '"'
    f.seek(0)
    f.write("\n".join(lines))
    f.truncate()
