#!/usr/bin/env python
import pika
import sys


exchange_name = "app_data"
connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange=exchange_name, type='topic')

routing_key = sys.argv[1] if len(sys.argv) > 1 else 'anonymous.info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'
channel.basic_publish(exchange=exchange_name,
                      routing_key=routing_key,
                      body=message)


print " [x] Sent %r:%r" % (routing_key, message)


connection.close()
