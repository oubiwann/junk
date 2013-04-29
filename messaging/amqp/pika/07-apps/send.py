#!/usr/bin/env python
import json
import sys

import pika

from common import *


connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.exchange_declare(exchange=exchange_name, type=exchange_type)


for routing_key, data in message_data:
    channel.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=data)
    print " [ ] Sent message to %r" % routing_key


connection.close()
