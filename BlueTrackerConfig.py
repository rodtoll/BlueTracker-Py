__author__ = 'rodtoll'

import json
import netifaces
import requests
import sys

class BlueTrackerConfig():
    def __init__(self):
        self.device_map = {}
        self.fields = ['master_server', 'master_password']
        self.ping_map = []

    def dump_config(self, logger_source):
        logger_source.error('CONFIG DUMP:')
        for field in self.fields:
            logger_source.error(field + ": " + str(getattr(self, field)))
        if hasattr(self, 'ping_sleep_period'):
            logger_source.error("Ping Service:")
            logger_source.error("- Sleep Period: "+str(self.ping_sleep_period)+"s")
            logger_source.error("- Timeout: "+str(self.ping_timeout)+"s")
            logger_source.error("- Retries: "+str(self.ping_retries))
            logger_source.error("- Retry Pause: "+str(self.ping_retry_pause)+"s")
        if hasattr(self, 'garage_pin_number'):
            logger_source.error("Garage Service:")
            logger_source.error("- Pin: "+str(self.garage_pin_number))
        if hasattr(self, "rht_sleep"):
            logger_source.error("RHT Service:")
            logger_source.error("- Sleep: "+str(self.rht_sleep)+"s")
            logger_source.error("- Base Address: "+self.rht_base_address)

    def load_node_from_master(self, logger_source):
        logger_source.error("Loading config from the master server")
        if 'wlan0' in netifaces.interfaces():
            local_address = netifaces.ifaddresses('wlan0')[2][0].get('addr')
        else:
            local_address = netifaces.ifaddresses('eth0')[2][0].get('addr')
        logger_source.error("Local address is: "+local_address)
        request_headers = {'content-length' : '0', 'x-troublex3-bluetracker-auth' : self.master_password }
        request_uri = self.master_server + '/_ah/api/tracker/v1/node/' + local_address
        try:
            logger_source.error("Loading from master server via: "+request_uri)
            result = requests.get(request_uri, headers = request_headers)
            server_config_data = result.json()
            self.station_id = server_config_data['nodeId']
            self.nodeType = server_config_data['nodeType']
            self.device_id = server_config_data['deviceId']
            if 'pingService' in server_config_data:
                logger_source.error("Loading the ping service")
                self.ping_sleep_period = server_config_data['pingService']['sleepPeriod']
                self.ping_timeout = server_config_data['pingService']['timeout']
                self.ping_retries = server_config_data['pingService']['retries']
                self.ping_retry_pause = server_config_data['pingService']['retryPause']
            if 'garageService' in server_config_data:
                logger_source.error("Loading the garage service")
                self.garage_pin_number = server_config_data['garageService']['pin']
            if 'rhtService' in server_config_data:
                logger_source.error("Loading the RHT service")
                self.rht_sleep = server_config_data['rhtService']['sleep']
                self.rht_base_address = server_config_data['rhtService']['baseAddress']
        except:
            print("Error getting config from master. Config: "+request_uri)
            print(sys.exc_info()[0])

    def load_devices_from_master(self, logger_source):
        logger_source.error("Loading device list from the master server")
        request_headers = {'content-length' : '0', 'x-troublex3-bluetracker-auth' : self.master_password }
        request_uri = self.master_server + '/_ah/api/tracker/v1/device'
        try:
            logger_source.error("Loading device from master server via: "+request_uri)
            result = requests.get(request_uri, headers = request_headers)
            server_config_data = result.json()
            device_list = server_config_data['items']
            for device in device_list:
                if device['deviceType'] == 'Ping':
                    logger_source.error("Adding device: "+device['address'])
                    self.ping_map.append(device['address'])
        except:
            print("Error getting config from master. Config: "+request_uri)
            print(sys.exc_info()[0])


    def load(self, file_name):
        config_file = open(file_name, "r")
        config_data = json.load(config_file)
        for field in self.fields:
            if field in config_data:
                setattr(self, field, config_data.get(field))
            else:
                setattr(self, field, "")
        config_file.close()

    def set_config(self, field_name, value_to_set):
        setattr(self, field_name, value_to_set)
