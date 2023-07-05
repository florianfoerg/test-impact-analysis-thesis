#!/bin/bash

# ============================================================================================================================================
# Script to visualize TIA data
# ============================================================================================================================================
# Note: Assumes correct command line input

# method to print info
print_info () {
    echo -e "\e[33m[INFO]\e[0m :$1"
}

install_if_not_exists() {
    local package_name="$1"
    
    if ! dpkg -s "$package_name" &> /dev/null; then
        echo "Installing $package_name..."
        sudo apt-get install -y "$package_name"
    else
        echo "$package_name is already installed."
    fi
}

install_if_not_exists "python3"
install_if_not_exists "python3-pip"

pip3 install -r requirements.txt

# take parameters
work_dir=$1

#test if work_dir is valid
if [ -z "$work_dir" ]
then
    print_info "work_dir is empty"
    print_info "Usage: ./visualize-tia.sh <work_dir>"
    exit 1
fi

# test if tia-data.csv exists in work_dir
if [ ! -f "$work_dir/tia_data.csv" ]
then
    print_info "tia_data.csv does not exist in $work_dir"
    exit 1
fi

# test if ./out exists or create it
if [ ! -d "./out" ]
then
    print_info "Creating $(pwd)/out"
    mkdir "./out"
fi

print_info "Visualizing TIA data..."
python3 visualize-first-all-failure.py "$work_dir"
python3 visualize-failure-detection.py "$work_dir"
