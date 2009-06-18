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
    # start the connection negotiation process, sending security mechanisms
    # which the client can use for authentication
    yield conn.start(credentials)
    returnValue(conn)


@inlineCallbacks
def getChannel(conn):
    chan = yield conn.channel(1)
    # open a virtual connection; channels are used so that heavy-weight TCP/IP
    # connections can be used my multiple light-weight connections (channels)
    yield chan.channel_open()
    returnValue(chan)

