import sys

from pika.adapters import SelectConnection
from pika.connection import ConnectionParameters

from common import *


class Receiver(Connector):
    """
    """
    def on_channel_open(self, channel):
        print "Channel opened."
        self.channel = channel
        self.channel.exchange_declare(
            exchange=exchange_name, type=exchange_type)
        for queue_name in queue_names:
            self.channel.queue_declare(
                queue=queue_name, durable=True, exclusive=True,
                auto_delete=True, callback=self.on_queue_declared) 
            for routing_key in routing_keys:
                if routing_key.startswith(queue_name):
                    self.channel.queue_bind(
                        exchange=exchange_name, queue=queue_name,
                        routing_key=routing_key)

    def on_queue_declared(self, frame, *args, **kwargs):
        print "Queue declared."
        self.channel.basic_consume(
            self.handle_delivery, queue=frame.method.queue)

    def handle_delivery(self, channel, method_frame, header_frame, body):
        print "[x] Data received on %s: %s" % (
            method_frame.routing_key, body)
        self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)


if __name__ == '__main__':
    host = (len(sys.argv) > 1) and sys.argv[1] or '127.0.0.1'
    receiver = Receiver(host)
    # Loop until CTRL-C
    try:
        # Start our blocking loop
        receiver.start()
    except KeyboardInterrupt:
        receiver.shutdown()
