#!/usr/bin/env bash

# enter your roll number here
ROLL_NUMBER=""

BINARY_DIR="./"
BINARY_NAME=${BINARY_DIR}binary

BINSERVER="140.238.228.84"

# make sure the roll number is not empty
if [ -z "$ROLL_NUMBER" ]; then
    echo "Please set the ROLL_NUMBER before running the script."
    exit 1
fi

# disable aslr
echo 0 | sudo tee /proc/sys/kernel/randomize_va_space

# install the required packages
sudo apt-get update

# install gdb
sudo apt-get install -y gdb zsh

# update /bin/sh to point to /bin/zsh
sudo ln -sf /bin/zsh /bin/sh || exit 1
# to reverse the change do teh following
# sudo ln -sf /bin/dash /bin/sh

# fetch the binary from the remote server
wget --no-check-certificate -O $BINARY_NAME "https://$BINSERVER/binary/$ROLL_NUMBER" || exit 1

# make the binary executable
chmod +x $BINARY_NAME

# change the owner to root
sudo chown root $BINARY_NAME

# set the setuid bit
sudo chmod 4755 $BINARY_NAME

# create a venv
python3 -m virtualenv .venv
source .venv/bin/activate
pip install pwntools
deactivate
