#!/bin/bash


clear
echo "Starting up exchange ..."
python receive.py & 
PID=$!
echo "Done."
sleep 2;
python send.py
sleep 2;
echo "Shutting down exchange ..."
kill $PID
echo "Done."
