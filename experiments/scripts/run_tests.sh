#!/bin/bash
set -e

echo "==================================================="
echo "Running Hardhat contract unit tests..."
echo "==================================================="
echo ""

cd experiments/hardhat
npx hardhat test > ../../results/hardhat-test-output.txt 2>&1
cat ../../results/hardhat-test-output.txt
cd ../..

echo ""
echo "Tests run completed successfully!"
