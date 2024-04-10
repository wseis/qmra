#! /bin/bash

# update system
apt update && apt -y upgrade

# create non-root sudo user
adduser wseis
usermod -aG sudo wseis
rsync --archive --chown=wseis:wseis ~/.ssh /home/wseis

# enable firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow https
ufw allow http #necessary for certbot to obtain certificate
ufw enable


