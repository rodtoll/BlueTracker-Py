__author__ = 'rodtoll'

from BluetoothAdapter import BluetoothAdapter
import gobject as GObject
from dbus.mainloop.glib import DBusGMainLoop
import ISY
import sys
from BluetoothFactory import BluetoothFactory

device_id = "hci0"
station_id = "station"

device_map = {}

def read_config(file_name):
    global device_id
    global station_id
    config_file = open(file_name, "r")
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
        print("key: "+config_elements[0])
        print("value: "+config_elements[1])
        device_map[config_elements[0]] = config_elements[1]
    config_file.close()

myisy = ISY.Isy(addr="10.0.1.19", userl="admin", userp="ErgoFlat91")

def handle_device_update(device):
    action = "=> No change"
    if device.address is not None:
        if device.address in device_map:
            variable_id = device_map[device.address]
            action = "=> Updated :"+variable_id
            if device.get_is_present():
                myisy.var_set_value(variable_id, 1)
            else:
                myisy.var_set_value(variable_id, 0)
    print(station_id+"-[DEVP] Name: ["+device.name+"] Device Update: ["+device.address+"] Present: ["+str(device.get_is_present())+"] RSSI: ["+str(device.rssi)+"] "+action)

def handle_device_property_changed(device):
    print(station_id+"-[PROP] Name: ["+device.name+"] Device Update: ["+device.address+"] Present: ["+str(device.get_is_present())+"] RSSI: ["+str(device.rssi)+"]")

if __name__ == "__main__":
    DBusGMainLoop(set_as_default=True)

    if len(sys.argv) > 1:
        config_file_name = sys.argv[1]
    else:
        config_file_name = "./devices.macbook.cfg"

    read_config(config_file_name)

    factory = BluetoothFactory()

    adapter = factory.get_adapter(device_id)
    adapter.set_device_callbacks(handle_device_update,handle_device_property_changed)
    adapter.start_discovery()

    mainloop = GObject.MainLoop()
    mainloop.run()

    adapter.stop_discovery()

    print "Done!"
