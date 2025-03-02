#!/bin/bash

# RAID Monitoring Script
# Add to crontab: */5 * * * * /usr/local/bin/raid-monitor.sh

# Check RAID status
RAID_STATUS=$(sudo mdadm --detail /dev/md0 | grep "State :" | awk '{print $3}')
RAID_DEVICES=$(sudo mdadm --detail /dev/md0 | grep "Active Devices :" | awk '{print $4}')
EXPECTED_DEVICES=2

# Check disk space
ROOT_SPACE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
VAR_SPACE=$(df -h /var | tail -1 | awk '{print $5}' | sed 's/%//')
HOME_SPACE=$(df -h /home | tail -1 | awk '{print $5}' | sed 's/%//')
DATA_SPACE=$(df -h /data | tail -1 | awk '{print $5}' | sed 's/%//')

# Log file
LOG_FILE="/var/log/raid-monitor.log"

# Check RAID health
if [ "$RAID_STATUS" != "clean" ] || [ "$RAID_DEVICES" -ne "$EXPECTED_DEVICES" ]; then
    echo "[$(date)] WARNING: RAID array is not healthy! Status: $RAID_STATUS, Active devices: $RAID_DEVICES" >> $LOG_FILE
    # Send alert (customize as needed)
    echo "RAID Warning on $(hostname)" | mail -s "RAID Alert" root
fi

# Check disk space (warn at 90%)
for SPACE in "$ROOT_SPACE" "$VAR_SPACE" "$HOME_SPACE" "$DATA_SPACE"; do
    if [ "$SPACE" -gt 90 ]; then
        echo "[$(date)] WARNING: Disk space usage above 90% on partition" >> $LOG_FILE
        # Send alert
        echo "Disk Space Warning on $(hostname)" | mail -s "Disk Space Alert" root
    fi
done

# Log status
echo "[$(date)] RAID Status: $RAID_STATUS, Active Devices: $RAID_DEVICES" >> $LOG_FILE
echo "[$(date)] Disk Usage - Root: $ROOT_SPACE%, Var: $VAR_SPACE%, Home: $HOME_SPACE%, Data: $DATA_SPACE%" >> $LOG_FILE
