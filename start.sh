#!/bin/bash

# Start Hardhat node in the background
echo "Starting local Hardhat node..."
cd /app/smart_contracts
npx hardhat node --hostname 127.0.0.1 --port 8545 > /tmp/hardhat.log 2>&1 &

# Wait for Hardhat to be ready using Python
echo "Waiting for Hardhat node to start..."
python3 -c '
import urllib.request, time, urllib.error
for i in range(30):
    try:
        urllib.request.urlopen("http://127.0.0.1:8545")
        break
    except urllib.error.HTTPError:
        break
    except Exception:
        time.sleep(1)
'
echo "Hardhat node is up!"

# Deploy the smart contract to the local Hardhat node
echo "Deploying smart contract..."
npx hardhat run scripts/deploy.js --network localhost

# Check deployment.json contents
cat deployment.json

# Extract deployed contract address
CONTRACT_ADDR=$(python3 -c "import json; print(json.load(open('/app/smart_contracts/deployment.json'))['address'])")
echo "Deployed contract address: $CONTRACT_ADDR"

export WEB3_PROVIDER_URL="http://127.0.0.1:8545"
export CONTRACT_ADDRESS="$CONTRACT_ADDR"
export CONTRACT_ABI_PATH="/app/smart_contracts/artifacts/contracts/HealthAccessControl.sol/HealthAccessControl.json"
export PATIENT_PRIVATE_KEY="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
export SECRET_KEY="${SECRET_KEY:-dev-secret-key-blockchain-prototype}"
export FLASK_DEBUG="False"

# Start the Flask app
echo "Starting Flask API backend on port ${PORT:-5000}..."
cd /app/backend
exec gunicorn -w1 -b 0.0.0.0:${PORT:-5000} app:app
