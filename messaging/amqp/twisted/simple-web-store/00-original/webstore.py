from twisted.web import server, resource
from twisted.application import service, internet

FORM = """
<html>
<body>
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


class ShoppingCart(resource.Resource):
    isLeaf = True
    allowedMethods = ("GET",)
    def render_GET(self, request):
        return FORM


class ProcessOrder(resource.Resource):
    isLeaf = True
    allowedMethods = ("GET",)
    def render_GET(self, request):
        item = request.args["item"][0]
        size = request.args["size"][0]
        # code for saving these to a database
        return THANKS


class Store(resource.Resource):
    allowedMethods = ("GET",)
    def getChild(self, path, request):
        if path == "shoppingCart":
            return ShoppingCart()
        elif path == "processOrder":
            return ProcessOrder()


application = service.Application("Web Store")
storeService = service.IService(application)
storeSite = server.Site(Store())
server = internet.TCPServer(8080, storeSite)
server.setServiceParent(storeService)
