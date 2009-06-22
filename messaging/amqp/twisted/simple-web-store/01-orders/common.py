import os

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.protocol import ClientCreator

from txamqp import spec
from txamqp.protocol import AMQClient
from txamqp.client import TwistedDelegate


RABBIT_MQ_HOST = "192.168.4.66"
RABBIT_MQ_PORT = 5672

VHOST = "/"
EXCHANGE_NAME = "test_message_exchange"
QUEUE_NAME = "test_message_queue"
ROUTING_KEY = "test_routing_key"
CONSUMER_TAG = "test_consumer_tag"

NON_PERSISTENT = 1
PERSISTENT = 2

credentials = {"LOGIN": "guest", "PASSWORD": "guest"}


def createClient():
    specFile = os.path.join(os.path.dirname(__file__), "amqp0-8.xml")
    # create the Twisted producer client
    return ClientCreator(
        reactor, AMQClient, delegate=TwistedDelegate(),
        vhost=VHOST, spec=spec.load(specFile))


@inlineCallbacks
def getConnection():
    client = createClient()
    connection = yield client.connectTCP(
        RABBIT_MQ_HOST, RABBIT_MQ_PORT)
    # start the connection negotiation process, sending security mechanisms
    # which the client can use for authentication
    yield connection.start(credentials)
    returnValue(connection)


@inlineCallbacks
def getChannel():
    connection = getConnection()
    # create a new channel that we'll use for sending messages; we can use any
    # numeric id here, only one channel will be created; we'll use this channel
    # for all the messages that we send
    channel = yield connection.channel(3)
    # open a virtual connection; channels are used so that heavy-weight TCP/IP
    # connections can be used my multiple light-weight connections (channels)
    yield channel.channel_open()
    returnValue(channel)


@inlineCallbacks
def cleanUp(connection, channel):
    # close the connections
    yield channel.channel_close()
    channel = yield connection.channel(0)
    yield channel.connection_close()
    returnValue(None)
