#!/bin/bash

# Create base directories
sudo mkdir -p /data/mirrors/{npm,pip,apt,docker,git}
sudo mkdir -p /data/services/{registry,cache}
sudo mkdir -p /var/log/mirrors

# Install required packages
sudo apt update
sudo apt install -y \
    nginx \
    verdaccio \
    apt-mirror \
    docker.io \
    docker-compose \
    git \
    python3-pip \
    devpi-server \
    apache2-utils

# NPM Mirror Setup
cat << EOF > /data/mirrors/npm/config.yaml
storage: /data/mirrors/npm/storage
uplinks:
  npmjs:
    url: https://registry.npmjs.org/
    timeout: 60000
packages:
  '@*/*':
    access: \$all
    publish: \$authenticated
    proxy: npmjs
  '**':
    access: \$all
    publish: \$authenticated
    proxy: npmjs
EOF

# Docker Registry Setup
cat << EOF > /data/services/registry/config.yml
version: 0.1
log:
  fields:
    service: registry
storage:
  cache:
    blobdescriptor: inmemory
  filesystem:
    rootdirectory: /data/mirrors/docker
http:
  addr: :5000
  headers:
    X-Content-Type-Options: [nosniff]
EOF

# Create Docker Compose file
cat << EOF > /data/services/docker-compose.yml
version: '3.8'

services:
  # NPM Registry Mirror
  verdaccio:
    image: verdaccio/verdaccio
    container_name: npm-mirror
    ports:
      - "4873:4873"
    volumes:
      - /data/mirrors/npm:/verdaccio
    restart: always

  # PyPI Mirror
  devpi:
    image: python:3.9
    container_name: pypi-mirror
    ports:
      - "3141:3141"
    volumes:
      - /data/mirrors/pip:/data
    command: devpi-server --host 0.0.0.0 --port 3141
    restart: always

  # Docker Registry
  registry:
    image: registry:2
    container_name: docker-mirror
    ports:
      - "5000:5000"
    volumes:
      - /data/mirrors/docker:/var/lib/registry
      - /data/services/registry/config.yml:/etc/docker/registry/config.yml
    restart: always

  # Git Mirror
  gitea:
    image: gitea/gitea
    container_name: git-mirror
    ports:
      - "3000:3000"
      - "22:22"
    volumes:
      - /data/mirrors/git:/data
    environment:
      - USER_UID=1000
      - USER_GID=1000
    restart: always

  # Cache Server
  nginx-cache:
    image: nginx
    container_name: nginx-cache
    ports:
      - "8080:80"
    volumes:
      - /data/services/cache:/var/cache/nginx
      - /data/services/nginx.conf:/etc/nginx/nginx.conf
    restart: always
EOF

# Create Nginx cache configuration
cat << EOF > /data/services/nginx.conf
worker_processes auto;
events {
    worker_connections 1024;
}

http {
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=10g inactive=60m use_temp_path=off;

    server {
        listen 80;
        
        # NPM Cache
        location /npm/ {
            proxy_cache my_cache;
            proxy_cache_use_stale error timeout http_500 http_502 http_503 http_504;
            proxy_cache_valid 200 60m;
            proxy_pass http://localhost:4873/;
        }

        # PyPI Cache
        location /pypi/ {
            proxy_cache my_cache;
            proxy_cache_use_stale error timeout http_500 http_502 http_503 http_504;
            proxy_cache_valid 200 60m;
            proxy_pass http://localhost:3141/;
        }

        # Docker Registry Cache
        location /v2/ {
            proxy_cache my_cache;
            proxy_cache_use_stale error timeout http_500 http_502 http_503 http_504;
            proxy_cache_valid 200 60m;
            proxy_pass http://localhost:5000/v2/;
        }
    }
}
EOF

# Create update script
cat << 'EOF' > /usr/local/bin/update-mirrors
#!/bin/bash

# Update APT mirror
apt-mirror

# Update NPM packages
npm cache verify
npm update -g

# Update PyPI packages
pip3 cache purge
pip3 install --upgrade pip

# Update Docker images
docker images | grep -v REPOSITORY | awk '{print $1":"$2}' | xargs -L1 docker pull

# Update Git repositories
cd /data/mirrors/git
find . -type d -name .git -exec sh -c 'cd "{}"/../ && git fetch --all' \;
EOF
chmod +x /usr/local/bin/update-mirrors

# Add to crontab for nightly updates
(crontab -l 2>/dev/null; echo "0 0 * * * /usr/local/bin/update-mirrors") | crontab -

# Start services
cd /data/services
docker-compose up -d

echo "Mirror setup complete!"
echo "Available services:"
echo "- NPM Registry: http://192.168.2.4:4873"
echo "- PyPI Mirror: http://192.168.2.4:3141"
echo "- Docker Registry: http://192.168.2.4:5000"
echo "- Git Server: http://192.168.2.4:3000"
echo "- Cache Server: http://192.168.2.4:8080"
