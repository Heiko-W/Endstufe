#!/bin/bash

sudo cp endstufe.py /etc/Endstufe/endstufe.py
sudo chmod +x /etc/Endstufe/endstufe.py

sudo cp endstufe.service /etc/systemd/system/endstufe.service
sudo systemctl disable endstufe
sudo systemctl daemon-reload
sudo systemctl enable endstufe
sudo systemctl start endstufe