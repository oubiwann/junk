import sys

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator

from txamqp.protocol import AMQClient
from txamqp.client import TwistedDelegate
from txamqp.content import Content
import txamqp.spec

import common


@inlineCallbacks
def pushText(chan, body):
    msg = Content(body)
    msg["delivery mode"] = 2
    yield chan.basic_publish(
        exchange="sorting_room", content=msg,
        routing_key="jason")
    returnValue(None)


@inlineCallbacks
def cleanUp(conn, chan):
    yield chan.channel_close()
    chan = yield conn.channel(0)
    yield chan.connection_close()
    reactor.stop()
    returnValue(None)


@inlineCallbacks
def main(spec, credentials):
    delegate = TwistedDelegate()
    producer = ClientCreator(
        reactor, AMQClient, delegate=delegate,
        vhost="/", spec=spec)
    conn = yield producer.connectTCP(
        common.RABBIT_MQ_HOST, common.RABBIT_MQ_PORT)
    chan = yield common.getChannel(conn, credentials)
    yield pushText(chan, sys.argv[2])
    yield cleanUp(conn, chan)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "%s path_to_spec content" % sys.argv[0]
        sys.exit(1)
    spec = txamqp.spec.load(sys.argv[1])
    main(spec, common.credentials)
    reactor.run()
