#!/bin/bash

echo "---------- rpool_data ---------" > backup_log.txt
echo "------- rpool_data ERROR ------" > backup_error.txt
syncoid --sendoptions="w" --no-privilege-elevation --no-sync-snap --skip-parent -r --sshport 2425 syncoid@pve.home.arpa:rpool/data backup/rpool_data 1>> backup_log.txt 2>> backup_error.txt
echo "---------- nc-disk ---------" >> backup_log.txt
echo "-==---- nc-disk ERROR ------" >> backup_error.txt
syncoid --sendoptions="w" --no-privilege-elevation --no-sync-snap --skip-parent -r --sshport 2425 syncoid@pve.home.arpa:nc-disk backup/nc-disk >> backup_log.txt 2>> backup_error.txt
echo "---------- shelf_disks ---------" >> backup_log.txt
echo "------- shelf_disks ERROR ------" >> backup_error.txt
syncoid --sendoptions="w" --no-privilege-elevation --no-sync-snap --skip-parent -r --sshport 2425 syncoid@pve.home.arpa:shelf/disks backup/shelf_disks >> backup_log.txt 2>> backup_error.txt
echo "---------- rpool_data ---------" >> backup_log.txt
echo "------- rpool_data ERROR ------" >> backup_error.txt
syncoid --sendoptions="w" --no-privilege-elevation --no-sync-snap --skip-parent -r --sshport 2425 syncoid@pve.home.arpa:shelf/data backup/shelf_data >> backup_log.txt 2>> backup_error.txt
echo "---------- LOG -----------" >> backup_log.txt

cat /var/log/syslog | grep backup.sh >> backup_log.txt

echo "---------- SANOID -----------" >> backup_log.txt
echo "------- SANOID ERROR --------" >> backup_error.txt
sudo sanoid 1>> backup_log.txt 2>> backup_error.txt

#send contents of backup_log.txt per telegram
python3 telegram_bot.py

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
