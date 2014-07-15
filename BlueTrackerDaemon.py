__author__ = 'rodtoll'

import logging
import time
from daemon import runner
import gobject as GObject
from dbus.mainloop.glib import DBusGMainLoop
import sys
from BluetoothFactory import BluetoothFactory
import ISY
import BluetoothConstants

class BlueTrackerDaemon():

    def __init__(self, config_file_name):
        x = 1
        self.device_map = {}
        self.device_id = "hci1"
        self.station_id = "station"
        self.config_file_name = config_file_name
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'

        self.pidfile_path =  '/home/rodtoll/PycharmProjects/BlueTracker-Py/bluetracker.pid'
        self.pidfile_timeout = 5
        self.isy = ISY.Isy(addr="10.0.1.19", userl="admin", userp="ErgoFlat91")

    def read_config_file(self):
        self.device_map = {}
        config_file = open(self.config_file_name, "r")
        # Header specifying device id is next
        config_file.readline()
        device_id = config_file.readline()
        device_id = device_id.rstrip('\n')
        # Header specifying station id is next
        config_file.readline()
        station_id = config_file.readline()
        station_id = station_id.rstrip('\n')
        # Header before the individual device entries
        config_file.readline()
        # read the entries
        for config_line in config_file:
            config_elements = config_line.split(",")
            logger.error("key: "+config_elements[0])
            logger.error("value: "+config_elements[1])
            self.device_map[config_elements[0]] = config_elements[1]
        config_file.close()

    def handle_device_update(self,device):
        action = "=> No change"
        if device.address is not None:
            if device.address in self.device_map:
                variable_id = self.device_map[device.address]
                action = "=> Updated :"+variable_id
                if device.get_is_present():
                    self.isy.var_set_value(variable_id, 1)
                else:
                    self.isy.var_set_value(variable_id, 0)
        logger.error(self.station_id+"-[DEVP] Name: ["+device.name+"] Device Update: ["+device.address+"] Present: ["+str(device.get_is_present())+"] RSSI: ["+str(device.rssi)+"] "+action)


    def handle_device_property_changed(self,device):
        logger.error(self.station_id+"-[PROP] Name: ["+device.name+"] Device Update: ["+device.address+"] Present: ["+str(device.get_is_present())+"] RSSI: ["+str(device.rssi)+"]")

    def run(self):

        DBusGMainLoop(set_as_default=True)

        self.read_config_file()

        logger.error("Read config file")

        factory = BluetoothFactory()

        logger.error("Bluetooth factory created - device:"+self.device_id+" factory "+str(factory))

        adapter = factory.get_adapter(self.device_id)

        logger.error("Got adapter "+self.device_id)

        adapter.power_on()

        logger.error("Powered on")

        adapter.set_device_callbacks(self.handle_device_update,self.handle_device_property_changed)

        logger.error("Set device callbacks")
        adapter.start_discovery()
        logger.error("discovery started")

        mainloop = GObject.MainLoop()
        mainloop.run()

        adapter.stop_discovery()

if len(sys.argv) > 2:
    config_file_name = sys.argv[2]
else:
    config_file_name = "/home/rodtoll/PycharmProjects/BlueTracker-Py/devices.macbook.cfg"

app = BlueTrackerDaemon(config_file_name)
logger = logging.getLogger("DaemonLog")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/home/rodtoll/PycharmProjects/BlueTracker-Py/bluetracker.log")
handler.setFormatter(formatter)
logger.addHandler(handler)

if len(sys.argv) > 1 and sys.argv[1] == 'local':
    app.run()
else:
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.daemon_context.files_preserve=[handler.stream]
    daemon_runner.do_action()