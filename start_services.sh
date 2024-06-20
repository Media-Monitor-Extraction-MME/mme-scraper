#!/bin/bash

# Run the Python script
/home/appuser/.venv/bin/python /home/appuser/testmain.py

# Start the cron daemon
cron

# Tail the log file
tail -F /home/appuser/logs.log
