#! bin/bash

# add admin user
adduser k8admin
usermod -aG sudo
su - k8admin

sudo apt update && apt upgrade -y

# install microk8s
sudo snap install microk8s --classic --channel=1.31
# add the user
sudo usermod -a -G microk8s $USER
mkdir -p ~/.kube
chmod 0700 ~/.kube
# copy the kube config (for k9s)
cd $HOME
mkdir .kube
cd .kube
microk8s config > config
# microk8s status --wait-ready

# install kubectl
snap install kubectl --classic
config config use-context microk8s

# install k9s
snap install k9s --devmode

# put the aliases in bash_aliases
cat <<EOF > .bash_aliases
alias mk8='microk8s'
alias k8='microk8s kubectl'
alias helm='microk8s helm'
EOF
source .bash_aliases

# enable add-ons
mk8 enable ingress observability dashboard hostpath-storage

kubectl create secret tls dev.qmra-secret\
 --namespace=observability\
 --cert=/etc/letsencrypt/live/dev.qmra.org/fullchain.pem\
 --key=/etc/letsencrypt/live/dev.qmra.org/privkey.pem