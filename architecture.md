# Architecture Document

## Healthcare Blockchain Access Control System

**Version:** 1.0.0  
**Date:** 2026-06-29  
**Status:** Research Prototype  

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  HTML5 + CSS3 + JavaScript (Accessibility-First Design)                    │   │
│  │  • WCAG 2.1 Level AA compliant                                               │   │
│  │  • ARIA live regions, keyboard navigation, screen reader support            │   │
│  │  • Fingerprint unlock simulation (Abstracted Authentication Design)         │   │
│  │  • Confirmatory Interaction Design (CID) for grants/revocations             │   │
│  │  • Plain Text Descriptions (PTD) for non-technical users                    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                                │
│                                    ▼ HTTP/REST API (CORS-enabled)                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  FRONTEND INTEGRATION LAYER (frontend_integration.js)                        │   │
│  │  • API client with retry logic, timeout handling                             │   │
│  │  • Blockchain status polling (5-second intervals)                            │   │
│  │  • Transaction hash display with explorer links                              │   │
│  │  • Error handling with user-friendly messages                                 │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              APPLICATION LAYER                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  FLASK BACKEND (Python) — app.py                                           │   │
│  │  • REST API endpoints for all frontend operations                          │   │
│  │  • Session management (15-minute expiry, 2-minute warning)                   │   │
│  │  • In-memory state simulation of the smart contract                         │   │
│  │  • CORS configuration for cross-origin requests                              │   │
│  │  • Gas cost simulation for educational purposes                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                                │
│                                    ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  BLOCKCHAIN SIMULATOR (Python) — blockchain_simulator.py                     │   │
│  │  • Block class with SHA-256 hashing, nonce, Merkle root                     │   │
│  │  • Blockchain class with chain, mempool, difficulty                          │   │
│  │  • Transaction class with digital signatures (SHA-256-based)                 │   │
│  │  • Wallet class with keypair generation and signing                          │   │
│  │  • Proof-of-work mining simulation                                           │   │
│  │  • Merkle tree construction and verification                                 │   │
│  │  • Chain validation (hash linkage, difficulty target)                        │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼ (In production, this would be Web3/JSON-RPC)
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              SMART CONTRACT LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  ETHEREUM SMART CONTRACT — HealthAccessControl.sol (Solidity ^0.8.19)        │   │
│  │  • Patient record hash registration (not full data)                          │   │
│  │  • Access grant management with pending state (60-second time-lock)          │   │
│  │  • Access revocation (immediate, no pending)                                 │   │
│  │  • Access check with expiration support                                      │   │
│  │  • Immutable audit log on-chain                                              │   │
│  │  • Events: GrantAccessInitiated, GrantAccessConfirmed, RevokeAccess,        │   │
│  │          AccessAttempt, GrantAccessCancelled, RecordRegistered               │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼ (In production, via IPFS gateway or API)
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              OFF-CHAIN STORAGE LAYER                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  IPFS / HIPAA-COMPLIANT STORAGE (Simulated in prototype)                    │   │
│  │  • Encrypted medical images, PDFs, lab results                               │   │
│  │  • Content-addressed via IPFS hashes (CID)                                   │   │
│  │  • Only hashes stored on-chain; actual data never touches blockchain          │   │
│  │  • Encryption at rest (patient controls keys)                                 │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Descriptions

### 2.1 User Interface Layer

The UI is a single-page HTML application built with accessibility as the primary constraint. It serves patients who may have limited technical literacy or physical disabilities.

