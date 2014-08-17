__author__ = 'rodtoll'
import time
import subprocess
import sys
import os

if len(sys.argv) < 2:
    print("Usage: StartupNode.py <node name>")
    exit()

if "arm" in os.uname()[4]:
    os.chdir("/home/pi/BlueTracker-Py" )
else:
    os.chdir("/home/rodtoll/PycharmProjects/BlueTracker-Py")

print("Launching daemon")
result = subprocess.check_output(["python","./BlueTrackerDaemon.py", "start","./devices."+sys.argv[1]+".cfg"])
print("Launch result "+result)