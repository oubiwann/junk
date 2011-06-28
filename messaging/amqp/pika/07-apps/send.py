#!/usr/bin/env python
import pika
import sys

from common import *


exchange_name = "app_data"
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.exchange_declare(exchange=exchange_name, type=exchange_type)

routing_key = sys.argv[1] if len(sys.argv) > 1 else 'anonymous.info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'
channel.basic_publish(exchange=exchange_name, routing_key=routing_key,
                      body=message)


print " [ ] Sent %r:%r" % (routing_key, message)


connection.close()
