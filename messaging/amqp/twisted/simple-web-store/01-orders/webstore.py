from twisted.web import server
from twisted.web.resource import Resource
from twisted.application import service, internet

import endpoint


FORM = """
<html>
<body>
<p><strong>Shopping Cart</stong></p>
<form action="/processOrder" method="put">
<input type="text" name="item" value="kilt"><br/>
<input type="text" name="size" value="large"<br/>
<input type="submit" value="Place Order" />
</form>
</body>
</html>
"""

THANKS = """
<html>
<body>
<p><strong>Thanks!</strong></p>
<p>Your order has been processed</p>
</body>
</html>
"""

OOPS = """
<html>
<body>
<p><strong>Oops!</strong></p>
<p>There was a problem placing your order.</p>
</body>
</html>
"""


class ShoppingCart(Resource):
    isLeaf = True
    def render_GET(self, request):
        return FORM


class ProcessOrder(Resource):
    isLeaf = True
    def render(self, request):
        # code for saving these to a database
        databaseCalls = "dummy"
        # code that creates a new order message
        endpoint.sendMessage(request)
        try:
            request.write(THANKS)
        except Exception, error:
            request.write(OOPS)
            request.write(error)
        finally:
            request.finish()


class Store(Resource):
    def getChild(self, path, request):
        if path == "shoppingCart":
            return ShoppingCart()
        elif path == "processOrder":
            return ProcessOrder()
        else:
            return Resource.getChild(self, path, request)


application = service.Application("Web Store")
storeService = service.IService(application)
storeSite = server.Site(Store())
storeServer = internet.TCPServer(8080, storeSite)
storeServer.setServiceParent(storeService)