| Feature | Implementation | Rationale |
|---------|---------------|-----------|
| **Fingerprint Unlock** | Button with SVG icon, simulated 800ms delay | Abstracted Authentication Design (AAD) — replaces complex passwords |
| **60-Second Countdown** | Visual timer + ARIA announcements | Confirmatory Interaction Design (CID) — prevents accidental grants |
| **ARIA Live Regions** | Two live regions (`polite` + `assertive`) | Screen reader users hear status changes without losing focus |
| **Skip Navigation** | First focusable element on page | WCAG 2.4.1 — bypass blocks of repeated content |
| **Reduced Motion** | `@media (prefers-reduced-motion)` | Respects user system preferences |
| **High Contrast** | `@media (prefers-contrast: high)` | Supports Windows High Contrast Mode |
| **Keyboard Shortcuts** | Escape cancels pending grants | Power users and screen reader users benefit |

### 2.2 Frontend Integration Layer

This JavaScript module (`frontend_integration.js`) is the bridge between the accessible UI and the blockchain backend. It replaces the original prototype's in-memory state with API calls.

**Key Responsibilities:**
- **API Client**: All REST calls to Flask backend with timeout (10s), retries (2), and exponential backoff
- **Polling**: Every 5 seconds, fetches blockchain status to display connection health
- **Transaction Display**: After each grant, shows the transaction hash with a link to the blockchain explorer
- **Error Handling**: Network errors show user-friendly messages in an ARIA alert region
- **State Management**: Tracks session, pending grants, and blockchain connection status

### 2.3 Flask Backend (`app.py`)

The Python Flask application serves as the API gateway and business logic layer. In the prototype, it simulates blockchain operations using the in-memory blockchain simulator. In production, it would connect to a real Ethereum node via Web3.py.

**Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check for monitoring |
| `/api/auth/unlock` | POST | Simulate biometric unlock, create session |
| `/api/auth/status` | GET | Check session status and remaining time |
| `/api/auth/extend` | POST | Extend session ("Keep me signed in") |
| `/api/records` | GET | Get all patient records with access info |
| `/api/records/{id}` | GET | Get specific record details |
| `/api/access/grant` | POST | Initiate access grant (pending state) |
| `/api/access/confirm` | POST | Confirm grant after countdown |
| `/api/access/cancel` | POST | Cancel pending grant |
| `/api/access/revoke` | POST | Revoke active access immediately |
| `/api/access/check` | GET | Check if provider has access to record |
| `/api/access/pending` | GET | List all pending grants with countdown |
| `/api/audit/log` | GET | Get complete audit trail for a record |
| `/api/blockchain/status` | GET | Blockchain connection and chain stats |
| `/api/blockchain/explorer` | GET | Paginated block explorer |
| `/api/blockchain/block/{hash}` | GET | Block detail by hash |
| `/api/blockchain/transaction/{hash}` | GET | Transaction detail by hash |
| `/api/blockchain/verify` | GET | Verify chain integrity |
| `/api/providers` | GET | List all registered healthcare providers |

### 2.4 Blockchain Simulator (`blockchain_simulator.py`)

A full educational blockchain implementation in Python. It demonstrates the same concepts that power Bitcoin and Ethereum but in a simplified, transparent form.

**Classes:**

| Class | Description |
|-------|-------------|
| `Transaction` | Signed transaction with hash, gas estimation, type enum |
| `Block` | Block with index, timestamp, transactions, previous hash, nonce, hash, Merkle root |
| `Blockchain` | Chain of blocks, mempool, difficulty, mining, validation |
| `Wallet` | Keypair generation, transaction signing, signature verification |

**Key Algorithms:**

1. **SHA-256 Hashing**: All block hashes and transaction hashes use SHA-256 (same as Bitcoin)
2. **Proof of Work**: Find a nonce such that `SHA256(block_data)` starts with N zeros
3. **Merkle Tree**: Binary hash tree over transactions — changing any transaction changes the root
4. **Chain Validation**: Verify every block's hash meets difficulty and links to previous block

### 2.5 Smart Contract (`HealthAccessControl.sol`)

A Solidity smart contract that would run on Ethereum (or any EVM-compatible chain like Polygon, Arbitrum, or Avalanche C-Chain).

**Key Design Decisions:**

