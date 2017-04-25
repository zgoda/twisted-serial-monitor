SERIAL_PORT_BAUD_RATE = 115200
SERIAL_PORT_DEVICE = '/dev/ttyUSB0'

DEBUG = False
TESTING = False

try:
    from .config_local import *  # noqa
except ImportError:
    pass

try:
    from .secrets import *  # noqa
except ImportError:
    pass
