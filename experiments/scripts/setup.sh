#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "==================================================="
echo "Setting up BCHAIN-ACCESS local environments..."
echo "==================================================="
echo ""

echo "Installing Node.js dependencies for Hardhat..."
cd experiments/hardhat
npm install
cd ../..

echo ""
echo "Setting up Python virtual environment..."
cd core/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ../..

echo ""
echo "Setup completed successfully!"
