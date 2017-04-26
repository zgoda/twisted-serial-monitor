import os
import sys

from twisted.python import log
from twisted.logger import Logger
from twisted.application import service
from twisted.internet import reactor

from service.service import make_service


logger = Logger()

root = make_service(reactor)
application = service.Application('serial-router')
root.setServiceParent(application)


if __name__ == "__main__":
    debug = os.environ.get('DEBUG')
    if not debug:
        log.startLogging(sys.stdout)

    root.startService()

    # run everything
    reactor.run()
