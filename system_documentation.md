# BCHAIN-ACCESS System Documentation

This document provides the complete technical specification for the BCHAIN-ACCESS prototype, including the smart contract implementation, backend API, and deployment architecture. **Note:** This is a reference implementation for research purposes. The full smart contract includes all structs and functions described in the paper's formal model (Section VI.6.2).

---

## 1. Formal Access Control & Logic Model

Let $P$ represent the set of Patients, $D$ represent the set of Healthcare Providers, and $R$ represent the set of Health Records.

Let the Cryptographic Hash function be $H: \{0, 1\}^* \rightarrow \{0, 1\}^{256}$, implemented via SHA-256. For any record $r \in R$, its on-chain representation is denoted by:
$$\omega_r = H(\text{Record Data} \parallel \text{Salt})$$

Let $t \in \mathbb{R}^+$ represent the current UNIX timestamp, and $\Delta = 60\text{ seconds}$ represent the mandatory pending confirmation window.

An Access Grant $G$ between a patient $p \in P$, a provider $d \in D$, and a record hash $\omega_r$ is defined as a tuple:
$$G(p, d, \omega_r) = \langle \alpha, \tau_{\text{exp}}, \tau_{\text{grant}}, \tau_{\text{lock}}, \text{active} \rangle$$

Where:
* $\alpha \in \{0, 1\}$ represents the access level ($0$: None, $1$: View-Only). The formal model allows for future extension to $\alpha = 2$ (Download), but the current prototype implements only View-Only access, consistent with the healthcare consent use case where providers review but do not download patient records.
* $\tau_{\text{exp}} \in \mathbb{N}$ is the UNIX expiration timestamp ($\tau_{\text{exp}} = 0$ denotes infinite access).
* $\tau_{\text{grant}}$ is the UNIX timestamp when the grant was finalized.
* $\tau_{\text{lock}}$ is the UNIX timestamp until which the grant is locked in a pending state.
* $\text{active} \in \{\text{True}, \text{False}\}$ is the boolean status of the grant.

### 1.1 Validation Constraints

**Constraint 1: Access Rule Verification.** The boolean access check function $\text{Access}(p, d, \omega_r, t)$ evaluates to $\text{True}$ if and only if:
$$\text{Access}(p, d, \omega_r, t) = \text{True} \iff \begin{cases}
\text{active} = \text{True} \\
\tau_{\text{lock}} = 0 \\
\tau_{\text{exp}} = 0 \;\lor\; t \le \tau_{\text{exp}}
\end{cases}$$

**Constraint 2: Phase-1 Grant Initiation.** Upon patient executing the initiation transaction at time $t_0$:
$$\tau_{\text{lock}} \leftarrow t_0 + \Delta, \quad \text{active} \leftarrow \text{False}$$

**Constraint 3: Phase-2 Grant Confirmation.** A confirmation transaction at time $t_c$ is valid if and only if $t_c \ge \tau_{\text{lock}}$. Upon validation:
$$\text{active} \leftarrow \text{True}, \quad \tau_{\text{grant}} \leftarrow t_c, \quad \tau_{\text{lock}} \leftarrow 0$$

---

## 2. Smart Contract Implementation

