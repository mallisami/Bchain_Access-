# Healthcare Blockchain Access Control System

## Secure, Patient-Owned Medical Record Access Management

**Version:** 1.0.0  
**Status:** Research Prototype (Not for Production Use)  
**Licenses:** MIT (Code), CC BY 4.0 (Data)  
**Zenodo DOI:** [10.5281/zenodo.21345578](https://doi.org/10.5281/zenodo.21345578)  

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Overview](#architecture-overview)
3. [Quick Start](#quick-start)
4. [File Structure](#file-structure)
5. [API Documentation](#api-documentation)
6. [Blockchain Simulation Details](#blockchain-simulation-details)
7. [Screenshots Description](#screenshots-description)
8. [Future Work](#future-work)
9. [Contributing](#contributing)
10. [License](#license)

---

## Project Overview

This project is a **complete healthcare access control system** built on an EVM-compatible blockchain backend (Solidity smart contracts) with an educational Python fallback. It demonstrates how patients can securely manage who has access to their medical records using blockchain technology — without requiring patients to understand blockchain jargon.

### Key Features

- **Patient-Controlled Access**: Patients decide which doctors can see which records, and for how long.
- **Blockchain-Backed Audit Trail**: Every access action is permanently recorded in a tamper-evident blockchain log.
- **60-Second Safety Countdown**: A time-locked confirmation window prevents accidental access grants.
- **Accessibility First**: WCAG 2.1 Level AA compliant with full screen reader support, keyboard navigation, and plain-language explanations.
- **Educational Fallback Engine**: A local Python-based blockchain engine demonstrating SHA-256 hashing, proof-of-work, Merkle trees, and digital signatures when running offline.
- **Immutable Record Hashes**: Medical data stays off-chain (IPFS); only cryptographic hashes are anchored on-chain for integrity verification.

### Why This Matters

Medical records are among the most sensitive personal data. Current electronic health record (EHR) systems often store access logs in centralized databases that can be altered or deleted. This prototype demonstrates a **patient-centric, transparent alternative** where:

- Patients own and control their data
- Every access is permanently recorded and auditable
- Providers cannot secretly access records without patient consent
- Data integrity is cryptographically verifiable

---

## Architecture Overview

The system is built in four layers:

```
┌──────────────────────────────────────────┐
│  USER INTERFACE (HTML/CSS/JS)            │
│  • Accessible, patient-friendly design     │
│  • Fingerprint unlock simulation           │
│  • 60-second countdown confirmation        │
│  • ARIA live regions, keyboard shortcuts   │
└────────────────────┬───────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼───────────────────────┐
│  FRONTEND INTEGRATION (JavaScript)         │
│  • API client with retries & timeouts      │
│  • Blockchain status polling (5s)          │
│  • Transaction hash display & explorer     │
│  • Error handling with ARIA alerts         │
└────────────────────┬───────────────────────┘
                     │
┌────────────────────▼───────────────────────┐
│  FLASK BACKEND (Python)                    │
│  • REST API endpoints                      │
│  • Session management (15-min timeout)     │
│  • In-memory fallback ledger state         │
│  • CORS configuration                      │
└────────────────────┬───────────────────────┘
                     │
┌────────────────────▼───────────────────────┐
│  EDUCATIONAL BLOCKCHAIN ENGINE (Python)     │
│  • Block class with SHA-256 + PoW          │
│  • Blockchain class with chain + mempool   │
│  • Transaction class with digital sigs     │
│  • Wallet class with keypair generation    │
│  • Merkle tree construction                │
└────────────────────┬───────────────────────┘
                     │
┌────────────────────▼───────────────────────┐
│  SMART CONTRACT (Solidity)                 │
│  • Record hash registration                │
│  • Access grant with pending state           │
│  • Access revocation (immediate)           │
│  • Immutable audit log                       │
│  • Events for off-chain indexing             │
└────────────────────────────────────────────┘
```

For a detailed architecture document, see **[architecture.md](architecture.md)**.

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** (optional, for frontend build tools)
- **Git**

### 1. Clone and Navigate

```bash
git clone https://github.com/your-org/healthcare-blockchain-access.git
cd healthcare-blockchain-access
```

### 2. Set Up Python Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install flask flask-cors
```

### 3. Run the Backend

```bash
python app.py
```

You should see:

```
============================================================
HEALTHCARE BLOCKCHAIN ACCESS CONTROL - BACKEND
============================================================
Patient wallet: 0x...
Genesis block: 0004...
Starting Flask server on http://localhost:5000
============================================================
```

### 4. Test the API

Open a new terminal:

```bash
# Health check
curl http://localhost:5000/api/health

# Unlock session
curl -X POST http://localhost:5000/api/auth/unlock \
  -H "Content-Type: application/json" \
  -d '{"method": "fingerprint"}'

# Get records
curl http://localhost:5000/api/records

# Get blockchain status
curl http://localhost:5000/api/blockchain/status
```

### 5. View the Frontend

The frontend is a static HTML file. You can open it directly in a browser, or serve it with a simple HTTP server:

```bash
# From the project root
# If you have the original prototype HTML:
# Copy the prototype HTML to the project
cp path/to/prototype/index.html frontend/index.html

# Serve with Python's built-in HTTP server
cd frontend
python3 -m http.server 3000

# Open http://localhost:3000 in your browser
```

### 6. Connect Frontend to Backend

Include the integration script in your HTML:

```html
<!-- After the existing prototype script -->
<script src="../integration/frontend_integration.js"></script>
```

The integration script will override the original prototype's in-memory functions with API calls to the backend.

---

## File Structure

```
bchain-access-prototype/
│
├── smart_contracts/
│   ├── contracts/
│   │   └── HealthAccessControl.sol      # Solidity smart contract (Ethereum/EVM)
│   ├── test/
│   │   ├── HealthAccessControl.test.js  # Mocha/Chai integration test suite
│   │   └── gas-report.txt               # Raw EVM gas benchmarks
│   ├── scripts/
│   │   └── deploy.js                    # Contract deployment script
│   └── hardhat.config.js                # Hardhat configurations (Sepolia + local)
│
├── backend/
│   ├── app.py                           # Flask REST API server
│   ├── blockchain_simulator.py          # Educational fallback blockchain engine
│   └── config.py                        # Backend configurations
│
├── frontend/
│   └── index.html                       # Patient UI prototype
│
├── integration/
│   └── frontend_integration.js          # API integration script
│
├── data/                                # De-identified expert-study evaluation data
│   ├── sus_scores.csv                   # SUS questionnaire responses
│   ├── cognitive_walkthrough.csv        # Walkthrough task durations, errors, difficulties
│   ├── accessibility_questionnaire.csv  # Accessibility Likert responses
│   └── heuristic_ratings.csv            # Original + re-rated heuristic severity scores
│
├── analysis/                            # Static analysis & evaluation scripts
│   ├── compute_results.py               # Reproducibility script
│   ├── slither_report.json              # Full Slither JSON static analysis report
│   └── wcag/                            # Automated accessibility reports
│       ├── lighthouse_report.json       # Google Lighthouse audit export
│       ├── wave_report.json             # WAVE audit export
│       ├── axe_report.json              # Axe DevTools audit export
│       └── contrast_check.csv           # 29 color contrast pair ratio audit
│
├── docs/
│   ├── instruments.md                   # Documented questionnaires & walkthrough script
│   └── instruments.pdf                  # Blank PDF version of evaluation instruments
│
├── LICENSE                              # Licenses (MIT for code, CC BY 4.0 for data)
├── CITATION.cff                         # Academic citation definition
├── REPRODUCE.md                         # Reproducibility guide (claims reproduction commands)
└── README.md                            # Main readme file
```

---

## API Documentation

All endpoints are prefixed with `/api` and return JSON.

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | `GET` | Health check — returns service status |
| `/api/auth/unlock` | `POST` | Simulate biometric unlock, create session |
| `/api/auth/status` | `GET` | Check if session is active and time remaining |
| `/api/auth/extend` | `POST` | Extend session ("Keep me signed in") |

**Example — Unlock Session:**

```bash
curl -X POST http://localhost:5000/api/auth/unlock \
  -H "Content-Type: application/json" \
  -d '{"method": "fingerprint"}'
```

**Response:**

```json
{
  "success": true,
  "message": "Session unlocked successfully",
  "session": {
    "active": true,
    "started_at": "2026-06-29T10:30:00+00:00",
    "expires_at": "2026-06-29T10:45:00+00:00",
    "duration_seconds": 900
  },
  "patient": {
    "id": "elena-vasquez-001",
    "name": "Elena Vasquez",
    "date_of_birth": "1985-03-15",
    "blockchain_address": "0x..."
  },
  "blockchain": {
    "tx_hash": "0x...",
    "block_number": 2,
    "gas_used": 35420,
    "gas_cost_eth": 0.000000708
  }
}
```

### Records

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/records` | `GET` | Get all patient records with access info |
| `/api/records/{id}` | `GET` | Get a specific record |

### Access Control

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/access/grant` | `POST` | Initiate access grant (pending 60s) |
| `/api/access/confirm` | `POST` | Confirm grant after countdown |
| `/api/access/cancel` | `POST` | Cancel pending grant |
| `/api/access/revoke` | `POST` | Revoke active access immediately |
| `/api/access/check` | `GET` | Check if provider has access to record |
| `/api/access/pending` | `GET` | List all active pending grants |

**Example — Grant Access:**

```bash
curl -X POST http://localhost:5000/api/access/grant \
  -H "Content-Type: application/json" \
  -d '{
    "provider_id": "dr-james-wilson",
    "record_ids": ["chest-xray"],
    "access_level": 1
  }'
```

**Response:**

```json
{
  "success": true,
  "pending_id": "pending_a1b2c3d4",
  "pending_until": 1751198170,
  "countdown_seconds": 60,
  "tx_hashes": ["0x..."],
  "message": "Access grant initiated for Dr. James Wilson. Confirm within 60 seconds."
}
```

### Audit

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/audit/log` | `GET` | Get complete audit trail for a record |

**Example:**

```bash
curl "http://localhost:5000/api/audit/log?record_id=mri-scan"
```

**Response:**

```json
{
  "record_id": "mri-scan",
  "record_hash": "0x...",
  "audit_entries": [
    {
      "action": "RECORD_REGISTERED",
      "timestamp": 1751198100,
      "timestamp_iso": "2026-06-29T10:00:00+00:00",
      "details": "MRI Brain Scan registered by patient"
    },
    {
      "action": "GRANT_CONFIRMED",
      "timestamp": 1751198200,
      "timestamp_iso": "2026-06-29T10:10:00+00:00",
      "details": "Access granted to Dr. Sarah Chen"
    }
  ],
  "total_entries": 5
}
```

### Blockchain Explorer

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/blockchain/status` | `GET` | Blockchain connection and chain stats |
| `/api/blockchain/explorer` | `GET` | Paginated block explorer |
| `/api/blockchain/block/{hash}` | `GET` | Block detail by hash |
| `/api/blockchain/transaction/{hash}` | `GET` | Transaction detail by hash |
| `/api/blockchain/verify` | `GET` | Verify chain integrity |

---

## Educational Fallback Ledger Details

### Dual-Ledger Framework

The Python `blockchain_simulator.py` implements a simplified but fully functional blockchain ledger that acts as an educational model and fallback database when the live EVM network is offline.

| Feature | Bitcoin | Ethereum | Our Fallback Engine |
|---------|---------|----------|---------------------|
| **Hash Function** | SHA-256 | Keccak-256 | SHA-256 |
| **Consensus** | PoW (ASICs) | PoS (since 2022) | Simple PoW (CPU) |
| **Block Time** | ~10 min | ~12 sec | ~0.1-1 sec (difficulty 3) |
| **Merkle Trees** | Yes (TXs) | Yes (TXs + receipts) | Yes (TXs) |
| **Difficulty** | Dynamic | N/A (PoS) | Configurable (default 3) |
| **Signatures** | ECDSA secp256k1 | ECDSA secp256k1 | SHA-256 (local engine) |
| **Smart Contracts** | No | Yes (EVM) | No (routed to EVM or cached) |
| **Gas** | Satoshis/byte | Gas units | Local engine gas estimation |

### How Mining Works

```python
def mine(self, difficulty: int) -> str:
    target = "0" * difficulty  # e.g., "000" for difficulty 3
    while True:
        self.hash = self.compute_hash()
        if self.hash.startswith(target):
            break
        self.nonce += 1
    return self.hash
```

A block hash of `000a3f2...` means the miner found a nonce that makes SHA-256(block_data) start with 3 zeros. The higher the difficulty, the more computational work is required.

### Merkle Trees in Action

Every block's transactions are hashed into a Merkle tree:

```
        [Merkle Root]  ← included in block hash
        /           \
  [Hash AB]       [Hash CD]
   /     \         /     \
[Hash A] [Hash B] [Hash C] [Hash D]
   |        |        |        |
  Tx1      Tx2      Tx3      Tx4
```

Changing any transaction (e.g., Tx2 → Tx2') changes Hash B → Hash AB → Merkle Root → Block Hash → breaks the chain. This is why blockchains are called "immutable."

### Running the Local Engine Demo

```bash
cd backend
python blockchain_simulator.py
```

Output:

```
============================================================
LOCAL BLOCKCHAIN ENGINE - DEMONSTRATION
============================================================

Patient Wallet: 0x...
Provider Wallet: 0x...

Genesis block created: 000...

Transaction added to mempool: 0x...
Gas estimate: 35420 gas units

Block 1 mined: 000...
Merkle root: 0x...
Nonce: 12345
Transactions in block: 2

Chain valid: True
Chain stats: {'chain_length': 2, 'difficulty': 3, ...}

============================================================
DEMONSTRATION COMPLETE
============================================================
```

---

## Screenshots Description

### 1. Authentication Screen

The patient sees a friendly "Simulate Fingerprint Unlock" button with a fingerprint icon. The button is large (44px minimum touch target), clearly labeled, and has a focus ring. Below the icon, text explains: "Press Enter or Space to activate." This replaces the need for a complex password.

### 2. Records Dashboard

After unlocking, the patient sees their medical records with clear status badges:
- **MRI Brain Scan**: Shows "Active" badge with a list of providers who have access (Dr. Sarah Chen, Dr. Michael Torres). Each provider has a "Remove Access" button. The record hash is displayed in a monospace font for transparency.
- **Blood Work Panel**: Shows "Private" badge with the text: "No one has access to this record. Only you can see it."

A system status banner reads: "Your records are secured on the blockchain."

### 3. Grant Access Workflow — Step 1: Select

The patient selects:
- A provider from a dropdown (Dr. James Wilson — Radiology)
- Which records to share (checked: Chest X-Ray)

A tooltip icon (?) next to "Choose a healthcare provider" explains: "A healthcare provider is a doctor, clinic, or hospital that needs to see your records to give you care."

### 4. Grant Access Workflow — Step 2: Review

A review box shows:
- **Records**: Chest X-Ray
- **With**: Dr. James Wilson, Radiology
- **Access level**: View only — they cannot change or download your records

A consequence statement in teal: "What this means: Dr. James Wilson will be able to view your Chest X-Ray when providing your care. They will not be able to edit, delete, or download them. You can remove their access at any time. This action will be recorded on the blockchain with a permanent transaction hash."

### 5. Grant Access Workflow — Step 3: Confirm (60-Second Countdown)

A large countdown timer displays "60" in bold gold text. Below it: "seconds remaining to confirm."

A transaction hash is displayed with a link: "View this transaction on the blockchain explorer."

Two buttons: "Confirm — Grant Access" (primary) and "Cancel This Request" (secondary).

The patient can press Escape at any time to cancel.

### 6. Success State

A green status banner: "Access granted successfully on blockchain. Dr. James Wilson can now view your Chest X-Ray."

The transaction hash is shown again with a blockchain explorer link.

A secondary button: "Grant Access to Someone Else" resets the workflow.

### 7. Audit Log Modal

Clicking "View audit log for this record" opens a modal showing:
- All blockchain events (GRANT_INITIATE, GRANT_CONFIRM, ACCESS_ATTEMPT) with block numbers and TX hashes
- All application events (RECORD_REGISTERED, GRANT_CONFIRMED, REVOKE) with timestamps

### 8. Blockchain Explorer

The footer includes a link to "View Blockchain Explorer" which shows a paginated list of blocks:
- Block #0 (Genesis): `0000...`
- Block #1: `000a...` with 2 transactions
- Block #2: `000b...` with 1 transaction

---

## Future Work

### Short Term (Next 3 Months)

1. **MetaMask Integration**: Replace the simulated fingerprint unlock with real wallet-based authentication using Web3.js or ethers.js.
2. **Real Smart Contract Deployment**: Deploy `HealthAccessControl.sol` to Sepolia testnet and connect the backend via Web3.py.
3. **Database Persistence**: Replace in-memory Python dictionaries with PostgreSQL for records, grants, and audit logs.
4. **Redis Session Caching**: Use Redis for session store and rate limiting.
5. **IPFS Integration**: Upload encrypted medical files to IPFS and store the CID in the smart contract.

### Medium Term (Next 6 Months)

6. **Zero-Knowledge Proofs**: Implement zk-SNARKs to allow providers to prove they have access without revealing which records or when.
7. **Layer 2 Scaling**: Move from Ethereum mainnet to Polygon or Arbitrum for 100x lower gas costs.
8. **Mobile App**: Build a React Native or Flutter app for patients to manage access on their phones.
9. **Provider Portal**: Build a separate interface for doctors to request access (creating a patient notification).
10. **AI Anomaly Detection**: Use machine learning to detect unusual access patterns (e.g., a provider accessing records at 3 AM from an unusual location).

### Long Term (Next 12+ Months)

11. **Decentralized Identity (DID)**: Use W3C DID standards for provider identity verification.
12. **Multi-Chain Support**: Deploy on multiple chains with cross-chain bridges for access verification.
13. **NFT-Based Records**: Represent each medical record as a Soulbound Token (SBT) that the patient owns.
14. **Patient-Controlled Encryption**: Use threshold encryption (Shamir's Secret Sharing) where the patient holds key shards.
15. **Regulatory Compliance**: HIPAA compliance audit, GDPR compliance for EU patients, FDA clearance for clinical use.

---

## Contributing

This is a research prototype. Contributions are welcome in the following areas:

- **Security Audits**: Review the smart contract for vulnerabilities
- **Accessibility Testing**: Test with screen readers (NVDA, JAWS, VoiceOver)
- **Performance Optimization**: Improve the blockchain simulator's mining speed
- **Documentation**: Improve deployment guides and API docs
- **UI/UX**: Design improvements for the patient interface
- **Translations**: Localize the interface for non-English speakers

### Development Setup

```bash
# Fork and clone
git clone https://github.com/your-username/healthcare-blockchain-access.git
cd healthcare-blockchain-access

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# Run tests
python -m pytest tests/ -v

# Smart contracts (if you have Hardhat set up)
cd ../contract-project
npx hardhat test
```

---

## Licenses

This repository is dual-licensed:
* **Code and Software** (smart contracts, backend app, integration layer, scripts): Licensed under the **MIT License**. See the [LICENSE](LICENSE) file for the full text.
* **Evaluation and Study Data** (CSV files inside the `data/` directory, including SUS and walkthrough metrics): Licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**. See the [LICENSE](LICENSE) file for details.

---

## Citation

If you use BCHAIN-ACCESS in your academic work, please cite it using the following format (or import the `CITATION.cff` metadata):

```bibtex
@article{yaqub2026bchain,
  title={Empowering Accessibility: BCHAIN-ACCESS, an Accessibility-by-Design Framework Integrating Blockchain and HCI for Healthcare Interfaces},
  author={Yaqub, Nadeem and Ullah, Muhammad Sami and Hussain, Imtiaz and Aleshaiker, Sama},
  journal={PeerJ Computer Science},
  volume={12},
  pages={e11155111},
  year={2026},
  publisher={PeerJ},
  doi={10.5281/zenodo.21345578}
}
```

---

**Disclaimer**: This is a research prototype and is NOT intended for production use with real patient data. It is designed for educational purposes and to demonstrate blockchain concepts in healthcare. Always consult with legal, regulatory, and security professionals before deploying any healthcare system.

**HIPAA Notice**: This prototype does not store real medical data. In a production system, all Protected Health Information (PHI) must be encrypted at rest and in transit, and the system must comply with HIPAA, GDPR, and other applicable regulations.
