#! /bin/bash

# update system
apt update && apt -y upgrade


# enable firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow https
ufw allow http #necessary for certbot to obtain certificate
ufw enable


if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

