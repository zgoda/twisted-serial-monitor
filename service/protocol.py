from twisted.internet.protocol import Protocol
from twisted.logger import Logger
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol


class SerialProtocol(Protocol):

    log = Logger()

    def __init__(self, wsFactory, mqttService):
        self.wsFactory = wsFactory
        self.mqtt = mqttService

    def dataReceived(self, data):
        data = data.decode('utf-8')
        self.log.debug('Data received: {data!r}', data=data)
        data = data.strip()
        self.wsFactory.send(data)
        self.mqtt.publish(message=data.encode('utf-8'))

    def connectionLost(self, reason):
        self.makeConnection(self.transport)


class ServerProtocol(WebSocketServerProtocol):

    log = Logger()

    def onOpen(self):
        self.log.info('client connected')
        self.factory.client = self

    def onClose(self, wasClean, code, reason):
        self.log.info('client disconnected')
        self.factory.client = None


class SerialToWebsocketServerFactory(WebSocketServerFactory):

    protocol = ServerProtocol

    log = Logger()

    def __init__(self, *args, **kwargs):
        super(SerialToWebsocketServerFactory, self).__init__(*args, **kwargs)
        self.client = None

    def send(self, data):
        if self.client is not None:
            self.log.debug('Data to send: {data!r}', data=data)
            data = data.encode('utf-8')
            self.client.sendMessage(data, False)
        else:
            self.log.warn('no client to send data to')
