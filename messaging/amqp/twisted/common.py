from twisted.internet.defer import inlineCallbacks, returnValue


RABBIT_MQ_HOST = "localhost"
RABBIT_MQ_PORT = 5672

EXCHANGE_NAME = "test_message_exchange"
QUEUE_NAME = "test_message_queue"
ROUTING_KEY = "test_routing_key"
CONSUMER_TAG = "test_consumer_tag"

NON_PERSISTENT = 1
PERSISTENT = 2

credentials = {"LOGIN": "guest", "PASSWORD": "guest"}


@inlineCallbacks
def getConnection(client):
    conn = yield client.connectTCP(
        RABBIT_MQ_HOST, RABBIT_MQ_PORT)
    yield conn.start(credentials)
    returnValue(conn)


@inlineCallbacks
def getChannel(conn, credentials):
    chan = yield conn.channel(1)
    yield chan.channel_open()
    returnValue(chan)

