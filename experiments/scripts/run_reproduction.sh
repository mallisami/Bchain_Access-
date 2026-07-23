#!/bin/bash
set -e

echo "==================================================="
echo "Recomputing data analysis metrics..."
echo "==================================================="
echo ""
python3 experiments/scripts/compute_results.py

echo ""
echo "==================================================="
echo "Re-running Hardhat tests..."
echo "==================================================="
echo ""
cd experiments/hardhat
npx hardhat test
cd ../..

echo ""
echo "==================================================="
echo "Re-running static security analysis (Slither)..."
echo "==================================================="
echo ""
cd experiments/hardhat
# Slither can return non-zero exit code if warnings are found, so we capture the run
set +e
slither . --json ../../results/slither-report.json > ../../results/slither-summary.txt 2>&1
set -e
echo "Slither static analysis run completed! Summary at results/slither-summary.txt"
cd ../..

echo ""
echo "Reproduction pipeline run completed!"
