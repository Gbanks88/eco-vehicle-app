#!/bin/bash

# Autodesk Software Server Setup Script

# Update system
echo "Updating system..."
sudo apt update && sudo apt upgrade -y

# Install required dependencies
echo "Installing dependencies..."
sudo apt install -y \
    build-essential \
    cmake \
    mesa-utils \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    xserver-xorg \
    xorg \
    openbox \
    nvidia-driver-535 \
    nvidia-cuda-toolkit \
    virtualgl \
    turbovnc \
    xvfb \
    libxss1 \
    libnss3 \
    libasound2 \
    libgconf-2-4 \
    libxtst6 \
    libxrender1 \
    libxi6 \
    libgtk-3-0

# Create directories
echo "Creating directories..."
sudo mkdir -p /opt/autodesk
sudo mkdir -p /var/log/autodesk
sudo mkdir -p /data/autodesk-projects
sudo chown -R $USER:$USER /opt/autodesk /var/log/autodesk /data/autodesk-projects

# Install VirtualGL and TurboVNC for remote 3D acceleration
echo "Setting up VirtualGL..."
sudo /opt/VirtualGL/bin/vglserver_config -config +s +f -t

# Configure X server
echo "Configuring X server..."
cat << EOF | sudo tee /etc/X11/xorg.conf
Section "ServerLayout"
    Identifier     "Layout0"
    Screen      0  "Screen0" 0 0
EndSection

Section "Screen"
    Identifier     "Screen0"
    Device         "Device0"
    DefaultDepth    24
EndSection

Section "Device"
    Identifier     "Device0"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
    BoardName      "NVIDIA GPU"
EndSection
EOF

# Set up VNC server
echo "Setting up VNC server..."
cat << EOF > ~/.vnc/config
session=openbox
geometry=1920x1080
alwaysshared
EOF

# Create startup script for Autodesk applications
echo "Creating startup scripts..."
cat << 'EOF' | sudo tee /usr/local/bin/start-autodesk
#!/bin/bash
export DISPLAY=:0
export VGL_DISPLAY=:0
vglrun /opt/autodesk/$1/bin/$1
EOF
sudo chmod +x /usr/local/bin/start-autodesk

# Set up monitoring for GPU usage
echo "Setting up GPU monitoring..."
cat << 'EOF' | sudo tee /usr/local/bin/gpu-status
#!/bin/bash
nvidia-smi --query-gpu=timestamp,name,pci.bus_id,driver_version,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used --format=csv -l 1
EOF
sudo chmod +x /usr/local/bin/gpu-status

# Create license server configuration
echo "Setting up license server configuration..."
cat << EOF | sudo tee /opt/autodesk/licpath.lic
ADSKFLEX_LICENSE_FILE=@192.168.2.4
EOF

# Set up environment variables
echo "export ADSKFLEX_LICENSE_FILE=@192.168.2.4" >> ~/.bashrc
echo "export AUTODESK_ROOT=/opt/autodesk" >> ~/.bashrc
echo "export PATH=\$PATH:/opt/autodesk/bin" >> ~/.bashrc

# Create installation directories for each Autodesk product
mkdir -p /opt/autodesk/{autocad,inventor,fusion360,3dsmax,maya}

# Set up remote access service
cat << EOF | sudo tee /etc/systemd/system/autodesk-remote.service
[Unit]
Description=Autodesk Remote Access Service
After=network.target

[Service]
Type=simple
User=$USER
Environment=DISPLAY=:0
ExecStart=/usr/bin/vncserver :0 -geometry 1920x1080 -depth 24
ExecStop=/usr/bin/vncserver -kill :0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl enable autodesk-remote
sudo systemctl start autodesk-remote

# Create backup script for Autodesk projects
cat << 'EOF' | sudo tee /usr/local/bin/backup-autodesk
#!/bin/bash
BACKUP_DIR=/data/backups/autodesk
DATE=$(date +%Y%m%d)
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/autodesk-projects-$DATE.tar.gz /data/autodesk-projects
find $BACKUP_DIR -type f -mtime +7 -delete
EOF
sudo chmod +x /usr/local/bin/backup-autodesk

# Add backup to crontab
(crontab -l 2>/dev/null; echo "0 0 * * * /usr/local/bin/backup-autodesk") | crontab -

echo "Setup complete! Next steps:"
echo "1. Install Autodesk software packages"
echo "2. Configure license server"
echo "3. Set up user accounts"
echo "4. Configure remote access"
echo ""
echo "Remote access will be available at: vnc://192.168.2.4:5900"
echo "Use 'gpu-status' to monitor GPU usage"
echo "Use 'start-autodesk <program>' to launch Autodesk applications"
