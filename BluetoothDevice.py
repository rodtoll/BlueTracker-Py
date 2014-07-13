__author__ = 'rodtoll'

import BluetoothConstants
from datetime import datetime

class BluetoothDevice:
    def __init__(self, path, properties, device_present_callback=None, device_property_callback=None):
        self._is_present = False
        self._path = path
        self._name = ""
        self._rssi = 0
        self._address = None
        self._device_present_callback = device_present_callback
        self._device_property_callback = device_property_callback
        self.set_properties(properties)
        self.set_is_present(True)

    def indicate_device_present_changed(self):
        if self._device_present_callback is not None:
            self._device_present_callback(self)

    def indicate_device_property_changed(self):
        if self._device_property_callback is not None:
            self._device_property_callback(self)

    def set_properties(self,properties):
        if BluetoothConstants.BLUEZ_DEVICE_PROPERTY_NAME in properties:
            self.name = properties[BluetoothConstants.BLUEZ_DEVICE_PROPERTY_NAME]
        if BluetoothConstants.BLUEZ_DEVICE_PROPERTY_ADDRESS in properties:
            self.address = properties[BluetoothConstants.BLUEZ_DEVICE_PROPERTY_ADDRESS]
        if BluetoothConstants.BLUEZ_DEVICE_PROPERTY_RSSI in properties:
            self.rssi = properties[BluetoothConstants.BLUEZ_DEVICE_PROPERTY_RSSI]

    def update_properties(self,properties):
        self.set_properties(properties)
        self.indicate_device_property_changed()

    def get_is_present(self):
        return self._is_present

    def set_is_present(self,new_is_present):
        if self._is_present != new_is_present:
            self._is_present = new_is_present
            self.indicate_device_present_changed()
        if self._is_present:
            self.last_seen = datetime.now()


    def get_last_seen(self):
        return self._last_seen
    def set_last_seen(self, last_seen):
        self._last_seen = last_seen

    last_seen = property(get_last_seen,set_last_seen)

    def get_path(self):
        return self._path
    def set_path(self,path):
        self._path = path

    path = property(get_path, set_path)

    def get_name(self):
        return self._name
    def set_name(self,name):
        self._name = name

    name = property(get_name, set_name)

    def get_rssi(self):
        return self._rssi
    def set_rssi(self,rssi):
        self._rssi = rssi

    rssi = property(get_rssi, set_rssi)

    def get_address(self):
        return self._address
    def set_address(self, address):
        self._address = address

    address = property(get_address, set_address)

    def get_update_callback(self):
        return self._update_callback
    def set_update_callback(self, update_callback):
        self._update_callback = update_callback

    update_callback = property(get_update_callback, set_update_callback)