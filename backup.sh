#!/bin/bash

# run python backup script
python3 backup_script.py

# RTC WAKE UP
# Takes a 24hour time HH:MM as its argument
# Example:
# suspend_until 9:30
# suspend_until 18:45

# ------------------------------------------------------
# Argument check
if [ $# -lt 1 ]; then
    echo "Usage: suspend_until HH:MM"
    exit
fi

# Check whether specified time today or tomorrow
DESIRED=$((`date +%s -d "$1"`))
NOW=$((`date +%s`))
if [ $DESIRED -lt $NOW ]; then
    DESIRED=$((`date +%s -d "$1"` + 24*60*60))
fi
DESIRED=$(($DESIRED + $2*24*60*60))

# Kill rtcwake if already running
#sudo killall rtcwake

# Set RTC wakeup time
# N.B. change "mem" for the suspend option
# find this by "man rtcwake"
sudo rtcwake -l -m off -t $DESIRED &

# feedback
echo "Shutdown..."

# give rtcwake some time to make its stuff
sleep 2
