#!/usr/bin/env python
import sys

import pika

from common import *


connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.exchange_declare(exchange=exchange_name, type=exchange_type)
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue


for routing_key in routing_keys:
    channel.queue_bind(
        exchange=exchange_name,
        queue=queue_name,
        routing_key=routing_key)


print " [*] Waiting for application data ... "
print "To exit press CTRL+C"


def callback(ch, method, properties, body):
    print " [x] Received in %r: %r" % (method.routing_key, body)


channel.basic_consume(callback, queue=queue_name, no_ack=True)
channel.start_consuming()
