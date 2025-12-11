#! /bin/bash

# set this to your wallet's directory
# the default is the home directory as specified in the manual.
export TNS_ADMIN="/home/ubuntu/wallet"

# provide your Oracle DB credentials here
export DB_USERNAME=""
export DB_PASSWORD=""
export DB_ALIAS=""

# Shared Secrets
export SECRET_KEY="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
export CLIENT_SECRET=$SECRET_KEY
export CLIENT_ID='desco-app'
export SECRET_CODE='g-HvFZT2P42nXlu-L2uobW3yOObcqfcDU5wNy37K4XA'
export ALGORITHM="HS256"

# Authentication server IP
export AUTH_SERVER_IP="140.238.228.84"

# HOST IP (app's ip, automatically retrieved)
GET_HOST_IP=$(curl -s ifconfig.me)
export HOST_IP="$GET_HOST_IP"
