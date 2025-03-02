#!/bin/bash

# System-wide proxy settings
export http_proxy="http://192.168.2.4:3128"
export https_proxy="http://192.168.2.4:3128"
export ftp_proxy="http://192.168.2.4:3128"
export no_proxy="localhost,127.0.0.1,192.168.2.0/24"

# Add to system-wide environment
echo "http_proxy=$http_proxy
https_proxy=$https_proxy
ftp_proxy=$ftp_proxy
no_proxy=$no_proxy" | sudo tee /etc/environment

# Configure APT proxy
echo "Acquire::http::Proxy \"$http_proxy\";
Acquire::https::Proxy \"$https_proxy\";" | sudo tee /etc/apt/apt.conf.d/95proxies

# Configure snap proxy
sudo snap set system proxy.http="$http_proxy"
sudo snap set system proxy.https="$https_proxy"

# Print current settings
echo "Current proxy settings:"
echo "HTTP Proxy: $http_proxy"
echo "HTTPS Proxy: $https_proxy"
echo "No Proxy: $no_proxy"
