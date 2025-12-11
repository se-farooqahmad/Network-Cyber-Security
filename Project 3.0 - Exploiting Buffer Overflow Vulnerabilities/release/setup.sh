#!/usr/bin/env bash

ROLL_NUMBER=""
BINARY_NAME="converter"

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
sudo apt-get install -y gdb ncat zsh

# update /bin/nc to point to /bin/ncat
sudo ln -sf /bin/ncat /bin/nc

# update /bin/sh to point to /bin/zsh
sudo ln -sf /bin/zsh /bin/sh

# fetch the binary from the remote server
wget --no-check-certificate -O app/bin/$BINARY_NAME "https://$BINSERVER/binary/$ROLL_NUMBER"

# make the binary executable
chmod +x app/bin/$BINARY_NAME

# change the owner to root
sudo chown root app/bin/$BINARY_NAME

# set the setuid bit
sudo chmod 4755 app/bin/$BINARY_NAME

# create a venv
python3 -m virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate