__author__ = 'rodtoll'

import dbus
import BluetoothConstants
from BluetoothDevice import BluetoothDevice

class BluetoothAdapter:
    def __init__(self,adapter_id, device_callback):
        self.device_callback = device_callback
        self.dbus_root = dbus.SystemBus()
        self.manager = dbus.Interface(self.dbus_root.get_object(BluetoothConstants.SERVICE_NAME, "/"),
                                      BluetoothConstants.OBJECT_MANAGER_OBJECT)
        self.adapter_id = adapter_id
        objects = self.manager.GetManagedObjects()
        for path, ifaces in objects.iteritems():
            adapter = ifaces.get(BluetoothConstants.ADAPTER_INTERFACE)
            if adapter is None:
                continue
            if path.endswith(adapter_id):
                self.adapter_Object = self.dbus_root.get_object(BluetoothConstants.SERVICE_NAME, path)
                break
        if self.adapter_Object is None:
            raise Exception("Could not find adapter specified: "+self.adapter_id)
        self.adapter = dbus.Interface(self.adapter_Object, dbus_interface=BluetoothConstants.ADAPTER_INTERFACE)
        self.devices = {}
        self.device_initial_discovery()

    def device_found(self, path, interfaces):
        properties = interfaces[BluetoothConstants.DEVICE_INTERFACE]
        self.device_update_and_create(path, properties)

    def device_update_and_create(self, path, properties):
        if not properties:
            return
        if path in self.devices:
            device = self.devices[path]
            device.update_properties(properties)
        else:
            device = BluetoothDevice(path, properties, self.device_callback)
            self.devices[path] = device

    def device_removed(self, path, interfaces):
        if path in self.devices:
            self.devices[path].set_is_present(False)

    def device_changed(self,interface, changed, invalidated, path):
        self.device_update_and_create(path, changed)

    def device_initial_discovery(self):
        objects = self.manager.GetManagedObjects()
        for path, interfaces in objects.iteritems():
            if BluetoothConstants.DEVICE_INTERFACE in interfaces:
                self.device_found(path, interfaces)
        print("initial discovery complete")

    def start_discovery(self):
        self.dbus_root.add_signal_receiver(self.device_found,
                        dbus_interface = BluetoothConstants.OBJECT_MANAGER_OBJECT,
                        signal_name = BluetoothConstants.SIGNAL_INTERFACE_ADDED)
        self.dbus_root.add_signal_receiver(self.device_removed,
                        dbus_interface = BluetoothConstants.OBJECT_MANAGER_OBJECT,
                        signal_name = BluetoothConstants.SIGNAL_INTERFACE_REMOVED)
        self.dbus_root.add_signal_receiver(self.device_changed,
                        dbus_interface = BluetoothConstants.PROPERTY_INTERFACE,
                        signal_name = BluetoothConstants.SIGNAL_PROPERTY_CHANGED,
                        arg0 = BluetoothConstants.DEVICE_INTERFACE,
                        path_keyword = "path")

        self.adapter.StartDiscovery()

    def stop_discovery(self):
        self.adapter.StopDiscovery()
        self.dbus_root.remove_signal_receiver(self.device_found,
                        dbus_interface = BluetoothConstants.OBJECT_MANAGER_OBJECT,
                        signal_name = BluetoothConstants.SIGNAL_INTERFACE_ADDED)
        self.dbus_root.remove_signal_receiver(self.device_removed,
                        dbus_interface = BluetoothConstants.OBJECT_MANAGER_OBJECT,
                        signal_name = BluetoothConstants.SIGNAL_INTERFACE_REMOVED)
        self.dbus_root.remove_signal_receiver(self.device_changed,
                        dbus_interface = BluetoothConstants.PROPERTY_INTERFACE,
                        signal_name = BluetoothConstants.SIGNAL_PROPERTY_CHANGED,
                        arg0 = BluetoothConstants.DEVICE_INTERFACE,
                        path_keyword = "path")

    def set_device_callback(self, device_callback):
        self.device_callback = device_callback


