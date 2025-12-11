#!/bin/bash

# Variables
ORACLE_DIR="/home/ubuntu/oracle"
INSTANT_CLIENT_DIR="${ORACLE_DIR}/instantclient"
INSTANT_CLIENT_ZIP_URL="https://download.oracle.com/otn_software/linux/instantclient/instantclient-basic-linuxx64.zip"
SQLPLUS_CLIENT_URL="https://download.oracle.com/otn_software/linux/instantclient/instantclient-sqlplus-linuxx64.zip"

ZIP_FILE_NAME="instantclient-basic-linuxx64.zip"
SQLPLUS_ZIP_FILE_NAME="instantclient-sqlplus-linuxx64.zip"

DB_SETUP_DIR="./db_setup"
DB_SETUP_INIT="myexec.sql"

source ./logging.sh

# the script requires that the TNS_ADMIN, DB_USER, DB_PASSWORD and DB_ALIAS environment variables are set. check if they are set, error out if not.
if [ -z "$TNS_ADMIN" ]; then
  error "TNS_ADMIN environment variable is not set. Make sure to source the env.sh file before running this script."
fi

if [ -z "$DB_USERNAME" ]; then
  error "DB_USERNAME environment variable is not set. Make sure to source the env.sh file before running this script."
fi

if [ -z "$DB_PASSWORD" ]; then
  error "DB_PASSWORD environment variable is not set. Make sure to source the env.sh file before running this script."
fi

if [ -z "$DB_ALIAS" ]; then
  error "DB_ALIAS environment variable is not set. Make sure to source the env.sh file before running this script."
fi

# Update and install prerequisites
log "Installing dependencies, and tools for Oracle Instant Client libs..."
if sudo apt install -y libaio1 unzip wget; then
  success "Dependencies installed successfully."
else
  error "Failed to install dependencies."
fi

# Create installation directory if it doesn't exist
log "Creating Oracle directory at ${ORACLE_DIR}..."
rm -rf $ORACLE_DIR
mkdir -p $ORACLE_DIR && success "Directory created."

# Download the Instant Client ZIP file

if [ -f ${ZIP_FILE_NAME} ]; then
  log "File \"${ZIP_FILE_NAME}\" exists. Skipping download."
else
  log "Downloading Oracle Instant Client from ${INSTANT_CLIENT_ZIP_URL}..."
  if wget "$INSTANT_CLIENT_ZIP_URL" -O $ZIP_FILE_NAME; then
      success "Downloaded Instant Client ZIP file."
  else
      error "Failed to download the ZIP file."
  fi
fi

# Download the SQLPlus Client ZIP file
if [ -f ${SQLPLUS_ZIP_FILE_NAME} ]; then
  log "File \"${SQLPLUS_ZIP_FILE_NAME}\" exists. Skipping download."
else
  log "Downloading Oracle SQLPlus Client from ${SQLPLUS_CLIENT_URL}..."
  if wget "$SQLPLUS_CLIENT_URL" -O $SQLPLUS_ZIP_FILE_NAME; then
      success "Downloaded SQLPlus Client ZIP file."
  else
      error "Failed to download the SQLPlus ZIP file."
  fi
fi

# Unzip the Instant Client package
log "Unzipping Instant Client..."
if unzip -oq $ZIP_FILE_NAME -d instantclient; then
    mv instantclient/instantclient_* ${INSTANT_CLIENT_DIR}
    # rm -rf ${ZIP_FILE_NAME}
    success "Unzipped and installed Instant Client."
else
    error "Failed to unzip Instant Client."
fi

# Unzip the SQLPlus Client package
log "Unzipping SQLPlus Client..."
if unzip -oq $SQLPLUS_ZIP_FILE_NAME -d sqlplus; then
    cp sqlplus/instantclient_*/* ${INSTANT_CLIENT_DIR}
    success "Unzipped SQLPlus Client."
    # rm -f $SQLPLUS_ZIP_FILE_NAME
else
    error "Failed to unzip SQLPlus Client."
fi

# Make sure that the ORACLE_HOME variable is not present in the rc file.
log "Checking if ORACLE_HOME is already set..."
if grep -q "ORACLE_HOME" ${HOME}/.bashrc; then
    warn "ORACLE_HOME is already set. Skipping setting up environment variables."
else
    log "Setting up environment variables..."

    echo "export LD_LIBRARY_PATH=${INSTANT_CLIENT_DIR}:\$LD_LIBRARY_PATH" | sudo tee -a ${HOME}/.bashrc
    echo "export ORACLE_HOME=${INSTANT_CLIENT_DIR}" | sudo tee -a ${HOME}/.bashrc
    echo "export PATH=${INSTANT_CLIENT_DIR}:\$PATH" | sudo tee -a ${HOME}/.bashrc
    success "Environment variables successfuly put in the ~/.bashrc file."
fi

export ORACLE_HOME=${INSTANT_CLIENT_DIR}
export LD_LIBRARY_PATH=${INSTANT_CLIENT_DIR}:$LD_LIBRARY_PATH
export PATH=${INSTANT_CLIENT_DIR}:$PATH

# save current directory
current_dir=$(pwd)

cd $DB_SETUP_DIR || exit 1

# verify the SQLPlus installation
log "Verifying SQLPlus installation..."
if sqlplus -v; then
    success "SQLPlus installed successfully."
else
    error "Failed to install SQLPlus. Kindly verify the installation of sqlplus client."
    cd $current_dir
    exit 1
fi

# execute the DB initialization script using SQLPlus
log "Executing DB initialization script. Wait for the process to complete..."
if sqlplus -S "$DB_USERNAME/$DB_PASSWORD@$DB_ALIAS" "@$DB_SETUP_INIT"; then
    success "DB initialization scripts executed successfully."
else
    error "Failed to execute DB initialization script."
    cd $current_dir
    exit 1
fi

# Clean up section
log "Cleaning up..."
cd $current_dir

# Final message
success "Oracle Instant Client setup is complete!"
log "Make sure to source ~/.bashrc before proceeding, to setup the environment variables correctly"
