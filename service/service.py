from twisted.internet.defer import inlineCallbacks
from twisted.application.internet import ClientService, backoffPolicy
from twisted.logger import Logger


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
