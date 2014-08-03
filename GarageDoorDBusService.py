__author__ = 'rodtoll'

import dbus
import dbus.service
import GarageDoor

class GarageDoorDbusService(dbus.service.Object):
    def __init__(self,pin_number):
        self.pin_number = pin_number
        bus_name = dbus.service.BusName('org.troublex3.garagedoorservice', bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, '/org/troublex3/garagedoorservice')

    @dbus.service.method('org.troublex3.garagedoorservice')
    def toggler_door(self):
        GarageDoor.press_garage_door_button(int(self.pin_number))
        return "Press sent"