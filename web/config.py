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
