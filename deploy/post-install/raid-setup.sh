#!/bin/bash

# Install required packages
sudo apt update
sudo apt install -y mdadm lvm2

# Create RAID 0 array
echo "Creating RAID 0 array..."
sudo mdadm --create /dev/md0 --level=0 --raid-devices=2 /dev/sda3 /dev/sdb1

# Wait for RAID array to initialize
echo "Waiting for RAID array to initialize..."
sudo mdadm --wait /dev/md0

# Create physical volume
sudo pvcreate /dev/md0

# Create volume group
sudo vgcreate vg0 /dev/md0

# Create logical volumes
echo "Creating logical volumes..."
sudo lvcreate -L 200G -n lv_root vg0     # Root filesystem
sudo lvcreate -L 300G -n lv_var vg0      # Variable data
sudo lvcreate -L 200G -n lv_home vg0     # Home directories
sudo lvcreate -l 100%FREE -n lv_data vg0 # Remaining space for data

# Create filesystems
echo "Creating filesystems..."
sudo mkfs.ext4 /dev/vg0/lv_root
sudo mkfs.ext4 /dev/vg0/lv_var
sudo mkfs.ext4 /dev/vg0/lv_home
sudo mkfs.ext4 /dev/vg0/lv_data

# Create mount points
sudo mkdir -p /mnt/root
sudo mkdir -p /mnt/var
sudo mkdir -p /mnt/home
sudo mkdir -p /mnt/data

# Mount temporary
sudo mount /dev/vg0/lv_root /mnt/root
sudo mount /dev/vg0/lv_var /mnt/var
sudo mount /dev/vg0/lv_home /mnt/home
sudo mount /dev/vg0/lv_data /mnt/data

# Update fstab
echo "Updating /etc/fstab..."
echo "# RAID Logical Volumes
/dev/vg0/lv_root /     ext4    defaults    0 1
/dev/vg0/lv_var  /var  ext4    defaults    0 2
/dev/vg0/lv_home /home ext4    defaults    0 2
/dev/vg0/lv_data /data ext4    defaults    0 2" | sudo tee -a /etc/fstab

# Save RAID configuration
sudo mdadm --detail --scan | sudo tee -a /etc/mdadm/mdadm.conf

# Update initramfs
sudo update-initramfs -u

# Set up monitoring
echo "Setting up RAID monitoring..."
sudo systemctl enable mdmonitor
sudo systemctl start mdmonitor

# Create RAID status script
echo '#!/bin/bash
echo "RAID Status:"
sudo mdadm --detail /dev/md0
echo -e "\nDisk Space:"
df -h
echo -e "\nLogical Volumes:"
sudo lvdisplay
echo -e "\nVolume Groups:"
sudo vgdisplay' | sudo tee /usr/local/bin/raid-status
sudo chmod +x /usr/local/bin/raid-status

echo "RAID Setup Complete!"
echo "Run 'raid-status' to check RAID health"
raid-status
