__author__ = 'rodtoll'

import logging
import time
from daemon import runner
import gobject as GObject
from dbus.mainloop.glib import DBusGMainLoop
import sys
from BluetoothFactory import BluetoothFactory
import requests
import platform
import BluetoothConstants
from BlueTrackerConfig import BlueTrackerConfig
from PingTracker import PingTrackerManager
from RHTDataCollector import RHTDataCollector
import urllib
import os

class BlueTrackerDaemon():

    def __init__(self, config_file_name):
        self.config_file_name = config_file_name
        self.init_paths()
        self.init_logger()
        self.read_config_file()
        self.dump_config()
        self.pidfile_timeout = 5

    def init_paths(self):
        self.pidfile_path = os.getcwd()+"/bluetracker.pid"
        self.logfile_path = os.getcwd()+"/bluetracker.log"
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'

    def init_logger(self):
        self.logger = logging.getLogger("DaemonLog")
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.handler = logging.FileHandler(self.logfile_path)
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)

    def read_config_file(self):
        self.config = BlueTrackerConfig()
        self.config.load(self.config_file_name)
        self.config.load_node_from_master(self.logger)
        self.config.load_devices_from_master(self.logger)

    def dump_config(self):
        self.config.dump_config(self.logger)

    def handle_device_update(self,device):
        action = "=> No change"
        self.logger.error(self.config.station_id+"-[DEVP] Name: ["+device.name+"] Device Update: ["+device.address+"] Present: ["+str(device.get_is_present())+"] RSSI: ["+str(device.rssi)+"] "+action)
        self.send_reading_to_master(device.address, device.rssi)

    def handle_device_property_changed(self,device):
        self.logger.error(self.config.station_id+"-[PROP] Name: ["+device.name+"] Device Update: ["+device.address+"] Present: ["+str(device.get_is_present())+"] RSSI: ["+str(device.rssi)+"]")
        self.send_reading_to_master(device.address, device.rssi)

    def run_daemon(self):
        daemon_runner = runner.DaemonRunner(self)
        daemon_runner.daemon_context.files_preserve=[self.handler.stream]
        daemon_runner.do_action()

    def send_heartbeat(self):
        self.logger.error("### Heartbeat sent")
        self.send_heartbeat_to_master()
        return True

    def send_reading_to_master(self, address, signal_strength):
        request_headers = {'content-length' : '0', 'x-troublex3-bluetracker-auth' : self.config.master_password}
        request_params = { 'readingValue' : str(signal_strength), 'node': self.config.station_id }
        address = urllib.quote(address)

        request_uri = self.config.master_server + '/_ah/api/tracker/v1/device/' + address + '/reading'

        try:
            requests.post(request_uri, params = request_params, headers = request_headers)
        except:
            self.logger.error("Failed loading specified URI for update")
            self.logger.error(self.config.master_server + '/_ah/api/tracker/v1/node/' + address + '/reading' )
            self.logger.error(request_params)

    def send_heartbeat_to_master(self):
        request_headers = {'content-length': '0', 'x-troublex3-bluetracker-auth' : self.config.master_password}
        try:
            requests.put(self.config.master_server + '/_ah/api/tracker/v1/node/' + self.config.station_id, headers = request_headers)
        except:
            self.logger.error("Failed loading specified URI for heartbeat")
            self.logger.error(self.config.master_server + '/_ah/api/tracker/v1/node/' + self.config.station_id )

    def start_ping_tracker(self):
        if hasattr(self.config,"ping_sleep_period"):
            self.logger.error("Starting ping tracker...")
            self.ping_tracker = PingTrackerManager(self.config.ping_sleep_period, self.config.ping_timeout,self.config.ping_retries,self.config.ping_retry_pause, self.logger, self.send_reading_to_master, self.config.ping_map)

    def start_temp_reader(self):
        if hasattr(self.config,'rht_base_address'):
            self.logger.error("Starting RHT reader...")
            self.rht_reader = RHTDataCollector(self.config.rht_base_address,self.logger, self.send_reading_to_master, self.config.rht_sleep)
            self.rht_reader.start() 

    def run(self):

        DBusGMainLoop(set_as_default=True)

        if hasattr(self.config, "garage_pin_number"):
            from GarageDoorDBusService import GarageDoorDBusService
            self.garage_service = GarageDoorDBusService(self.config.garage_pin_number)

        factory = BluetoothFactory()

        self.logger.error("Bluetooth factory created - device:"+self.config.device_id+" factory "+str(factory))

        adapter = factory.get_adapter(self.config.device_id)

        if adapter is None:
            raise Exception("Unable to find specified adapter. Fatal error. Adapter- "+self.config.device_id)

        self.logger.error("Got adapter "+self.config.device_id)

        adapter.power_on()

        self.logger.error("Powered on")

        adapter.set_device_callbacks(self.handle_device_update,self.handle_device_property_changed)

        self.start_ping_tracker()
        self.start_temp_reader()

        self.logger.error("Set device callbacks")
        adapter.start_discovery()
        self.logger.error("discovery started")
        self.send_heartbeat()
        self.logger.error("initial heartbeat sent")


        event_id = GObject.timeout_add(240000,self.send_heartbeat)
        mainloop = GObject.MainLoop()
        mainloop.run()
        GObject.source_remove(event_id)

        adapter.stop_discovery()

    def dump_status(self):
        print("Status of BlueTracker on ISY:")


if len(sys.argv) > 2:
    config_file_name = sys.argv[2]
else:
    config_file_name = "/home/rodtoll/PycharmProjects/BlueTracker-Py/devices.macbook.cfg"

app = BlueTrackerDaemon(config_file_name)
try:
    if len(sys.argv) > 1 and sys.argv[1] == 'local':
        app.run()
    elif len(sys.argv) > 1 and sys.argv[1] == "status":
        app.dump_status()
    else:
        app.run_daemon()

except:
    app.logger.exception("Exception running daemon - ")
    sys.exit(1)
