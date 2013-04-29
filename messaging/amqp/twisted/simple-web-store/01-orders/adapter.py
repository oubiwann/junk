from twisted.web.xmlrpc import Proxy
from twisted.internet import reactor

import common


@inlineCallbacks
def main():
    while True:
        proxy = Proxy("http://10.0.4.64:8081/RPC")
        orderData = yield proxy.callRemote('orderQueue.pop')
        yield common.sendMessage(orderData, "crm-queue")


if name == "__main__":
    main()
    reactor.run()
