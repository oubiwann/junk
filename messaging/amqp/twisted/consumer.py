import sys

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator

from txamqp.protocol import AMQClient
from txamqp.client import TwistedDelegate
import txamqp.spec

import common


@inlineCallbacks
def getQueue(conn, chan):
    # create an exchange on the message server
    yield chan.exchange_declare(
        exchange="sorting_room", type="direct",
        durable=True, auto_delete=False)
    # create a message queue on the message server
    yield chan.queue_declare(
        queue="po_box", durable=True, exclusive=False,
        auto_delete=False)
    # bind the exchange and the message queue
    yield chan.queue_bind(
        queue="po_box", exchange="sorting_room",
        routing_key="jason")
    #XXX ? read the spec for basic_consume
    yield chan.basic_consume(
        queue='po_box', no_ack=True,
        consumer_tag="testtag")
    queue = yield conn.queue("testtag")
    returnValue(queue)


@inlineCallbacks
def processMessage(chan, queue):
    msg = yield queue.get()
    print "Received: %s from channel #%s" % (
        msg.content.body, chan.id)
    processMessage(chan, queue)
    returnValue(None)


@inlineCallbacks
def main(spec, credentials):
    delegate = TwistedDelegate()
    consumer = ClientCreator(
        reactor, AMQClient, delegate=delegate,
        vhost="/", spec=spec)
    conn = yield consumer.connectTCP(
        common.RABBIT_MQ_HOST, common.RABBIT_MQ_PORT)
    chan = yield common.getChannel(conn, credentials)
    queue = yield getQueue(conn, chan)
    while True:
        yield processMessage(chan, queue)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "%s path_to_spec" % sys.argv[0]
        sys.exit(1)
    spec = txamqp.spec.load(sys.argv[1])
    main(spec, common.credentials)
    reactor.run()
