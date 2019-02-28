#!/usr/bin/python3
'''
The tool will print the library path of Python, and
also check whether `argparse.py` is inside.
'''

from sys import path
from os import path as ospath

libPathList = ""
for libpath in path:
  if ospath.isdir(libpath) and ospath.exists(ospath.join(libpath, "argparse.py")):
    libPathList += libpath + " "

print(libPathList[:-1])
