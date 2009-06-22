from twisted.internet.defer import inlineCallbacks, returnValue                                     

from txamqp.content import Content

import common


def createOrderMessage(data, source):
    message = Content("test data")
    message["source"] = source
    message["delivery mode"] = common.NON_PERSISTENT
    return message


@inlineCallbacks
def sendMessage(requestArgs):
    # create the message from the shopping cart request
    message = createOrderMessage(requestArgs, "web store")
    # connect to messaging server and get channel
    producer = common.createProducer()
    connection = yield common.getConnection(producer)
    channel = yield common.getChannel(connection)
    # send the message to the message queue
    yield channel.basic_publish(
        exchange=common.EXCHANGE_NAME, content=message,
        routing_key=common.ROUTING_KEY)
    # close the connections
    yield common.cleanUp(connection, channel)