- **Only hashes on-chain**: Full medical data is too large and sensitive for Ethereum storage. The contract stores SHA-256 hashes that can verify data integrity from off-chain storage.
- **Time-locked grants**: The 60-second `pendingUntil` mechanism prevents accidental grants. This mirrors the frontend's countdown.
- **Immutable audit log**: Every action creates an `AuditEntry` that can never be deleted. This is critical for HIPAA compliance.
- **Access expiration**: Grants can have an optional expiration timestamp, useful for temporary consultations.
- **Events**: All state changes emit events, allowing off-chain indexers (like The Graph) to build efficient query layers.

---

## 3. Data Flow Diagrams

### 3.1 Unlock Session

```
User presses Fingerprint Button
        │
        ▼
┌─────────────────┐
│  Frontend JS    │  Simulate fingerprint, show loading state
│  (unlockSession)  │  Set aria-busy="true" on button
└────────┬────────┘
         │ POST /api/auth/unlock
         ▼
┌─────────────────┐
│  Flask Backend  │  Create session (15 min expiry)
│  (app.py)       │  Create blockchain transaction (SESSION_UNLOCK)
│                 │  Mine block to confirm auth
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Blockchain Sim │  Add auth transaction to mempool
│  (blockchain_    │  Mine block with PoW
│   simulator.py)   │  Update chain state
└────────┬────────┘
         │ Response: { session, blockchain tx_hash, gas_used }
         ▼
┌─────────────────┐
│  Frontend JS    │  Update UI: show unlocked state
│                 │  Display blockchain TX hash
│                 │  Start blockchain polling (5s interval)
│                 │  Load records from backend
│                 │  Announce to screen reader
└─────────────────┘
```

### 3.2 View Records

```
User session is active
        │
        ▼
┌─────────────────┐
│  Frontend JS    │  Call GET /api/records
│  (loadRecords)  │  (called automatically after unlock)
└────────┬────────┘
         │ GET /api/records
         ▼
┌─────────────────┐
│  Flask Backend  │  Look up records_db for patient
│  (app.py)       │  For each record, query access_grants_db
│                 │  Filter active grants (check expiration)
│                 │  Build response with access info
└────────┬────────┘
         │ Response: { records: [{ ...access_grants }] }
         ▼
┌─────────────────┐
│  Frontend JS    │  Render record cards with:
│  (updateDash)   │  • Record hash (truncated)
│                 │  • Active providers with names/specialties
│                 │  • Grant dates and TX hashes
│                 │  • "Remove Access" buttons
│                 │  • "View Audit Log" links
└─────────────────┘
```

### 3.3 Grant Access (Full Flow)

```
User selects provider + records, clicks "Review My Choices"
        │
        ▼
┌─────────────────┐
│  Frontend JS    │  Gather selections, validate at least 1 record
│  (proceedToRev) │  Show review screen with Plain Text Description
│                 │  "What this means: Dr. X will be able to view..."
└────────┬────────┘
         │ User clicks "Yes, Grant Access"
         ▼
┌─────────────────┐
│  Frontend JS    │  POST /api/access/grant
│  (proceedToConf)│  { provider_id, record_ids, access_level: 1 }
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Flask Backend  │  Create pending grant entry (60s countdown)
│  (app.py)       │  For each record, create blockchain transaction
│                 │  TxType: GRANT_INITIATE
│                 │  Mine block to confirm transaction
│                 │  Return pending_id, tx_hashes, countdown
└────────┬────────┘
         │ Response: { pending_id, countdown_seconds, tx_hashes }
         ▼
┌─────────────────┐
│  Frontend JS    │  Show Stage 3: Countdown timer (60 seconds)
│  (Stage 3)      │  Display TX hash with blockchain explorer link
│                 │  Start countdown interval (1 second)
│                 │  Every 10s: announce to screen reader
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
Cancel    Confirm (after 60s)
│              │
▼              ▼
POST /api/   POST /api/access/confirm
access/cancel    { pending_id }
│              │
▼              ▼
Mark pending    Move grant from pending to active
as cancelled    Update access_grants_db
Log on chain    Create GRANT_CONFIRM transaction
                Mine block
                Add to audit log
                Refresh dashboard
```