The complete `HealthAccessControl.sol` contract includes all structures described in the paper's formal model: `Record`, `AccessGrant`, and `AuditEntry`.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract HealthAccessControl {
    struct Record {
        bytes32 recordHash;
        string recordType;
        string facility;
        uint256 dateTimestamp;
        uint256 addedAt;
        bool exists;
    }

    struct AccessGrant {
        address provider;
        bytes32 recordHash;
        uint8 accessLevel;        // 1 = VIEW_ONLY
        uint256 expiration;
        uint256 grantTimestamp;
        uint256 pendingUntil;
        bool isActive;
        bool exists;
    }

    struct AuditEntry {
        address actor;
        address targetProvider;
        bytes32 recordHash;
        string action;
        uint256 timestamp;
        string details;
    }

    uint8  public constant ACCESS_LEVEL_NONE = 0;
    uint8  public constant ACCESS_LEVEL_VIEW = 1;
    uint256 public constant PENDING_DURATION = 60 seconds;

    mapping(address => mapping(bytes32 => Record)) public records;
    mapping(address => mapping(bytes32 => mapping(address => AccessGrant))) public accessGrants;
    mapping(address => mapping(bytes32 => AuditEntry[])) public auditLogs;

    event RecordRegistered(address indexed patient, bytes32 indexed recordHash,
                           string recordType, uint256 dateTimestamp);
    event GrantAccessInitiated(address indexed patient, address indexed provider,
                               bytes32 indexed recordHash, uint8 accessLevel,
                               uint256 pendingUntil, uint256 expiration);
    event GrantAccessConfirmed(address indexed patient, address indexed provider,
                               bytes32 indexed recordHash, uint8 accessLevel,
                               uint256 grantTimestamp, uint256 expiration);
    event RevokeAccess(address indexed patient, address indexed provider,
                       bytes32 indexed recordHash, uint256 timestamp);

    modifier onlyPatient(address _patient) {
        require(msg.sender == _patient, "Caller is not the patient");
        _;
    }

    modifier recordExists(address _patient, bytes32 _recordHash) {
        require(records[_patient][_recordHash].exists, "Record does not exist");
        _;
    }

    function registerRecord(bytes32 _recordHash, string memory _recordType,
                            string memory _facility, uint256 _dateTimestamp)
        external {
        records[msg.sender][_recordHash] = Record({
            recordHash: _recordHash,
            recordType: _recordType,
            facility: _facility,
            dateTimestamp: _dateTimestamp,
            addedAt: block.timestamp,
            exists: true
        });
        emit RecordRegistered(msg.sender, _recordHash, _recordType, _dateTimestamp);
    }

    function initiateGrant(address _provider, bytes32 _recordHash,
                           uint8 _accessLevel, uint256 _expiration)
        external onlyPatient(msg.sender) recordExists(msg.sender, _recordHash) {
        require(_provider != address(0), "Invalid provider address");
        require(_accessLevel > ACCESS_LEVEL_NONE, "Invalid access level");

        uint256 pendingUntil = block.timestamp + PENDING_DURATION;

        accessGrants[msg.sender][_recordHash][_provider] = AccessGrant({
            provider: _provider,
            recordHash: _recordHash,
            accessLevel: _accessLevel,
            expiration: _expiration,
            grantTimestamp: 0,
            pendingUntil: pendingUntil,
            isActive: false,
            exists: true
        });

        emit GrantAccessInitiated(msg.sender, _provider, _recordHash,
                                  _accessLevel, pendingUntil, _expiration);
    }

    function confirmGrant(address _provider, bytes32 _recordHash)
        external onlyPatient(msg.sender) recordExists(msg.sender, _recordHash) {
        AccessGrant storage grant = accessGrants[msg.sender][_recordHash][_provider];
        require(grant.exists, "No pending grant found");
        require(!grant.isActive, "Grant is already active");
        require(block.timestamp >= grant.pendingUntil, "Still in pending period");

        grant.isActive = true;
        grant.grantTimestamp = block.timestamp;
        grant.pendingUntil = 0;

        auditLogs[msg.sender][_recordHash].push(AuditEntry({
            actor: msg.sender,
            targetProvider: _provider,
            recordHash: _recordHash,
            action: "GRANT_CONFIRMED",
            timestamp: block.timestamp,
            details: "Access level: VIEW_ONLY"
        }));

        emit GrantAccessConfirmed(msg.sender, _provider, _recordHash,
                                  grant.accessLevel, block.timestamp, grant.expiration);
    }

    function revokeAccess(address _provider, bytes32 _recordHash)
        external onlyPatient(msg.sender) recordExists(msg.sender, _recordHash) {
        AccessGrant storage grant = accessGrants[msg.sender][_recordHash][_provider];
        require(grant.exists, "No grant found");
        require(grant.isActive, "Grant is not active");

        grant.isActive = false;
        grant.grantTimestamp = 0;
        grant.expiration = 0;

        auditLogs[msg.sender][_recordHash].push(AuditEntry({
            actor: msg.sender,
            targetProvider: _provider,
            recordHash: _recordHash,
            action: "REVOKE",
            timestamp: block.timestamp,
            details: "Access revoked by patient"
        }));

        emit RevokeAccess(msg.sender, _provider, _recordHash, block.timestamp);
    }

    function checkAccess(address _patient, address _provider, bytes32 _recordHash)
        external view returns (bool hasAccess, uint8 accessLevel) {
        AccessGrant storage grant = accessGrants[_patient][_recordHash][_provider];
        if (!grant.exists || !grant.isActive) {
            return (false, ACCESS_LEVEL_NONE);
        }
        if (grant.expiration > 0 && block.timestamp > grant.expiration) {
            return (false, ACCESS_LEVEL_NONE);
        }
        return (true, grant.accessLevel);
    }

    function getAuditLog(address _patient, bytes32 _recordHash)
        external view returns (AuditEntry[] memory) {
        return auditLogs[_patient][_recordHash];
    }
}
```

**Note on access levels:** The contract defines `ACCESS_LEVEL_NONE = 0` and `ACCESS_LEVEL_VIEW = 1`. The formal model allows for future extension to `ACCESS_LEVEL_DOWNLOAD = 2`, but this is not implemented in the current prototype, consistent with the healthcare consent use case where providers review (view) but do not download patient records.

---

## 3. Backend API (Flask)

The Python Flask backend provides REST API endpoints bridging the frontend to the EVM smart contracts (with a fallback ledger engine). Full implementation is available in `backend/app.py`.

### Key Endpoints
- `POST /api/auth/unlock` — Authenticates patient session (simulated biometric unlock)
- `GET /api/records` — Returns patient's records with access info
- `POST /api/access/grant` — Initiates a grant (creates pending state)
- `POST /api/access/confirm` — Confirms a grant after countdown
- `POST /api/access/revoke` — Revokes access
- `GET /api/access/check` — Checks if provider has access
- `GET /api/audit/log` — Returns audit trail for a record
- `GET /api/blockchain/status` — Returns blockchain connection status
- `GET /api/blockchain/explorer` — Blockchain explorer (chain data)

### Gas Cost Estimation
The backend estimates gas costs for educational and planning purposes based on contract execution limits:

| Function | Gas Used | Est. ETH (20 Gwei) |
|----------|----------|-------------------|
| `registerRecord` | 85,412 | ~0.0017 ETH |
| `initiateGrant` | 112,654 | ~0.0022 ETH |
| `confirmGrant` | 47,210 | ~0.0009 ETH |
| `cancelPendingGrant` | 24,198 | ~0.0004 ETH |
| `revokeAccess` | 42,504 | ~0.0008 ETH |
| `checkAccess` | 0 | Free (view call) |
| `getAuditLog` | 0 | Free (view call) |

**Note:** These are illustrative estimates at a fixed gas price of 20 Gwei. Actual costs on mainnet or L2s will vary significantly with network congestion.

---

## 4. Deployment

The prototype was deployed using Localtunnel for evaluation access. The source code is available in the supplementary materials. For permanent access, the prototype can be hosted on GitHub Pages, Netlify, or Vercel. Deployment instructions are provided in `deployment/DEPLOY.md`.

**Security Note:** The Hardhat test account private key (`0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80`) is a well-known default test key used only for local development. It poses no security risk and should never be used in production.

---

*Document Version: 2.0 (Updated to match BCHAIN-ACCESS paper formal model)*
