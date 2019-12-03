#!/usr/bin/env bash

# Ensuring we run in sudo
SUDO=""
if [ "$EUID" -ne 0 ]
then
    SUDO="sudo"
fi

# Disabling and removing the service file
$SUDO systemctl stop pico-raspberry
$SUDO systemctl disable pico-raspberry
$SUDO rm /etc/systemd/system/pico-raspberry.service
