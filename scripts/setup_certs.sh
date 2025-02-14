#!/bin/bash

# Create certificates directory if it doesn't exist
mkdir -p nginx/certs

# Copy certificates for logging-dev1
echo "Copying certificates for logging-dev1.slicedhealth.com..."
sudo cp /etc/letsencrypt/live/logging-dev1.slicedhealth.com/fullchain.pem ../nginx/certs/fullchain.pem 
sudo cp /etc/letsencrypt/live/logging-dev1.slicedhealth.com/privkey.pem ../nginx/certs/privkey.pem 

# Set correct permissions
sudo chown -R $USER:$USER ../nginx/certs/
chmod 600 ../nginx/certs/*

echo "Certificates have been copied and permissions set"