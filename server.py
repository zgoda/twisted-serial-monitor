import os
import sys

from twisted.python import log
from twisted.logger import Logger
from twisted.application import strports, service
from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString
from twisted.internet.serialport import SerialPort
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from autobahn.twisted.resource import WebSocketResource, WSGIRootResource
from mqtt.client.factory import MQTTFactory

from web import create_app
from service import settings
from service.service import MQTTService
from service.protocol import SerialProtocol, SerialToWebsocketServerFactory


logger = Logger()


if __name__ == "__main__":
    debug = os.environ.get('DEBUG')
    if not debug:
        log.startLogging(sys.stdout)

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

    application = service.Application('serial-router')
    root.setServiceParent(application)
    root.startService()

    # serial port monitor
    SerialPort(SerialProtocol(wsFactory, mqttService),
        settings.SERIAL_PORT, reactor, baudrate=settings.SERIAL_BAUDRATE)

    # run everything
    reactor.run()