### 3.4 Revoke Access

```
User clicks "Remove Access" on a record card
        │
        ▼
Browser confirm() dialog
"Are you sure...? They will no longer be able to view this record."
        │
   ┌────┴────┐
   │         │
Cancel    OK
│              │
▼              ▼
No change   POST /api/access/revoke
            { provider_id, record_id }
            │
            ▼
        ┌─────────────────┐
        │  Flask Backend  │  Mark grant as "revoked"
        │  (app.py)       │  Create REVOKE blockchain transaction
        │                 │  Mine block
        │                 │  Add to audit log
        └────────┬────────┘
                 │ Response: { tx_hash, message }
                 ▼
            ┌─────────────────┐
            │  Frontend JS    │  Announce to screen reader
            │                 │  Show success banner with TX hash
            │                 │  Refresh dashboard from backend
            └─────────────────┘
```

---

## 4. Blockchain Layer Details

### 4.1 How the Prototype Differs from the Pure HTML Demo

| Aspect | Pure HTML Demo | Blockchain-Integrated System |
|--------|---------------|---------------------------|
| **State Storage** | JavaScript variables | Python in-memory DB + blockchain simulator |
| **Persistence** | Lost on page refresh | Survives backend restart (in-memory for now) |
| **Transaction Logging** | Console.log only | Blockchain blocks with Merkle roots |
| **Immutability** | None — state can be edited via dev tools | SHA-256 chain + PoW makes tampering detectable |
| **Audit Trail** | None | Immutable audit log on "chain" |
| **Grant Confirmation** | Client-side countdown only | 60-second pending + blockchain tx confirmation |
| **Transaction Hashes** | Fake strings | Real SHA-256 hashes computed from transaction data |
| **Provider Identity** | String IDs | Cryptographic addresses (wallet public keys) |
| **Data Integrity** | None | Record hashes anchor off-chain data to on-chain integrity |

### 4.2 Block Structure

```json
{
  "index": 5,
  "timestamp": 1751198110.42,
  "transactions": [
    {
      "from_address": "0x...",
      "to_address": "0x...",
      "tx_type": "grant_initiate",
      "data": { "provider_id": "dr-sarah-chen", ... },
      "tx_hash": "0x...",
      "signature": "0x...",
      "gas_used": 35420
    }
  ],
  "previous_hash": "0x0000a3f2...",
  "merkle_root": "0x8b2c...",
  "nonce": 12345,
  "hash": "0x0000f7a2...",
  "difficulty": 3
}
```

### 4.3 Proof of Work

The simulator uses a simple PoW where the target is a number of leading zeros:

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

On a typical laptop, difficulty 3 takes ~0.01-0.5 seconds. Difficulty 4 takes 0.1-5 seconds. Real Bitcoin uses difficulty 72+ (requiring ~2^72 hash attempts on average).

### 4.4 Merkle Trees

Every block's transactions are hashed into a Merkle tree. The root is included in the block hash. This means:
- Verifying a transaction is in a block only requires O(log n) hash operations
- Changing any transaction changes the Merkle root, which changes the block hash, which breaks the chain

---

## 5. Security Considerations

### 5.1 Prototype Limitations (Acknowledged)

This is a **research prototype**, not a production system. The following security measures are educational simulations:

| Component | Simulation | Production Requirement |
|-----------|-----------|----------------------|
| Wallet Keys | SHA-256 based | ECDSA secp256k1 (Ethereum standard) |
| Consensus | Single-node mining | Proof-of-Stake (Ethereum) or permissioned BFT |
| Network | Localhost only | TLS 1.3, firewall, DDoS protection |
| Authentication | Simulated fingerprint | WebAuthn/FIDO2, hardware security keys |
| Storage | In-memory Python dict | Encrypted database, IPFS with encryption |
| Smart Contract | Not deployed | Formal verification, audit by CertiK/OpenZeppelin |

