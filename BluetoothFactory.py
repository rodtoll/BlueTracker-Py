__author__ = 'rodtoll'

import dbus
import BluetoothConstants
from BluetoothAdapter import BluetoothAdapter
import logging

class BluetoothFactory:
    def __init__(self):
        self.dbus_root = dbus.SystemBus()
        self.manager = dbus.Interface(self.dbus_root.get_object(BluetoothConstants.SERVICE_NAME, "/"),
                                      BluetoothConstants.BLUEZ_MANAGER_INTERFACE)
        adapter_name_list = self.manager.ListAdapters()
        self.adapter_list = {}
        for adapter_full_name in adapter_name_list:
            adapter_short_name = adapter_full_name[adapter_full_name.find("hci"):]
            self.adapter_list[adapter_short_name] = BluetoothAdapter(adapter_full_name)

    def get_adapter(self, adapter_short_name):
        if adapter_short_name in self.adapter_list:
            return self.adapter_list[adapter_short_name]
        else:
            return None

