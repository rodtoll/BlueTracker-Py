__author__ = 'rodtoll'
import time
import subprocess
import sys
import os

if len(sys.argv) < 3:
    print("Usage: ShutdownNode.py <node name> <device name>")
    exit()

if "arm" in os.uname()[4]:
    os.chdir("/home/pi/BlueTracker-Py" )
else:
    os.chdir("/home/rodtoll/PycharmProjects/BlueTracker-Py")

print("Requesting stop of daemon")
result = subprocess.check_output(["python","./BlueTrackerDaemon.py","stop", "./devices."+sys.argv[1]+".cfg"])
print("Result: "+result)
print("Waiting for shutdown")
time.sleep(10)
print("Checking to see if still running...")
if os.path.isfile("bluetracker.pid"):
    print("Doing a hard kill")
    with file('bluetracker.pid') as f: s = f.read()
    result = subprocess.check_output(["kill","-9",s.rstrip('\n')])
    print("Killed process: "+s)
    print("Killing pid file...")
    subprocess.check_output(["rm", "bluetracker.pid"])
    subprocess.check_output(["rm", "bluetracker.pid.lock"])

print("Killing bluetoothd")
result = subprocess.check_output(["killall","-9","bluetoothd"])
print("Result: "+result)
print("Bouncing "+sys.argv[2]+" device")
result = subprocess.check_output(["hciconfig","hci0","down"])
print("Down Result: "+result)
result = subprocess.check_output(["hciconfig","hci0","up"])
print("Up result: "+result)
