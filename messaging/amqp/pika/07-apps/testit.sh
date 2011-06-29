#!/bin/bash


clear
echo "RabbitMQ checks:"
echo
sudo rabbitmqctl list_vhosts
sudo rabbitmqctl list_queues
sudo rabbitmqctl list_bindings
echo "Starting up exchange ..."
python receive.py & 
PID=$!
echo "...done."
sleep 2;
python send.py
sudo rabbitmqctl list_queues
sudo rabbitmqctl list_bindings
sleep 5;
echo "Shutting down exchange ..."
kill $PID
echo "...done."
echo
echo "RabbitMQ checks:"
sudo rabbitmqctl list_vhosts
sudo rabbitmqctl list_queues
sudo rabbitmqctl list_bindings
