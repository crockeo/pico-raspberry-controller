#!/usr/bin/env bash

# Ensuring we run in sudo
SUDO=""
if [ "$EUID" -ne 0 ]
then
    SUDO="sudo"
fi

# Generating the service file
export SERVICE_PATH="$(cd "$(dirname "$0")"; pwd -P)"
cat template_pico-raspberry.service \
    | perl -p -e 's/\$\{([^}]+)\}/defined $ENV{$1} ? $ENV{$1} : $&/eg' \
    > pico-raspberry.service

# Moving the service and enabling the service file
$SUDO mv pico-raspberry.service /etc/systemd/system/
$SUDO systemctl enable pico-raspberry
