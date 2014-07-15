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
        self.device_map = {}
        self.device_id = "hci1"
        self.station_id = "station"
        self.config_file_name = config_file_name
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.read_config_file()
        self.init_logger()
        self.dump_config()

        self.pidfile_timeout = 5
        self.isy = ISY.Isy(addr=self.isy_address, userl=self.isy_user, userp=self.isy_password)

    def init_logger(self):
        self.logger = logging.getLogger("DaemonLog")
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.handler = logging.FileHandler(self.logfile_path)
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)


    def read_config_file(self):
        self.device_map = {}
        config_file = open(self.config_file_name, "r")
        # Header specifying device id is next
        config_file.readline()
        self.device_id = config_file.readline()
        self.device_id = self.device_id.rstrip('\n')
        # Header specifying station id is next
        config_file.readline()
        self.station_id = config_file.readline()
        self.station_id = self.station_id.rstrip('\n')
        # Header specifying pid file is next
        config_file.readline()
        self.pidfile_path = config_file.readline()
        self.pidfile_path = self.pidfile_path.rstrip('\n')
        # Header specifying log file is next
        config_file.readline()
        self.logfile_path = config_file.readline()
        self.logfile_path = self.logfile_path.rstrip('\n')
        # Header specifying ISY address is next
        config_file.readline()
        self.isy_address = config_file.readline()
        self.isy_address = self.isy_address.rstrip('\n')
        # Header specifying ISY user is next
        config_file.readline()
        self.isy_user = config_file.readline()
        self.isy_user = self.isy_user.rstrip('\n')
        # Header specifying ISY password is next
        config_file.readline()
        self.isy_password = config_file.readline()
        self.isy_password = self.isy_password.rstrip('\n')
        # Header before the individual device entries
        config_file.readline()
        # read the entries
        for config_line in config_file:
            config_elements = config_line.split(",")
            self.device_map[config_elements[0]] = config_elements[1]
        config_file.close()

    def dump_config(self):
        self.logger.error("Config...")
        self.logger.error("Device ID: "+self.device_id)
        self.logger.error("Station ID: "+self.station_id)
        self.logger.error("PidFile: "+self.pidfile_path)
        self.logger.error("Logfile: "+self.logfile_path)
        self.logger.error("ISY Address: "+self.isy_address)
        self.logger.error("ISY User: "+self.isy_user)
        self.logger.error("ISY Password: "+self.isy_password)

        for address in self.device_map:
            self.logger.error("Device: "+address+" ISY Variable ID: "+self.device_map[address])

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
        self.logger.error(self.station_id+"-[DEVP] Name: ["+device.name+"] Device Update: ["+device.address+"] Present: ["+str(device.get_is_present())+"] RSSI: ["+str(device.rssi)+"] "+action)


    def handle_device_property_changed(self,device):
        self.logger.error(self.station_id+"-[PROP] Name: ["+device.name+"] Device Update: ["+device.address+"] Present: ["+str(device.get_is_present())+"] RSSI: ["+str(device.rssi)+"]")

    def run_daemon(self):
        daemon_runner = runner.DaemonRunner(self)
        daemon_runner.daemon_context.files_preserve=[self.handler.stream]
        daemon_runner.do_action()

    def run(self):

        DBusGMainLoop(set_as_default=True)

        factory = BluetoothFactory()

        self.logger.error("Bluetooth factory created - device:"+self.device_id+" factory "+str(factory))

        adapter = factory.get_adapter(self.device_id)

        if adapter is None:
            raise Exception("Unable to find specified adapter. Fatal error. Adapter- "+self.device_id)

        self.logger.error("Got adapter "+self.device_id)

        adapter.power_on()

        self.logger.error("Powered on")

        adapter.set_device_callbacks(self.handle_device_update,self.handle_device_property_changed)

        self.logger.error("Set device callbacks")
        adapter.start_discovery()
        self.logger.error("discovery started")

        mainloop = GObject.MainLoop()
        mainloop.run()

        adapter.stop_discovery()

if len(sys.argv) > 2:
    config_file_name = sys.argv[2]
else:
    config_file_name = "/home/rodtoll/PycharmProjects/BlueTracker-Py/devices.macbook.cfg"

app = BlueTrackerDaemon(config_file_name)
try:
    if len(sys.argv) > 1 and sys.argv[1] == 'local':
        app.run()
    else:
        app.run_daemon()

except:
    app.logger.exception("Exception running daemon - ")
    sys.exit(1)
