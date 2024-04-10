#! /bin/bash

set -e

source ./django_deployment_vars

DJANGO_USER=$DJANGO_PROJECT
DJANGO_GROUP=$DJANGO_PROJECT
if [ $PYTHON = "3" ]; then
	PYTHON_EXECUTABLE=/usr/bin/python3
else
	PYTHON_EXECUTABLE=/usr/bin/python
fi

# Creating a user and group
if ! getent passwd $DJANGO_PROJECT; then
	adduser --system --home=/var/opt/$DJANGO_PROJECT \
		--no-create-home --disabled-password --group \
		--shell=/bin/bash $DJANGO_USER
fi


# The data directory
mkdir -p /var/opt/$DJANGO_PROJECT
chown $DJANGO_USER /var/opt/$DJANGO_PROJECT

# download miniconda into django users home directorysource ~/.bashrc # activate shell
su - $DJANGO_USER -c 'wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh'

# install miniconda as Django user
su - $DJANGO_USER -c '/bin/bash ~/Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda3'

source /var/opt/$DJANGO_PROJECT/miniconda3/bin/activate
su - $DJANGO_USER -c "source /var/opt/$DJANGO_PROJECT/miniconda3/bin/activate"

conda create -n $DJANGO_PROJECT python=3.10 -y

cd /var/opt/$DJANGO_PROJECT/miniconda3/lib
mv -vf libstdc++.so.6 libstdc++.so.6.old
ln -s /usr/lib/x86_64-linux-gnu/libstdc++.so.6 ./libstdc++.so.6


cd /var/opt/$DJANGO_PROJECT/miniconda3/envs/$DJANGO_PROJECT/lib
mv -vf libstdc++.so.6 libstdc++.so.6.old
ln -s /usr/lib/x86_64-linux-gnu/libstdc++.so.6 ./libstdc++.so.6