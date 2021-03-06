#!/usr/bin/python

import os
import sys
import re
import subprocess

os.chdir(os.path.dirname(os.path.abspath(__file__)))

packages = []
casks = []
brewData = open("../Brewfile", "r").readlines()
for command in brewData:
    if (len(command.strip()) == 0):
        continue
    if (command.strip()[0] == "#"):
        continue
    if (command.strip().startswith("brew '")):
        pkg = re.match(r"brew '([^']*)'", command)
        packages.append(pkg.group(1))
    elif (command.strip().startswith("cask '")):
        cask = re.match(r"cask '([^']*)'", command)
        casks.append(cask.group(1))


deps = subprocess.check_output(["/usr/local/bin/brew", "deps", "--union"] + packages)

erred = False
for dep in deps.split("\n"):
    if dep == "python":
        sys.stderr.write("WARNING: this Brewfile will result in Homebrew Python.\n")
        erred = True
    if dep == "node":
        sys.stderr.write("WARNING: this Brewfile will result in Homebrew Node.js.\n")
        erred = True

FNULL = open(os.devnull, "w")
for pkg in packages:
    infoStatus = subprocess.call(["/usr/local/bin/brew", "info", pkg], stdout=FNULL, stderr=FNULL)
    if (infoStatus != 0):
        sys.stderr.write("WARNING: problematic package: %s\n" % pkg)
        erred = True
for cask in casks:
    infoStatus = subprocess.call(["/usr/local/bin/brew", "cask", "info", cask], stdout=FNULL, stderr=FNULL)
    if (infoStatus != 0):
        sys.stderr.write("WARNING: problematic cask: %s\n" % cask)
        erred = True
    rawCask = subprocess.check_output(["/usr/local/bin/brew", "cask", "cat", cask])
    if "installer manual:" in rawCask:
        sys.stdout.write("INFO: %s cask requires a manual installation step.\n" % cask)

if (erred):
    sys.exit(1)

