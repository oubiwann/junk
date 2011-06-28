#!/bin/bash


clear
echo "Starting up exchange ..."
python receive.py & 
PID=$!
echo "Done."
python send.py "kern.critical" "A critical kernel error"
python send.py "kern.info" "An info-level kernel message"
python send.py "sys.info" "An info-level system message"
python send.py
python send.py "sys.critical" "A critical system error"
echo "Shutting down exchange ..."
kill $PID
echo "Done."
