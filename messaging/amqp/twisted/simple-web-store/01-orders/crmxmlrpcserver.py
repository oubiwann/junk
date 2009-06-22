from twisted.web import server, xmlrpc
from twisted.application import service, internet

import xmlrpclib


class CRMXMLRPC(xmlrpc.XMLRPC):

    def xmlrpc_echo(self, *args):
        """Return all passed args."""
        return args


class OrderQueue(xmlrpc.XMLRPC):

    queue = [
        {"order_number": 1, "customer_id": 23, "item": "kilt", "size": "sm"},
        {"order_number": 2, "customer_id": 117, "item": "kilt", "size": "med"},
        {"order_number": 3, "customer_id": 592, "item": "kilt", "size": "lg"},
        ]

    def xmlrpc_pop(self):
        """Return 'hello, world'."""
        try:
            value = self.queue.pop()
        except IndexError:
            value = {}
        return value


application = service.Application("CRM XML-RPC Server")
root = CRMXMLRPC()
root.putSubHandler("orderQueue", OrderQueue())
site = server.Site(root)
service = internet.TCPServer(8081, site)
service.setServiceParent(application)
