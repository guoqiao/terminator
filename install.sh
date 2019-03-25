#!/bin/bash
set -xue

sudo pip3 install -r requirements.txt

if (which brew); then
    brew install \
        pygobject3 \
        vte3 \
        gtk+3
elif (which apt-get); then
    sudo apt-get update -y
    sudo apt-get install -y \
        intltool \
        libkeybinder-dev \
        libkeybinder-3.0-dev \
        python-keybinder \
        python-vte
    sudo python3 setup.py install --verbose --record=install-files.txt
fi
