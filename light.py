#! /usr/bin/python
import time
import subprocess
from subprocess import Popen
import cgi, cgitb
import sys
cgitb.enable()

form = cgi.FieldStorage()

insteon = "/home/anthony/eng/lightcontrol-c/insteon"

ui = "yes"
if "ui" in form:
    ui = form["ui"].value

print "Content-Type: text/html\n\n"

device = ""
if ("device" in form):
    device = form["device"].value
else:
    exit()

command = ""
if ("cmd" in form):
    command = form["cmd"].value
else:
    exit()

level = ""
if ("level" in form):
    level = form["level"].value

pipe = Popen(insteon + " " + device + " " + command + " " + level, shell=True, bufsize=60096, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print >> sys.stderr, pipe.stderr.read()
print >> sys.stdout, pipe.stdout.read()

exit()
