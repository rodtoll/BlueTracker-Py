__author__ = 'rodtoll'

import dbus
import BluetoothConstants
from BluetoothDevice import BluetoothDevice

class BluetoothAdapter:
    def __init__(self,adapter_full_name):
        self.device_callback = None
        self.dbus_root = dbus.SystemBus()
        self.adapter = dbus.Interface(self.dbus_root.get_object(BluetoothConstants.SERVICE_NAME, adapter_full_name),
                                      BluetoothConstants.BLUEZ_ADAPTER_INTERFACE)
        self.devices = {}
        self.discovering = False

    def set_device_callbacks(self,device_update, device_property_changed):
        self.device_callback = device_update
        self.device_property_changed_callback = device_property_changed

    def device_found(self, address, properties):
        self.device_update_and_create(address, properties)

    def device_removed(self,address):
        device = self.devices[address]
        if device is None:
            print("Specified device not found: "+address)
        else:
            device.set_is_present(False)

    def device_update_and_create(self, address, properties):
        if address in self.devices:
            device = self.devices[address]
            device.set_is_present(True)
            device.update_properties(properties)
        else:
            device = BluetoothDevice(address, properties, self.device_callback, self.device_property_changed_callback)
            self.devices[address] = device

    def power_on(self):
        current_state = self.adapter.GetProperties()

        # Boot adapter if needed
        if BluetoothConstants.BLUEZ_DEVICE_PROPERTY_POWERED in current_state:
            if current_state[BluetoothConstants.BLUEZ_DEVICE_PROPERTY_POWERED] == 0:
                self.adapter.SetProperty(BluetoothConstants.BLUEZ_DEVICE_PROPERTY_POWERED,dbus.Boolean(1))


    def property_changed(self, property, value):
        if property == "Discovering":
            if self.discovering:
                if value == False:
                    self.adapter.StartDiscovery()

    def start_discovery(self):
        self.dbus_root.add_signal_receiver(self.device_found,
                        dbus_interface = BluetoothConstants.BLUEZ_ADAPTER_INTERFACE,
                        signal_name = BluetoothConstants.BLUEZ_ADAPTER_SIGNAL_DEVICE_ADDED)
        self.dbus_root.add_signal_receiver(self.device_removed,
                        dbus_interface = BluetoothConstants.BLUEZ_ADAPTER_INTERFACE,
                        signal_name = BluetoothConstants.BLUEZ_ADAPTER_SIGNAL_DEVICE_GONE)
        self.dbus_root.add_signal_receiver(self.property_changed,
                        dbus_interface = BluetoothConstants.BLUEZ_ADAPTER_INTERFACE,
                        signal_name = BluetoothConstants.BLUEZ_ADAPTER_SIGNAL_PROPERTY_CHANGED)
        self.discovering = True
        self.adapter.StartDiscovery()

    def stop_discovery(self):
        self.discovering = False
        self.adapter.StopDiscovery()
        self.dbus_root.remove_signal_receiver(self.device_found,
                        dbus_interface = BluetoothConstants.BLUEZ_ADAPTER_INTERFACE,
                        signal_name = BluetoothConstants.BLUEZ_ADAPTER_SIGNAL_DEVICE_ADDED)
        self.dbus_root.remove_signal_receiver(self.device_removed,
                        dbus_interface = BluetoothConstants.BLUEZ_ADAPTER_INTERFACE,
                        signal_name = BluetoothConstants.BLUEZ_ADAPTER_SIGNAL_DEVICE_GONE)
        self.dbus_root.remove_signal_receiver(self.property_changed,
                        dbus_interface = BluetoothConstants.BLUEZ_ADAPTER_INTERFACE,
                        signal_name = BluetoothConstants.BLUEZ_ADAPTER_SIGNAL_PROPERTY_CHANGED)



