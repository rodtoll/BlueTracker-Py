__author__ = 'rodtoll'

from BluetoothAdapter import BluetoothAdapter
import gobject as GObject
from dbus.mainloop.glib import DBusGMainLoop
import ISY
import sys

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
    station_name = config_file.readline()
    station_name = station_name.rstrip('\n')
    # Header before the individual device entries
    config_file.readline()
    # read the entries
    for config_line in config_file:
        config_elements = config_line.split(",")
        device_map[config_elements[0]] = config_elements[1]
    config_file.close()

myisy = ISY.Isy(addr="10.0.1.19", userl="admin", userp="ErgoFlat91")

def handle_device_update(device):
    print(station_id+"- Name: ["+device.name+"] Device Update: ["+device.address+"] Present: ["+str(device.is_present)+"] RSSI: ["+str(device.rssi)+"]")
    if device.address is not None:
        if device.address in device_map:
            variable_id = device_map[device.address]
            print("> Updated variable: "+variable_id)
            if device.is_present:
                myisy.var_set_value(variable_id, 1)
            else:
                myisy.var_set_value(variable_id, 0)

if __name__ == "__main__":
    DBusGMainLoop(set_as_default=True)

    if len(sys.argv) > 1:
        config_file_name = sys.argv[1]
    else:
        config_file_name = "./devices.macbook.cfg"

    read_config(config_file_name)

    adapter = BluetoothAdapter(device_id, handle_device_update)
    adapter.start_discovery()

    mainloop = GObject.MainLoop()
    mainloop.run()

    adapter.stop_discovery()

    print "Done!"
