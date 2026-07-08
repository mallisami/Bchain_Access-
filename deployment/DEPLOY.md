# Deployment Guide

## Healthcare Blockchain Access Control System

**Version:** 1.0.0  
**Last Updated:** 2026-06-29

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Local Development Setup](#2-local-development-setup)
3. [Smart Contract Deployment](#3-smart-contract-deployment)
4. [Backend Configuration](#4-backend-configuration)
5. [IPFS Setup](#5-ipfs-setup)
6. [Frontend Configuration](#6-frontend-configuration)
7. [Cloud Deployment](#7-cloud-deployment)
8. [Testing Checklist](#8-testing-checklist)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Prerequisites

### 1.1 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | macOS 12 / Ubuntu 20.04 / Windows 10 | macOS 14 / Ubuntu 22.04 / Windows 11 |
| RAM | 8 GB | 16 GB |
| Disk | 20 GB free | 50 GB SSD |
| Internet | 10 Mbps | 50 Mbps |

### 1.2 Required Software

Install the following tools:

#### Node.js (v18.x or later)

```bash
# macOS (Homebrew)
brew install node@18

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y nodejs npm

# Windows (Chocolatey)
choco install nodejs

# Verify
node --version  # Should print v18.x.x or higher
npm --version   # Should print 9.x.x or higher
```

#### Python (3.10 or later)

```bash
# macOS (Homebrew)
brew install python@3.10

# Ubuntu/Debian
sudo apt-get install python3.10 python3.10-pip python3.10-venv

# Windows (Microsoft Store or python.org)
# Download from https://www.python.org/downloads/

# Verify
python3 --version  # Should print 3.10.x or higher
```

#### Git

```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt-get install git

# Windows
choco install git

# Verify
git --version
```

#### Solidity Compiler (solc)

```bash
# Via npm (recommended for this project)
npm install -g solc

# Or via Homebrew (macOS)
brew install solidity

# Verify
solc --version
```

---

## 2. Local Development Setup

### 2.1 Clone and Install

```bash
# Clone the repository
git clone https://github.com/your-org/healthcare-blockchain-access.git
cd healthcare-blockchain-access

# Install Python dependencies
cd backend
python3 -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat

# Install packages
pip install flask flask-cors

# Verify
python -c "import flask; print(flask.__version__)"
```

### 2.2 Run the Backend (Simulation Mode)

```bash
# From the backend directory
python app.py
```

You should see output like:

```
============================================================
HEALTHCARE BLOCKCHAIN ACCESS CONTROL - BACKEND
============================================================
Patient wallet: 0x...
Genesis block: 0000...
Chain length: 1
------------------------------------------------------------
Pre-mining initial blocks...
Chain length after pre-mine: 3
Latest block: 0000...
============================================================
Starting Flask server on http://localhost:5000
API documentation: http://localhost:5000/api/health
============================================================
```

Verify the health endpoint:

```bash
curl http://localhost:5000/api/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": 1751198110.42,
  "service": "healthcare-blockchain-access-control",
  "version": "1.0.0"
}
```

### 2.3 Test the API Endpoints

```bash
# Test authentication
curl -X POST http://localhost:5000/api/auth/unlock \
  -H "Content-Type: application/json" \
  -d '{"method": "fingerprint"}'

# Test records
curl http://localhost:5000/api/records

# Test blockchain status
curl http://localhost:5000/api/blockchain/status

# Test blockchain explorer
curl http://localhost:5000/api/blockchain/explorer
```

---

## 3. Smart Contract Deployment

### 3.1 Install Hardhat (Recommended)

```bash
# Create a project directory for the smart contract
mkdir contract-project
cd contract-project
npm init -y
npm install --save-dev hardhat

# Initialize Hardhat
npx hardhat init
# Select: "Create a TypeScript project (with Viem)"
# Or: "Create an empty hardhat.config.js"
```

### 3.2 Configure Hardhat

Create `hardhat.config.js`:

```javascript
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.19",
  networks: {
    // Local development network
    hardhat: {
      chainId: 1337,
    },
    // Sepolia testnet (requires ETH from faucet)
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL || "https://rpc.sepolia.org",
      accounts: [process.env.PRIVATE_KEY],
      chainId: 11155111,
    },
    // Goerli testnet (deprecated, use Sepolia instead)
    // Mumbai testnet (Polygon)
    mumbai: {
      url: process.env.MUMBAI_RPC_URL || "https://rpc-mumbai.maticvigil.com",
      accounts: [process.env.PRIVATE_KEY],
      chainId: 80001,
    },
  },
  etherscan: {
    apiKey: {
      sepolia: process.env.ETHERSCAN_API_KEY,
      polygonMumbai: process.env.POLYGONSCAN_API_KEY,
    },
  },
};
```

### 3.3 Install Dependencies

```bash
npm install --save-dev @nomicfoundation/hardhat-toolbox
npm install dotenv
```

### 3.4 Create Environment File

```bash
# Create .env file (NEVER commit this to git!)
touch .env
echo ".env" >> .gitignore
```

`.env` contents:

```bash
# Private key of the deployer wallet (with testnet ETH)
# Get testnet ETH from: https://sepoliafaucet.com/ or https://faucet.quicknode.com/ethereum/sepolia
PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE

# RPC URLs (Infura or Alchemy)
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
MUMBAI_RPC_URL=https://polygon-mumbai.infura.io/v3/YOUR_INFURA_KEY

# API keys for contract verification
ETHERSCAN_API_KEY=YOUR_ETHERSCAN_KEY
POLYGONSCAN_API_KEY=YOUR_POLYGONSCAN_KEY
```

**⚠️ SECURITY WARNING**: Never use your mainnet private key on testnets. Create a dedicated test wallet.

### 3.5 Copy the Smart Contract

```bash
# Copy the contract from this project to Hardhat
cp ../smart_contracts/HealthAccessControl.sol contracts/HealthAccessControl.sol
```

### 3.6 Create Deployment Script

Create `scripts/deploy.js`:

```javascript
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with account:", deployer.address);

  const HealthAccessControl = await hre.ethers.getContractFactory("HealthAccessControl");
  const contract = await HealthAccessControl.deploy();

  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log("HealthAccessControl deployed to:", address);
  console.log("Transaction hash:", contract.deploymentTransaction().hash);

  // Save deployment info
  const fs = require("fs");
  const deploymentInfo = {
    contract: "HealthAccessControl",
    address: address,
    deployer: deployer.address,
    network: hre.network.name,
    chainId: hre.network.config.chainId,
    timestamp: new Date().toISOString(),
  };
  fs.writeFileSync("deployment.json", JSON.stringify(deploymentInfo, null, 2));
  console.log("Deployment info saved to deployment.json");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
```

### 3.7 Deploy to Local Hardhat Network

```bash
# Start a local Hardhat node
npx hardhat node

# In another terminal, deploy to the local node
npx hardhat run scripts/deploy.js --network hardhat
```

### 3.8 Deploy to Sepolia Testnet

```bash
# 1. Get Sepolia ETH from a faucet:
#    - https://sepoliafaucet.com/ (Alchemy)
#    - https://faucet.quicknode.com/ethereum/sepolia
#    - https://www.infura.io/faucet/sepolia

# 2. Verify your wallet has ETH
npx hardhat console --network sepolia
> (await ethers.provider.getBalance("YOUR_ADDRESS")).toString()

# 3. Deploy
npx hardhat run scripts/deploy.js --network sepolia

# 4. Verify contract on Etherscan
npx hardhat verify --network sepolia DEPLOYED_CONTRACT_ADDRESS
```

### 3.9 Deploy to Polygon Mumbai (Lower Gas Costs)

```bash
# Get Mumbai MATIC from: https://faucet.polygon.technology/

npx hardhat run scripts/deploy.js --network mumbai
npx hardhat verify --network mumbai DEPLOYED_CONTRACT_ADDRESS
```

---

## 4. Backend Configuration

### 4.1 Install Production Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Create `requirements.txt`:

```
flask==2.3.3
flask-cors==4.0.0
web3==6.11.0
python-dotenv==1.0.0
gunicorn==21.2.0
psycopg2-binary==2.9.7
redis==4.6.0
```

### 4.2 Configure Web3 Provider

Create `backend/config.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Production configuration for the blockchain backend."""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # CORS settings (restrict in production!)
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')

    # Blockchain settings
    WEB3_PROVIDER_URL = os.environ.get('WEB3_PROVIDER_URL', 'http://localhost:8545')
    CHAIN_ID = int(os.environ.get('CHAIN_ID', '1337'))

    # Smart contract
    CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS', '')
    CONTRACT_ABI_PATH = os.environ.get('CONTRACT_ABI_PATH', './contracts/HealthAccessControl.json')

    # Patient wallet (in production, this comes from the authenticated session)
    PATIENT_PRIVATE_KEY = os.environ.get('PATIENT_PRIVATE_KEY', '')

    # IPFS
    IPFS_GATEWAY_URL = os.environ.get('IPFS_GATEWAY_URL', 'https://ipfs.io/ipfs/')
    IPFS_API_URL = os.environ.get('IPFS_API_URL', 'http://localhost:5001')
    IPFS_API_KEY = os.environ.get('IPFS_API_KEY', '')

    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/healthchain')
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # Session
    SESSION_TIMEOUT_SECONDS = int(os.environ.get('SESSION_TIMEOUT_SECONDS', '900'))  # 15 minutes
```

### 4.3 Environment Variables for Production

```bash
# .env.production
SECRET_KEY=your-very-long-random-secret-key-min-32-chars
FLASK_DEBUG=False
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com

# Blockchain (Infura or Alchemy)
WEB3_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
CHAIN_ID=11155111
CONTRACT_ADDRESS=0xYOUR_DEPLOYED_CONTRACT_ADDRESS
CONTRACT_ABI_PATH=./contracts/HealthAccessControl.json

# Patient wallet (used for blockchain transactions on behalf of patient)
# In production, this should be a dedicated service wallet, not the patient's
PATIENT_PRIVATE_KEY=0x...

# IPFS (Pinata or Infura)
IPFS_GATEWAY_URL=https://gateway.pinata.cloud/ipfs/
IPFS_API_URL=https://api.pinata.cloud/
IPFS_API_KEY=your-pinata-api-key
IPFS_SECRET_KEY=your-pinata-secret-key

# Database (AWS RDS, Supabase, etc.)
DATABASE_URL=postgresql://user:pass@your-db-host:5432/healthchain
REDIS_URL=redis://your-redis-host:6379/0

# Session timeout
SESSION_TIMEOUT_SECONDS=900
```

### 4.4 Update app.py for Production Web3

Replace the blockchain simulation with real Web3 calls:

```python
from web3 import Web3
from config import Config

# Connect to Ethereum
w3 = Web3(Web3.HTTPProvider(Config.WEB3_PROVIDER_URL))
assert w3.is_connected(), "Failed to connect to Ethereum node"

# Load contract
with open(Config.CONTRACT_ABI_PATH) as f:
    contract_abi = json.load(f)

contract = w3.eth.contract(address=Config.CONTRACT_ADDRESS, abi=contract_abi)

# Example: check access on real blockchain
def check_real_access(patient, provider, record_hash):
    has_access, access_level = contract.functions.checkAccess(
        patient, provider, record_hash
    ).call()
    return has_access, access_level
```

---

## 5. IPFS Setup

### 5.1 Why IPFS?

Medical records are too large and sensitive to store directly on Ethereum. IPFS provides:
- **Content addressing**: The hash (CID) uniquely identifies the content
- **Decentralization**: No single point of failure
- **Integrity**: Changing the file changes the CID

### 5.2 Option A: Pinata (Managed IPFS)

```bash
# Sign up at https://pinata.cloud/
# Get your API keys from the dashboard

# Install Pinata SDK
npm install -g @pinata/sdk

# Or use Python
pip install pinata-python
```

Python example:

```python
import requests

def upload_to_ipfs(file_path, api_key, secret_key):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": api_key,
        "pinata_secret_api_key": secret_key,
    }
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files, headers=headers)
    return response.json()

# Usage
result = upload_to_ipfs(
    file_path="encrypted_mri_scan.pdf",
    api_key="YOUR_PINATA_API_KEY",
    secret_key="YOUR_PINATA_SECRET_KEY"
)
print(f"IPFS CID: {result['IpfsHash']}")
print(f"Gateway URL: https://gateway.pinata.cloud/ipfs/{result['IpfsHash']}")
```

### 5.3 Option B: Local IPFS Node

```bash
# Install IPFS
curl -L https://dist.ipfs.tech/kubo/v0.23.0/kubo_v0.23.0_linux-amd64.tar.gz | tar -xz
sudo mv kubo/ipfs /usr/local/bin/

# Initialize
ipfs init

# Start daemon
ipfs daemon

# Add a file
ipfs add encrypted_mri_scan.pdf
# Output: Qm...  encrypted_mri_scan.pdf

# The Qm... hash is your CID
```

### 5.4 Encryption Before Upload

**Critical**: Encrypt medical data BEFORE uploading to IPFS.

```python
from cryptography.fernet import Fernet
import hashlib

def encrypt_file(file_path, key):
    """Encrypt a file using AES-256 via Fernet."""
    f = Fernet(key)
    with open(file_path, 'rb') as file:
        data = file.read()
    encrypted = f.encrypt(data)

    # Save encrypted file
    with open(file_path + '.enc', 'wb') as file:
        file.write(encrypted)

    # Compute hash of encrypted data (for blockchain anchor)
    record_hash = '0x' + hashlib.sha256(encrypted).hexdigest()

    return encrypted, record_hash

# Generate key (patient stores this securely)
key = Fernet.generate_key()
print(f"Encryption key (STORE THIS SAFELY): {key.decode()}")

encrypted, record_hash = encrypt_file('mri_scan.pdf', key)
print(f"Record hash for blockchain: {record_hash}")
```

---

## 6. Frontend Configuration

### 6.1 Build for Production

```bash
# If using a modern build tool (Vite, Webpack, etc.)
cd frontend
npm install
npm run build

# The build output goes to dist/ or build/
```

### 6.2 Configure API Base URL

Update `frontend_integration.js`:

```javascript
const CONFIG = {
  API_BASE_URL: "https://api.your-production-domain.com/api",
  // ... rest of config
};
```

Or use environment variables at build time:

```javascript
// Vite
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

// Create React App
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000/api";
```

### 6.3 MetaMask Integration (Production)

For production, replace the simulated fingerprint unlock with real wallet connection:

```javascript
// Using ethers.js
import { ethers } from "ethers";

async function connectWallet() {
  if (window.ethereum) {
    const provider = new ethers.BrowserProvider(window.ethereum);
    await provider.send("eth_requestAccounts", []);
    const signer = await provider.getSigner();
    const address = await signer.getAddress();
    return { provider, signer, address };
  } else {
    throw new Error("Please install MetaMask");
  }
}
```

### 6.4 Static Hosting Options

| Provider | Setup | Cost |
|----------|-------|------|
| **Vercel** | `npm i -g vercel && vercel --prod` | Free tier available |
| **Netlify** | `npm i -g netlify-cli && netlify deploy --prod` | Free tier available |
| **AWS S3 + CloudFront** | Upload to S3, configure CloudFront CDN | ~$5-20/month |
| **GitHub Pages** | Enable in repo settings | Free |
| **Firebase Hosting** | `firebase deploy` | Free tier available |

---

## 7. Cloud Deployment

### 7.1 Option A: AWS (Recommended for Production)

```bash
# Prerequisites
# - AWS CLI installed and configured
# - Docker installed

# 1. Build Docker image
cd backend
docker build -t healthchain-backend:latest .

# 2. Push to Amazon ECR
aws ecr get-login-password | docker login --username AWS --password-stdin YOUR_ECR_URL
docker tag healthchain-backend:latest YOUR_ECR_URL/healthchain-backend:latest
docker push YOUR_ECR_URL/healthchain-backend:latest

# 3. Deploy to ECS (using AWS Console or Terraform)
# Create ECS cluster, task definition, service
# Use Application Load Balancer for HTTPS

# 4. Configure RDS PostgreSQL
aws rds create-db-instance \
  --db-instance-identifier healthchain-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YOUR_SECURE_PASSWORD \
  --allocated-storage 20

# 5. Configure ElastiCache Redis
aws elasticache create-cache-cluster \
  --cache-cluster-id healthchain-redis \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --num-cache-nodes 1
```

**Dockerfile** for the backend:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables (override in production)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Run with Gunicorn (production WSGI server)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### 7.2 Option B: Heroku (Simplest)

```bash
# 1. Create Heroku app
heroku create your-healthchain-app

# 2. Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# 3. Add Redis addon
heroku addons:create heroku-redis:mini

# 4. Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set WEB3_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_KEY
heroku config:set CONTRACT_ADDRESS=0x...
heroku config:set CORS_ORIGINS=https://your-frontend-domain.com

# 5. Create Procfile
echo "web: gunicorn app:app" > Procfile

# 6. Deploy
git push heroku main

# 7. Scale dynos
heroku ps:scale web=2
```

### 7.3 Option C: Render (Good Free Tier)

```bash
# 1. Create render.yaml
# 2. Push to GitHub
# 3. Connect Render to your GitHub repo
# 4. Render auto-deploys on push
```

`render.yaml`:

```yaml
services:
  - type: web
    name: healthchain-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn -w 4 app:app"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        generateValue: true
      - key: WEB3_PROVIDER_URL
        sync: false
      - key: CONTRACT_ADDRESS
        sync: false

  - type: redis
    name: healthchain-redis
    ipAllowList: []

  - type: pserv
    name: healthchain-db
    env: docker
    dockerfilePath: ./postgres/Dockerfile
```

### 7.4 HTTPS and SSL

**Always use HTTPS in production.** Configure via:

- **AWS**: Certificate Manager (ACM) + Application Load Balancer
- **Cloudflare**: Free SSL + DDoS protection
- **Heroku**: Automatic SSL
- **Render**: Automatic SSL

### 7.5 Domain Configuration

```bash
# Example DNS records
A     api.your-domain.com    →  54.123.45.67  (ALB/EC2 IP)
CNAME www.your-domain.com    →  your-app.vercel.app
```

---

## 8. Testing Checklist

### 8.1 Pre-Deployment Tests

```bash
# Run all tests locally
cd backend
python -m pytest tests/ -v

# Test blockchain simulator
python blockchain_simulator.py  # Should run demo successfully

# Test Flask endpoints
python app.py &
./test_api.sh  # See below
```

### 8.2 Manual API Testing Script

Save as `test_api.sh`:

```bash
#!/bin/bash
set -e

BASE="http://localhost:5000/api"

echo "=== Health Check ==="
curl -s $BASE/health | jq .

echo ""
echo "=== Unlock Session ==="
UNLOCK=$(curl -s -X POST $BASE/auth/unlock -H "Content-Type: application/json" -d '{"method": "fingerprint"}')
echo $UNLOCK | jq .

echo ""
echo "=== Get Records ==="
curl -s $BASE/records | jq '.records | length'

echo ""
echo "=== Grant Access (initiate) ==="
GRANT=$(curl -s -X POST $BASE/access/grant -H "Content-Type: application/json" -d '{
  "provider_id": "dr-james-wilson",
  "record_ids": ["chest-xray"],
  "access_level": 1
}')
echo $GRANT | jq .
PENDING_ID=$(echo $GRANT | jq -r '.pending_id')

echo ""
echo "=== Check Pending Grants ==="
curl -s $BASE/access/pending | jq .

echo ""
echo "=== Wait for countdown... ==="
echo "Sleeping 60 seconds..."
sleep 60

echo ""
echo "=== Confirm Access ==="
curl -s -X POST $BASE/access/confirm -H "Content-Type: application/json" -d "{\"pending_id\": \"$PENDING_ID\"}" | jq .

echo ""
echo "=== Check Access ==="
curl -s "$BASE/access/check?provider_id=dr-james-wilson&record_id=chest-xray" | jq .

echo ""
echo "=== Get Audit Log ==="
curl -s "$BASE/audit/log?record_id=chest-xray" | jq '.total_entries'

echo ""
echo "=== Blockchain Status ==="
curl -s $BASE/blockchain/status | jq '.stats'

echo ""
echo "=== Blockchain Explorer ==="
curl -s $BASE/blockchain/explorer | jq '.total_blocks'

echo ""
echo "=== Verify Chain ==="
curl -s $BASE/blockchain/verify | jq .

echo ""
echo "=== Revoke Access ==="
curl -s -X POST $BASE/access/revoke -H "Content-Type: application/json" -d '{
  "provider_id": "dr-james-wilson",
  "record_id": "chest-xray"
}' | jq .

echo ""
echo "=== All tests passed! ==="
```

Make it executable: `chmod +x test_api.sh`

### 8.3 Production Testing Checklist

| # | Test | Expected Result |
|---|------|-----------------|
| 1 | Health check | Returns `{"status": "healthy"}` |
| 2 | Unlock with fingerprint | Returns session + blockchain tx |
| 3 | View records | Shows 3 records with access info |
| 4 | Grant access (initiate) | Creates pending state, returns tx hash |
| 5 | Grant access (confirm < 60s) | Returns error "still in pending" |
| 6 | Grant access (confirm after 60s) | Confirms on blockchain, shows tx hash |
| 7 | Cancel pending grant | Cancels without creating access |
| 8 | Revoke active access | Removes access, logs on blockchain |
| 9 | Check access (has access) | Returns `{"has_access": true}` |
| 10 | Check access (no access) | Returns `{"has_access": false}` |
| 11 | Audit log | Shows all events for a record |
| 12 | Blockchain explorer | Shows paginated blocks |
| 13 | Chain verification | Returns `{"valid": true}` |
| 14 | Session timeout | After 15 min, requires re-unlock |
| 15 | Session extend | Resets timer, extends expiry |
| 16 | HTTPS | All connections use TLS 1.2+ |
| 17 | CORS | Only allows your frontend domain |
| 18 | Rate limiting | 429 response after too many requests |
| 19 | Smart contract (testnet) | Contract deployed and verified |
| 20 | IPFS upload | File uploaded, CID returned, accessible |

### 8.4 Load Testing

```bash
# Install Locust
pip install locust

# Create locustfile.py
```

```python
from locust import HttpUser, task, between

class HealthChainUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_records(self):
        self.client.get("/api/records")

    @task(1)
    def blockchain_status(self):
        self.client.get("/api/blockchain/status")

    @task(1)
    def check_access(self):
        self.client.get("/api/access/check?provider_id=dr-sarah-chen&record_id=mri-scan")
```

Run:

```bash
locust -f locustfile.py --host http://localhost:5000
# Open http://localhost:8089 and start test with 100 users
```

---

## 9. Troubleshooting

### 9.1 Common Issues

#### Issue: `ModuleNotFoundError: No module named 'flask'`

```bash
# Solution: Activate virtual environment and install dependencies
cd backend
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows
pip install flask flask-cors
```

#### Issue: `Port 5000 already in use`

```bash
# Solution: Change the port
python app.py  # Or modify app.run(port=5001) in app.py
# Or kill existing process
lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000   # Windows
```

#### Issue: `CORS error in browser`

```bash
# Solution: Check CORS configuration in app.py
# Ensure your frontend origin is allowed
# In development: CORS(app, resources={r"/api/*": {"origins": "*"}})
# In production: Replace "*" with your actual domain
```

#### Issue: `Smart contract deployment fails with "insufficient funds"`

```bash
# Solution: Get more testnet ETH from faucets
# - https://sepoliafaucet.com/
# - https://faucet.quicknode.com/ethereum/sepolia
# - https://www.infura.io/faucet/sepolia
# Check balance: npx hardhat console --network sepolia
# > (await ethers.provider.getBalance("YOUR_ADDRESS")).toString()
```

#### Issue: `IPFS file not accessible`

```bash
# Solution: The IPFS node must be online or file must be pinned
# Check if file is pinned: ipfs pin ls | grep YOUR_CID
# If not pinned: ipfs pin add YOUR_CID
# For Pinata: check dashboard for pin status
```

#### Issue: `Transaction timeout`

```bash
# Solution: Increase gas price or check network congestion
# On Ethereum, use https://etherscan.io/gastracker
# On testnets, gas is usually free so any price works
```

### 9.2 Getting Help

| Resource | Link |
|----------|------|
| Hardhat Documentation | https://hardhat.org/docs |
| Flask Documentation | https://flask.palletsprojects.com/ |
| Web3.py Documentation | https://web3py.readthedocs.io/ |
| Ethereum Developer Docs | https://ethereum.org/developers/ |
| OpenZeppelin Contracts | https://docs.openzeppelin.com/ |
| IPFS Documentation | https://docs.ipfs.tech/ |
| Pinata Support | https://pinata.cloud/ |
| Infura Support | https://support.infura.io/ |

---

## Appendix A: Quick Reference

### A.1 File Structure

```
healthcare-blockchain-access/
├── smart_contracts/
│   └── HealthAccessControl.sol
├── backend/
│   ├── app.py
│   ├── blockchain_simulator.py
│   ├── config.py
│   ├── requirements.txt
│   └── Dockerfile
├── integration/
│   └── frontend_integration.js
├── frontend/
│   ├── index.html          (from prototype)
│   ├── src/
│   └── package.json
├── architecture.md
├── deployment/
│   └── DEPLOY.md
├── README.md
└── .env                    (never commit!)
```

### A.2 Environment Variables Summary

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `super-secret-change-me` |
| `WEB3_PROVIDER_URL` | Ethereum RPC endpoint | `https://sepolia.infura.io/v3/...` |
| `CHAIN_ID` | Network chain ID | `11155111` (Sepolia) |
| `CONTRACT_ADDRESS` | Deployed contract address | `0x...` |
| `PATIENT_PRIVATE_KEY` | Service wallet private key | `0x...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `REDIS_URL` | Redis connection string | `redis://...` |
| `CORS_ORIGINS` | Allowed frontend domains | `https://example.com` |
| `IPFS_API_KEY` | IPFS service API key | `...` |
| `IPFS_SECRET_KEY` | IPFS service secret | `...` |
| `SESSION_TIMEOUT_SECONDS` | Session duration | `900` |

### A.3 Network Chain IDs

| Network | Chain ID | Currency |
|---------|----------|----------|
| Ethereum Mainnet | 1 | ETH |
| Ethereum Sepolia | 11155111 | SepoliaETH |
| Ethereum Goerli | 5 | GoerliETH (deprecated) |
| Polygon Mainnet | 137 | MATIC |
| Polygon Mumbai | 80001 | TestMATIC |
| Arbitrum One | 42161 | ETH |
| Arbitrum Goerli | 421613 | TestETH |
| Optimism | 10 | ETH |
| Optimism Goerli | 420 | TestETH |
| Hardhat Local | 1337 | ETH (fake) |
| Ganache Local | 1337 | ETH (fake) |

---

**End of Deployment Guide**
