from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import clientFromString
from twisted.internet.serialport import SerialPort
from twisted.application import service, strports
from twisted.application.internet import ClientService, backoffPolicy
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from twisted.logger import Logger

from autobahn.twisted.resource import WebSocketResource, WSGIRootResource
from mqtt.client.factory import MQTTFactory

import settings
from protocol import SerialToWebsocketServerFactory, SerialProtocol
from web import create_app


class MQTTService(ClientService):

    name = 'mqtt-client'

    log = Logger()

    def __init__(self, endpoint, factory):
        super(MQTTService, self).__init__(endpoint, factory, retryPolicy=backoffPolicy())

    def startService(self):
        self.whenConnected().addCallback(self.connectToBroker)
        super(MQTTService, self).startService()

    @inlineCallbacks
    def connectToBroker(self, protocol):
        self.protocol = protocol
        self.protocol.onDisconnection = self.onDisconnect
        try:
            yield self.protocol.connect('serialmon', keepalive=60)
        except Exception as e:
            self.log.error('Connecting to MQTT broker raised {excp!s}', excp=e)
        else:
            self.log.info('Connected to MQTT broker')

    def onDisconnect(self, reason):
        self.whenConnected().addCallback(self.connectToBroker)

    def publish(self, message):
        return self.protocol.publish(topic='esp8266/serial', message=message, qos=1)


def make_service(reactor=None):

    if reactor is None:
        from twisted.internet import reactor

    # create root service
    root = service.MultiService()

    # MQTT
    mqttFactory = MQTTFactory(profile=MQTTFactory.PUBLISHER)
    mqttEndpoint = clientFromString(reactor, settings.MQTT_BROKER_URI)
    mqttService = MQTTService(mqttEndpoint, mqttFactory)
    mqttService.setServiceParent(root)

    # create a Twisted Web resource for our WebSocket server
    wsFactory = SerialToWebsocketServerFactory(settings.WS_URI)
    wsResource = WebSocketResource(wsFactory)

    # create a Twisted Web WSGI resource for our Flask server
    wsgiResource = WSGIResource(reactor, reactor.getThreadPool(), create_app())

    # create a root resource serving everything via WSGI/Flask, but
    # the path "/ws" served by our WebSocket stuff
    rootResource = WSGIRootResource(wsgiResource, {settings.WS_PATH: wsResource})

    # create a Twisted Web Site
    site = Site(rootResource)

    # create service and add it to root
    wsService = strports.service(settings.SERVICE_URI, site)
    wsService.setName('web')
    wsService.setServiceParent(root)

    # serial port monitor
    SerialPort(SerialProtocol(wsFactory, mqttService),
        settings.SERIAL_PORT, reactor, baudrate=settings.SERIAL_BAUDRATE)

    return root