### 5.2 Security Principles for Production

1. **Data Minimization**: Only store record hashes on-chain. Full data stays in HIPAA-compliant storage.
2. **Encryption at Rest**: Patient controls encryption keys. Provider never sees raw data without decryption.
3. **Zero-Knowledge Proofs**: Future enhancement — prove access without revealing record contents.
4. **Multi-Signature**: Critical operations (revoking a long-term grant) could require 2-of-3 signatures.
5. **Time-Locked Recovery**: If patient loses keys, a social recovery mechanism with time delay.
6. **Rate Limiting**: Backend API must rate-limit access checks to prevent enumeration attacks.
7. **CORS**: In production, restrict CORS to the exact frontend domain, not `*`.
8. **Input Validation**: All smart contract functions use `require()` for validation. Backend uses Flask validation.

### 5.3 Threat Model

| Threat | Mitigation in Prototype | Mitigation in Production |
|--------|------------------------|------------------------|
| Patient loses private key | N/A (simulated) | Social recovery + Shamir's Secret Sharing |
| Provider steals data | Cannot — only hashes on chain | Off-chain encryption + legal contracts |
| Malicious provider adds fake records | Only patient can register records | Multi-sig for record addition from facilities |
| Replay attacks | Nonce in transactions | EIP-155 chain-specific signing |
| Front-running | Not applicable in single-node | Private mempools, commit-reveal schemes |
| 51% attack | Single node = 100% control | PoS or permissioned validators |

---

