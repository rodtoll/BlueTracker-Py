__author__ = 'rodtoll'

import json

class BlueTrackerConfig():
    def __init__(self):
        self.device_map = {}
        self.fields = ['isy_address', 'isy_password', 'isy_heartbeat', 'device_id', 'station_id', 'pid_file',
                       'log_file', 'master_server', 'isy_username', 'master_password', 'garage_pin_number']

    def dump_config(self, logger_source):
        logger_source.error('CONFIG DUMP:')
        for field in self.fields:
            logger_source.error(field + ": " + getattr(self, field))
        logger_source.error('Devices: ')
        for address in self.device_map:
            logger_source.error("Device: "+address+" ISY Variable ID: "+self.device_map[address])

    def load(self, file_name):
        config_file = open(file_name, "r")
        config_data = json.load(config_file)
        for field in self.fields:
            if field in config_data:
                setattr(self, field, config_data.get(field))
            else:
                setattr(self, field, "")
        config_device_map = config_data.get('devices')
        for device_name in config_device_map:
            self.device_map[device_name] = config_device_map.get(device_name)
        config_file.close()
