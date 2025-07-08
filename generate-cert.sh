#!/bin/bash

CERT_DIR="/app/certs"
mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

# Check if certificates already exist
if [ -f "cert.pem" ] && [ -f "key.pem" ]; then
    echo "SSL certificates already exist. Skipping generation."
    echo "Using existing cert files:"
    ls -l cert.pem key.pem
    exit 0
fi

# Generate the RSA private key (encrypted with a passphrase)
openssl genrsa -des3 -passout pass:x -out server.pass.key 2048

# Remove the passphrase from the private key (to generate a usable key)
openssl rsa -passin pass:x -in server.pass.key -out key.pem

# Remove the passphrase encrypted private key file
rm server.pass.key

# Generate the certificate signing request (CSR)
openssl req -new -key key.pem -out server.csr \
    -subj "/C=FI/ST=Pohjois-Karjala/L=Joensuu/O=Materialisting Oy/OU=IT Department/CN=example.com"

# Self-sign the CSR to create the certificate (valid for 365 days)
openssl x509 -req -days 365 -in server.csr -signkey key.pem -out cert.pem

echo "Generated cert files:"
ls -l
