#!/bin/bash

# Check if apache2-utils is installed
if ! command -v htpasswd &> /dev/null; then
    echo "Installing apache2-utils..."
    sudo apt-get update && sudo apt-get install -y apache2-utils
fi

# Create .htpasswd file
echo "Generating passwords for protected endpoints..."

# Create or overwrite .htpasswd file
htpasswd -c -B ../nginx/.htpasswd admin

echo "Passwords have been generated and saved to nginx/.htpasswd"
echo "Use these credentials to access protected endpoints (Prometheus, Redis Commander, etc.)" 