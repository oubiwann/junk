#!/usr/bin/env python
import pika
import sys

from common import *


connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.exchange_declare(exchange=exchange_name, type=exchange_type)
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue


for binding_key in binding_keys.splitlines():
    # remove whitespace
    binding_key = binding_key.strip()
    channel.queue_bind(exchange=exchange_name, queue=queue_name,
                       routing_key=binding_key)

print ' [*] Waiting for logs. To exit press CTRL+C'


def callback(ch, method, properties, body):
    print " [x] Received %r:%r" % (method.routing_key, body,)


channel.basic_consume(callback, queue=queue_name, no_ack=True)
channel.start_consuming()
