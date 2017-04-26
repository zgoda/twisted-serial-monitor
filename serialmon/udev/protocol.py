"""
Based on https://gist.github.com/dpnova/a7830b34e7c465baace7
"""

import pyudev
from twisted.internet import abstract
from twisted.internet.serialport import SerialPort
from serial.tools.list_ports import comports


def get_serialports():
    result = []
    for p, d, h in comports():
        if not p:
            continue
        result.append({"port": p, "description": d, "hwid": h})
    return result


class UDevMonitor(abstract.FileDescriptor):
    """
    Protocol wrapper for pyudev.Monitor.

    @see: U{http://packages.python.org/pyudev/api/monitor.html}.
    """

    def __init__(self, reactor, protocol, subsystem=None, deviceType=None):
        abstract.FileDescriptor.__init__(self, reactor)

        # Set up monitor
        context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(context)
        kw = {}
        if subsystem:
            kw['subsystem'] = subsystem
        if deviceType:
            kw['device_type'] = deviceType
        self.monitor.filter_by(**kw)

        # Connect protocol
        self.protocol = protocol

    def fileno(self):
        """
        Return monitor's file descriptor.
        """
        return self.monitor.fileno()

    def startReading(self):
        """
        Start waiting for read availability.
        """
        self.monitor.start()
        abstract.FileDescriptor.startReading(self)

    def doRead(self):
        """
        An event is ready, decode it through Monitor and call our protocol.
        """
        event = self.monitor.receive_device()
        if event:
            action, device = event
            self.protocol.event_received(action, device)


class UDevMonitorListener(object):

    subsystem = 'usb'
    device_type = 'usb_device'

    def __init__(self, device_listener, reactor=None, subsystem=None, device_type=None):
        if reactor is None:
            from twisted.internet import reactor
        self.reactor = reactor
        self.device_listener = device_listener
        if subsystem is not None:
            self.subsystem = subsystem
        if device_type is not None:
            self.device_type = device_type
        self.monitor = None

    def start_listening(self):
        self.monitor = UDevMonitor(self.reactor, self, self.subsystem, self.device_type)
        self.monitor.startReading()

    def event_received(self, action, device):
        print action, device


class UDevDeviceListener(object):

    def __init__(self, reactor, proto, baud_rate):
        self.baud_rate = baud_rate
        self.reactor = reactor
        self.proto = proto
        ports = get_serialports()
        if len(ports) == 1:
            self.make_serialport(ports[0])
        else:
            self.port = None

    def make_serialport(self, port_data):
        self.port = SerialPort(self.proto, port_data['port'], self.reactor, baudrate=self.baud_rate)
