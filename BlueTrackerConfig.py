__author__ = 'rodtoll'

import json

class BlueTrackerConfig():
    def __init__(self):
        self.device_map = {}
        self.ping_map = []
        self.fields = ['isy_address', 'isy_password', 'isy_heartbeat', 'device_id', 'station_id', 'pid_file',
                       'log_file', 'master_server', 'isy_username', 'master_password', 'garage_pin_number',
                       'ping_sleep_period', 'ping_timeout', 'ping_retries', 'ping_retry_pause',
                       'rht_base_address', 'rht_sleep']

    def dump_config(self, logger_source):
        logger_source.error('CONFIG DUMP:')
        for field in self.fields:
            logger_source.error(field + ": " + str(getattr(self, field)))
        logger_source.error('Devices: ')
        for address in self.device_map:
            logger_source.error("Device: "+address+" ISY Variable ID: "+self.device_map[address])
        logger_source.error("Ping Devices:")
        for address in self.ping_map:
            logger_source.error("Device: "+address)

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
        ping_device_map = config_data.get('pingdevices')
        for ping_device in ping_device_map:
            self.ping_map.append(ping_device)
        config_file.close()
