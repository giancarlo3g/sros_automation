#!/bin/bash

# Script to detect OS and install git and make
# Supports Debian/Ubuntu (apt) and Rocky Linux/RHEL (dnf)

set -e  # Exit on any error

echo "Detecting operating system..."

# Function to install packages with apt
install_with_apt() {
    echo "Detected Debian/Ubuntu system"
    echo "Installing git and make with apt..."
    sudo apt update
    sudo apt install -y git make
    echo "Installation completed successfully!"
}

# Function to install packages with dnf
install_with_dnf() {
    echo "Detected Rocky Linux/RHEL system"
    echo "Installing git and make with dnf..."
    sudo dnf install -y git make
    echo "Installation completed successfully!"
}

# Detect OS using release files
if [ -f /etc/debian_version ]; then
    echo "Detected: Debian/Ubuntu"
    install_with_apt
elif [ -f /etc/rocky-release ] || [ -f /etc/redhat-release ]; then
    echo "Detected: Rocky Linux/RHEL"
    install_with_dnf
else
    echo "Error: Unsupported OS. This script supports Debian/Ubuntu and Rocky Linux/RHEL only."
    exit 1
fi

echo "Verifying installation..."
git --version
make --version