## 6. Production Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           END USER BROWSER                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  React/Vue Frontend (build artifacts served from CDN)               │   │
│  │  • MetaMask / WalletConnect integration                             │   │
│  │  • IPFS client for encrypted data retrieval                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTPS
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLOUD LOAD BALANCER (AWS ALB / Cloudflare)        │
│  • TLS termination                                                        │
│  • DDoS protection                                                      │
│  • Rate limiting                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND API (AWS ECS / Heroku / Render)           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Python / Node.js API Server                                        │   │
│  │  • Web3.py / ethers.js for Ethereum interaction                     │   │
│  │  • PostgreSQL for off-chain metadata (HIPAA-compliant)            │   │
│  │  • Redis for session caching                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
┌──────────────────────────────────┐  ┌──────────────────────────────────┐
│  ETHEREUM / EVM CHAIN            │  │  OFF-CHAIN STORAGE               │
│  ┌────────────────────────────┐  │  │  ┌────────────────────────────┐  │
│  │  Smart Contract (deployed) │  │  │  │  IPFS / Encrypted S3       │  │
│  │  • Access control logic    │  │  │  │  • Encrypted medical data  │  │
│  │  • Audit log events        │  │  │  │  • Content-addressed       │  │
│  │  • Record hash anchors     │  │  │  │  • Patient-controlled keys │  │
│  └────────────────────────────┘  │  │  └────────────────────────────┘  │
│  Infura / Alchemy / QuickNode    │  │  Pinata / Web3.Storage /       │
│  JSON-RPC provider               │  │  Custom IPFS cluster           │
└──────────────────────────────────┘  └──────────────────────────────────┘
```

### 6.1 Technology Stack for Production

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | React / Next.js | Component-based, SSR for accessibility, large ecosystem |
| **Wallet** | MetaMask, WalletConnect, Coinbase Wallet | Standard Ethereum wallet interfaces |
| **Backend** | Python (FastAPI) or Node.js (Express) | FastAPI for async; Express for ethers.js native |
| **Database** | PostgreSQL (RDS) + Redis (ElastiCache) | ACID compliance + fast session caching |
| **Blockchain** | Ethereum Sepolia (testnet) → Ethereum Mainnet or Polygon | Polygon for lower gas costs |
| **Smart Contract** | Solidity + OpenZeppelin + Hardhat | Battle-tested libraries, modern toolchain |
| **Off-chain Storage** | IPFS + Filecoin or Arweave | Permanent, decentralized, content-addressed |
| **Monitoring** | Prometheus + Grafana + PagerDuty | HIPAA requires uptime monitoring |
| **CI/CD** | GitHub Actions → AWS ECS / Vercel | Automated testing and deployment |

### 6.2 Gas Cost Estimates (Production)

| Operation | Estimated Gas | Cost at 20 gwei | Cost at 100 gwei |
|-----------|-------------|-----------------|-----------------|
| Register Record | ~45,000 | $0.90 | $4.50 |
| Initiate Grant | ~55,000 | $1.10 | $5.50 |
| Confirm Grant | ~35,000 | $0.70 | $3.50 |
| Revoke Access | ~30,000 | $0.60 | $3.00 |
| Log Access Attempt | ~25,000 | $0.50 | $2.50 |

*Note: On Polygon, these costs are ~100x lower due to lower gas prices.*

---

## 7. Data Model

### 7.1 On-Chain (Smart Contract)

```solidity
mapping(address => mapping(bytes32 => Record)) records;
mapping(address => mapping(bytes32 => mapping(address => AccessGrant))) accessGrants;
mapping(address => mapping(bytes32 => AuditEntry[])) auditLogs;
```

### 7.2 Off-Chain (Backend Database)

```sql
-- patients table
CREATE TABLE patients (
    id UUID PRIMARY KEY,
    wallet_address VARCHAR(42) UNIQUE NOT NULL,
    name VARCHAR(255),
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- records table (metadata only, hash is the link to IPFS)
CREATE TABLE records (
    id UUID PRIMARY KEY,
    patient_id UUID REFERENCES patients(id),
    record_hash VARCHAR(66) NOT NULL,
    record_type VARCHAR(100),
    facility VARCHAR(255),
    date DATE,
    ipfs_cid VARCHAR(100),  -- Content Identifier for the encrypted data
    created_at TIMESTAMP DEFAULT NOW()
);

-- access_grants table (mirrors on-chain state for fast queries)
CREATE TABLE access_grants (
    id UUID PRIMARY KEY,
    patient_id UUID REFERENCES patients(id),
    provider_id UUID REFERENCES providers(id),
    record_id UUID REFERENCES records(id),
    access_level INT DEFAULT 1,
    status VARCHAR(20) DEFAULT 'pending', -- pending, active, revoked, expired
    pending_until TIMESTAMP,
    grant_timestamp TIMESTAMP,
    expiration TIMESTAMP,
    tx_hash VARCHAR(66),
    block_number INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- audit_log table (all events for analytics and compliance reports)
CREATE TABLE audit_log (
    id UUID PRIMARY KEY,
    patient_id UUID REFERENCES patients(id),
    provider_id UUID REFERENCES providers(id),
    record_id UUID REFERENCES records(id),
    action VARCHAR(50) NOT NULL,
    tx_hash VARCHAR(66),
    block_number INT,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 8. Future Enhancements

1. **Zero-Knowledge Access Proofs**: Patient can prove they have a valid grant without revealing the provider's identity or the record contents.
2. **Decentralized Identity (DID)**: Use DID standards (W3C) for provider identity instead of simple wallet addresses.
3. **Layer 2 Scaling**: Move to Arbitrum or Optimism for lower gas costs and faster finality.
4. **Multi-Chain Support**: Deploy on multiple chains with a bridge for cross-chain access verification.
5. **AI-Powered Anomaly Detection**: Monitor access patterns to detect unusual provider behavior (e.g., a provider accessing 100 records at 3 AM).
6. **Patient-Controlled Encryption**: Use threshold encryption where the patient holds the decryption key shards.
7. **NFT-Based Records**: Represent each record as a soulbound NFT (SBT) that the patient owns and controls.
