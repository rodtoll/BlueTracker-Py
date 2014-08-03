__author__ = 'rodtoll'

import cherrypy

class GarageDoorService(object):
    @cherrypy.expose
    def index(self):
#        press_garage_door_button(4)
        return "<html><body>Opened</body></html>"

cherrypy.config.update({'server.socket_host': '0.0.0.0'})
cherrypy.tree.mount(GarageDoorService(),'/')
#cherrypy.quickstart(GarageDoorService())