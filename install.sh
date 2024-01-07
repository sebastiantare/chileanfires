#!/bin/bash

sudo apt-get update

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 could not be found. Installing Python 3..."
    sudo apt-get install python3 python3-pip -y
fi

# Check if conda is installed
if ! command -v conda &> /dev/null
then
    echo "Conda could not be found. Installing Conda..."
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    bash miniconda.sh -b -p $HOME/miniconda
    echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
fi

sudo apt install build-essential libssl-dev libpq-dev libffi-dev python3-dev -y

# Create Conda environment
conda env create -f environment.yml
conda activate api

# Install Python packages
pip install -r requirements.txt

# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib -y

# Start PostgreSQL service
sudo service postgresql start

# PostgreSQL password
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres'"

echo "Installation completed successfully."
