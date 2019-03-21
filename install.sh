#!/bin/bash

set -xue

sudo apt update -y
sudo apt install -y \
    intltool \
    libkeybinder-dev \
    libkeybinder-3.0-dev \
    python-keybinder \
    python-vte

sudo /usr/bin/pip3 install -r requirements.txt

sudo /usr/bin/python3 setup.py build --verbose

sudo /usr/bin/python3 setup.py install --verbose --record=install-files.txt
