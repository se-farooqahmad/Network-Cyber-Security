#!/bin/bash

# the script installs python3, pip3, and virtualenv
VENV_NAME=".venv"                 # name of the env
PROJECT_DIR="../application"       # just to make life easy
VENV_DIR="../$VENV_NAME"           # creates a venv in the current dir. replace this with the path where you want to create the venv
REQUIREMENTS="./requirements.txt" # path to the requirements file

source ./logging.sh

# Update package list and install Python, pip
log "Updating package list and installing Python, pip, and virtualenv..."
if sudo apt update && sudo apt install -y python3 python3-pip; then
  success "Python and pip installed successfully."
else
  error "Failed to install Python and pip."
fi

# Install virtualenv
log "Installing virtualenv..."
if sudo pip3 install virtualenv; then
  success "virtualenv installed successfully."
else
  error "Failed to install virtualenv."
fi

# Display Python, pip, and virtualenv versions
log "Python version:"
python3 --version

log "pip version:"
pip3 --version

log "virtualenv version:"
virtualenv --version

# check if PROJECT_DIR exists, error out if it doesn't
if [ ! -d "$PROJECT_DIR" ]; then
  error "Project directory $PROJECT_DIR not found. Make sure to put the application files in the correct directory. Expected to find the application files in $PROJECT_DIR."
fi

# check if VENV_DIR exists, warn the user if it already does. create a new venv otherwise.
if [ -d "$VENV_DIR" ]; then
  warn "Virtual environment directory $VENV_DIR already exists. Deleting the existing virtual environment..."
  if rm -rf $VENV_DIR; then
    success "Deleted existing virtual environment."
  else
    error "Failed to delete existing virtual environment."
  fi
fi

log "Creating virtual environment in $VENV_DIR..."
if virtualenv $VENV_DIR; then
  success "Virtual environment created."
else
  error "Failed to create virtual environment."
fi

# Activate virtual environment
log "Activating virtual environment and installing application dependencies..."
if source $VENV_DIR/bin/activate; then
  success "Virtual environment activated."
else
  error "Failed to activate virtual environment."
fi

# Install dependencies
if pip install -r $REQUIREMENTS; then
  success "Python modules installed correctly."
else
  deactivate
  error "Failed to install FastAPI dependencies."
fi

# Deactivate virtual environment
deactivate
success "Environment setup is complete! To start using FastAPI, activate the virtual environment with 'source $VENV_DIR/bin/activate'."
