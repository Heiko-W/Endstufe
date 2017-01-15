#!/bin/bash

SCRIPT_DIRECTORY=/etc/endstufe
SCRIPT_NAME=endstufe.py
USER=endstufe
#TEMPDIR='mkdir -d'

# Check if pymata is installed
#if 'pip3 show pymata-aio' > null; then
#    echo "Pymata already installed"
#else 
#    pip3 install pymata-aio
#fi

# Create User if not exists
if id "endstufe" > /dev/null 2>&1; then
    echo "endstufe user already exists"
else
    echo "need to create user: $USER"
    sudo adduser $USER
    # Add user to group dialout to get access to tty ports
    sudo adduser $USER dialout
    sudo chmod o+rw /dev/snd/*
fi

# Create directory for script if not exists
if [ ! -d "$SCRIPT_DIRECTORY" ]; then
    sudo mkdir $SCRIPT_DIRECTORY
    sudo chown $USER:dialout $SCRIPT_DIRECTORY
fi

sudo cp endstufe.py $SCRIPT_DIRECTORY/$SCRIPT_NAME
sudo chown $USER:dialout $SCRIPT_DIRECTORY/$SCRIPT_NAME
sudo chmod +x $SCRIPT_DIRECTORY/$SCRIPT_NAME

sudo cp endstufe.service /etc/systemd/system/endstufe.service
sudo systemctl disable endstufe
sudo systemctl daemon-reload
sudo systemctl enable endstufe
sudo systemctl start endstufe