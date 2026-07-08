"""
app.py
Flask backend for the Healthcare Blockchain Access Control prototype.

This backend coordinates blockchain operations by interfacing with real Solidity
smart contracts via Web3.py, falling back to a local educational Python ledger
engine if the local node is offline. It replaces client-side JavaScript state 
management with a secure server-side blockchain interface.

Endpoints:
- Authentication: /api/auth/unlock
- Records: /api/records
- Access Control: /api/access/grant, /api/access/confirm, /api/access/revoke, /api/access/check
- Audit: /api/audit/log
- Blockchain: /api/blockchain/status, /api/blockchain/explorer
- Health: /api/health

Run with: python app.py
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import time
import secrets
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Import the local educational fallback ledger engine
from blockchain_simulator import (
    Blockchain, Wallet, Transaction, Block,
    TxType, build_merkle_root, current_timestamp, sha256_hash
)

# Web3 Integration
from web3 import Web3
from config import Config

# Connect to local Hardhat node
w3 = Web3(Web3.HTTPProvider(Config.WEB3_PROVIDER_URL))
contract = None

if w3.is_connected():
    print(f"Connected to local Hardhat JSON-RPC node at {Config.WEB3_PROVIDER_URL}")
    try:
        with open(Config.CONTRACT_ABI_PATH, 'r') as f:
            abi_json = json.load(f)
            contract_abi = abi_json.get('abi', abi_json)
        contract = w3.eth.contract(address=Config.CONTRACT_ADDRESS, abi=contract_abi)
        print(f"Interfacing with Solidity smart contract at {Config.CONTRACT_ADDRESS}")
    except Exception as e:
        print(f"Failed to load contract ABI: {e}")
else:
    print("WARNING: Could not connect to local Hardhat node. Operating in Local Fallback Ledger Mode.")

# =============================================================================
# FLASK APP SETUP
# =============================================================================

app = Flask(__name__)

# Enable CORS for all origins (for development; restrict in production)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
    }
})

# Configuration
PATIENT_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"  # Hardhat Account #0
PENDING_DURATION_SECONDS = 60  # Must match frontend and smart contract
SESSION_TIMEOUT_SECONDS = 15 * 60  # 15 minutes, matches frontend

# =============================================================================
# IN-MEMORY STATE (LOCAL FALLBACK LEDGER + APP STATE)
# =============================================================================

# The local fallback blockchain ledger
blockchain = Blockchain(difficulty=3)

# Local fallback wallets mapped to actual local Hardhat accounts
patient_wallet = Wallet(private_key="ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
patient_wallet.address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

provider_wallets = {
    "dr-sarah-chen": Wallet(private_key="59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"),
    "dr-michael-torres": Wallet(private_key="5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a"),
    "dr-james-wilson": Wallet(private_key="7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6"),
    "metro-physical-therapy": Wallet(private_key="47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a"),
}

provider_wallets["dr-sarah-chen"].address = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
provider_wallets["dr-michael-torres"].address = "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"
provider_wallets["dr-james-wilson"].address = "0x90F79bf6EB2c4f870365E785982E1f101E93b906"
provider_wallets["metro-physical-therapy"].address = "0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65"

# Pre-populate patient records (synced with the smart contract initial state)
records_db = {
    "mri-scan": {
        "record_id": "mri-scan",
        "record_hash": sha256_hash("mri_brain_scan_june_2026_metro_neurology"),
        "record_type": "MRI Brain Scan",
        "facility": "Metro Neurology Center",
        "date": "2026-06-12",
        "date_timestamp": int(datetime(2026, 6, 12, tzinfo=timezone.utc).timestamp()),
        "patient_address": patient_wallet.address,
        "status": "active",
    },
    "blood-panel": {
        "record_id": "blood-panel",
        "record_hash": sha256_hash("blood_work_panel_may_2026_metro_general"),
        "record_type": "Blood Work Panel",
        "facility": "Metro General Lab",
        "date": "2026-05-28",
        "date_timestamp": int(datetime(2026, 5, 28, tzinfo=timezone.utc).timestamp()),
        "patient_address": patient_wallet.address,
        "status": "active",
    },
    "chest-xray": {
        "record_id": "chest-xray",
        "record_hash": sha256_hash("chest_xray_april_2026_metro_imaging"),
        "record_type": "Chest X-Ray",
        "facility": "Metro Imaging",
        "date": "2026-04-10",
        "date_timestamp": int(datetime(2026, 4, 10, tzinfo=timezone.utc).timestamp()),
        "patient_address": patient_wallet.address,
        "status": "active",
    },
}

# Access grants database (acting as a local cache of the smart contract state)
# Structure: {record_id: {provider_id: grant_info}}
access_grants_db: Dict[str, Dict[str, Any]] = {
    "mri-scan": {
        "dr-sarah-chen": {
            "provider_id": "dr-sarah-chen",
            "provider_name": "Dr. Sarah Chen",
            "provider_specialty": "Neurology",
            "provider_address": provider_wallets["dr-sarah-chen"].address,
            "record_id": "mri-scan",
            "record_hash": records_db["mri-scan"]["record_hash"],
            "access_level": 1,  # VIEW_ONLY
            "status": "active",
            "grant_timestamp": int(datetime(2026, 6, 15, tzinfo=timezone.utc).timestamp()),
            "expiration": 0,  # No expiration
            "tx_hash": sha256_hash("grant_dr_chen_mri"),
            "block_number": 2,
        },
        "dr-michael-torres": {
            "provider_id": "dr-michael-torres",
            "provider_name": "Dr. Michael Torres",
            "provider_specialty": "Primary Care",
            "provider_address": provider_wallets["dr-michael-torres"].address,
            "record_id": "mri-scan",
            "record_hash": records_db["mri-scan"]["record_hash"],
            "access_level": 1,
            "status": "active",
            "grant_timestamp": int(datetime(2026, 1, 3, tzinfo=timezone.utc).timestamp()),
            "expiration": 0,
            "tx_hash": sha256_hash("grant_dr_torres_mri"),
            "block_number": 3,
        },
    },
    "blood-panel": {},
    "chest-xray": {},
}

# Pending grants (time-locked state before confirmation)
# Structure: {pending_id: {grant info with pending_until}}
pending_grants: Dict[str, Any] = {}

# Audit log database (acting as a local cache of the smart contract's immutable audit log)
# Structure: {record_id: [audit_entries]}
audit_logs_db: Dict[str, list] = {
    "mri-scan": [
        {
            "actor": patient_wallet.address,
            "action": "RECORD_REGISTERED",
            "timestamp": int(datetime(2026, 6, 12, tzinfo=timezone.utc).timestamp()),
            "details": "MRI Brain Scan registered by patient",
            "tx_hash": sha256_hash("register_mri"),
        },
        {
            "actor": patient_wallet.address,
            "target_provider": provider_wallets["dr-sarah-chen"].address,
            "action": "GRANT_CONFIRMED",
            "timestamp": int(datetime(2026, 6, 15, tzinfo=timezone.utc).timestamp()),
            "details": "Access level: VIEW_ONLY",
            "tx_hash": sha256_hash("grant_dr_chen_mri"),
        },
        {
            "actor": patient_wallet.address,
            "target_provider": provider_wallets["dr-michael-torres"].address,
            "action": "GRANT_CONFIRMED",
            "timestamp": int(datetime(2026, 1, 3, tzinfo=timezone.utc).timestamp()),
            "details": "Access level: VIEW_ONLY",
            "tx_hash": sha256_hash("grant_dr_torres_mri"),
        },
    ],
    "blood-panel": [
        {
            "actor": patient_wallet.address,
            "action": "RECORD_REGISTERED",
            "timestamp": int(datetime(2026, 5, 28, tzinfo=timezone.utc).timestamp()),
            "details": "Blood Work Panel registered by patient",
            "tx_hash": sha256_hash("register_blood"),
        },
    ],
    "chest-xray": [
        {
            "actor": patient_wallet.address,
            "action": "RECORD_REGISTERED",
            "timestamp": int(datetime(2026, 4, 10, tzinfo=timezone.utc).timestamp()),
            "details": "Chest X-Ray registered by patient",
            "tx_hash": sha256_hash("register_xray"),
        },
    ],
}

# Session state (handling local dashboard authentication)
session_state = {
    "active": False,
    "started_at": 0,
    "expires_at": 0,
    "patient_address": PATIENT_ADDRESS,
}

# Transaction counter for nonce generation
tx_nonce_counter = 100

# Provider registry
provider_registry = {
    "dr-sarah-chen": {
        "id": "dr-sarah-chen",
        "name": "Dr. Sarah Chen",
        "specialty": "Neurology",
        "address": provider_wallets["dr-sarah-chen"].address,
    },
    "dr-michael-torres": {
        "id": "dr-michael-torres",
        "name": "Dr. Michael Torres",
        "specialty": "Primary Care",
        "address": provider_wallets["dr-michael-torres"].address,
    },
    "dr-james-wilson": {
        "id": "dr-james-wilson",
        "name": "Dr. James Wilson",
        "specialty": "Radiology",
        "address": provider_wallets["dr-james-wilson"].address,
    },
    "metro-physical-therapy": {
        "id": "metro-physical-therapy",
        "name": "Metro Physical Therapy",
        "specialty": "Physical Therapy",
        "address": provider_wallets["metro-physical-therapy"].address,
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_tx_hash() -> str:
    """Generate a unique transaction hash."""
    global tx_nonce_counter
    tx_nonce_counter += 1
    data = f"tx:{time.time()}:{tx_nonce_counter}:{secrets.token_hex(8)}"
    return "0x" + sha256_hash(data)


def create_blockchain_transaction(
    tx_type: TxType,
    from_addr: str,
    to_addr: str,
    data: Dict[str, Any]
) -> Transaction:
    """
    Create a signed transaction and add it to the blockchain mempool.
    Returns the transaction object for the caller to track.
    """
    tx = Transaction(
        from_address=from_addr,
        to_address=to_addr,
        tx_type=tx_type,
        data=data,
        timestamp=current_timestamp(),
        tx_hash="",
        signature="",
        nonce=tx_nonce_counter,
    )
    tx.tx_hash = tx.compute_hash()
    tx.gas_price = 20  # gwei (simulated)
    tx.estimate_gas()

    # Sign with the appropriate wallet
    if from_addr == patient_wallet.address:
        patient_wallet.sign_transaction(tx)
    elif from_addr in [w.address for w in provider_wallets.values()]:
        # Find the matching provider wallet
        for w in provider_wallets.values():
            if w.address == from_addr:
                w.sign_transaction(tx)
                break
    else:
        # System transaction, no real signature needed
        tx.signature = "system"

    blockchain.add_transaction(tx)
    return tx


def mine_if_needed():
    """Mine a block if the mempool has transactions."""
    if blockchain.mempool:
        blockchain.mine_block(miner_address=patient_wallet.address)


def send_contract_tx(func_call):
    if not w3.is_connected() or not contract:
        print("w3 not connected or contract not loaded. Skipping tx.")
        return None
    try:
        account = w3.eth.account.from_key(Config.PATIENT_PRIVATE_KEY)
        tx_params = func_call.build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 3000000,
            'gasPrice': w3.eth.gas_price,
        })
        signed_tx = w3.eth.account.sign_transaction(tx_params, Config.PATIENT_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Solidity transaction confirmed. Tx Hash: {tx_hash.hex()}")
        return receipt
    except Exception as e:
        print(f"Solidity transaction execution failed: {e}")
        raise e


def sync_records_to_smart_contract():
    if not w3.is_connected() or not contract:
        print("Blockchain node not connected; skipping contract sync.")
        return

    print("Syncing records to Solidity smart contract...")
    account = w3.eth.account.from_key(Config.PATIENT_PRIVATE_KEY)

    for record_id, record in records_db.items():
        record_hash_bytes = w3.to_bytes(hexstr=record["record_hash"])
        try:
            onchain_record = contract.functions.getRecord(account.address, record_hash_bytes).call()
            exists = onchain_record[5]
            if exists:
                print(f"Record {record_id} already registered on-chain.")
                continue
        except Exception:
            pass

        try:
            print(f"Registering record {record_id} on-chain...")
            tx_params = contract.functions.registerRecord(
                record_hash_bytes,
                record["record_type"],
                record["facility"],
                int(record["date_timestamp"])
            ).build_transaction({
                'from': account.address,
                'nonce': w3.eth.get_transaction_count(account.address),
                'gas': 3000000,
                'gasPrice': w3.eth.gas_price,
            })
            signed_tx = w3.eth.account.sign_transaction(tx_params, Config.PATIENT_PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Record {record_id} registered successfully. Tx: {tx_hash.hex()}")
        except Exception as ex:
            print(f"Error registering record {record_id} on-chain: {ex}")


def get_active_providers_for_record(record_id: str) -> list:
    """Get list of active providers for a given record."""
    grants = access_grants_db.get(record_id, {})
    active = []
    for provider_id, grant in grants.items():
        if grant.get("status") == "active":
            # Check expiration
            expiration = grant.get("expiration", 0)
            if expiration == 0 or time.time() < expiration:
                active.append(grant)
    return active


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return jsonify({
        "status": "healthy",
        "timestamp": current_timestamp(),
        "service": "healthcare-blockchain-access-control",
        "version": "1.0.0",
    })


# -------------------------------------------------------------------------
# AUTHENTICATION
# -------------------------------------------------------------------------

@app.route("/api/auth/unlock", methods=["POST"])
def auth_unlock():
    """
    Simulate patient biometric/fingerprint unlock.

    In production, this would integrate with WebAuthn, biometric APIs,
    or wallet-based authentication (MetaMask, WalletConnect, etc.).

    Request body: { "method": "fingerprint" } (optional)
    Response: { success, session, patient, blockchain_address }
    """
    data = request.get_json(silent=True) or {}
    method = data.get("method", "fingerprint")

    # Mock biometric verification delay (matches frontend UI transition of ~800ms)
    time.sleep(0.5)

    # Activate session
    now = time.time()
    session_state["active"] = True
    session_state["started_at"] = now
    session_state["expires_at"] = now + SESSION_TIMEOUT_SECONDS
    session_state["patient_address"] = patient_wallet.address

    # Create a blockchain transaction logging the authentication
    tx = create_blockchain_transaction(
        tx_type=TxType.SYSTEM,
        from_addr=patient_wallet.address,
        to_addr="system_auth",
        data={
            "action": "SESSION_UNLOCK",
            "method": method,
            "patient_id": "elena-vasquez-001",
            "patient_name": "Elena Vasquez",
            "patient_dob": "1985-03-15",
        }
    )

    # Mine a block to confirm the auth transaction
    mine_if_needed()

    return jsonify({
        "success": True,
        "message": "Session unlocked successfully",
        "session": {
            "active": True,
            "started_at": datetime.fromtimestamp(now, tz=timezone.utc).isoformat(),
            "expires_at": datetime.fromtimestamp(now + SESSION_TIMEOUT_SECONDS, tz=timezone.utc).isoformat(),
            "duration_seconds": SESSION_TIMEOUT_SECONDS,
        },
        "patient": {
            "id": "elena-vasquez-001",
            "name": "Elena Vasquez",
            "date_of_birth": "1985-03-15",
            "blockchain_address": patient_wallet.address,
        },
        "blockchain": {
            "tx_hash": tx.tx_hash,
            "block_number": tx.block_number,
            "gas_used": tx.gas_used,
            "gas_cost_eth": round(tx.gas_used * tx.gas_price / 1e9, 9),  # Cost in ETH
        },
    })


@app.route("/api/auth/status", methods=["GET"])
def auth_status():
    """Check current session status and time remaining."""
    if not session_state["active"]:
        return jsonify({"active": False, "message": "No active session"})

    remaining = session_state["expires_at"] - time.time()
    if remaining <= 0:
        session_state["active"] = False
        return jsonify({"active": False, "message": "Session expired"})

    return jsonify({
        "active": True,
        "patient_address": session_state["patient_address"],
        "expires_at": datetime.fromtimestamp(session_state["expires_at"], tz=timezone.utc).isoformat(),
        "remaining_seconds": int(remaining),
        "warning_threshold_seconds": 120,  # Warn 2 min before expiry
    })


@app.route("/api/auth/extend", methods=["POST"])
def auth_extend():
    """Extend the current session (equivalent to "Keep me signed in")."""
    if not session_state["active"]:
        return jsonify({"success": False, "message": "No active session to extend"}), 401

    now = time.time()
    session_state["expires_at"] = now + SESSION_TIMEOUT_SECONDS

    return jsonify({
        "success": True,
        "message": "Session extended",
        "expires_at": datetime.fromtimestamp(session_state["expires_at"], tz=timezone.utc).isoformat(),
        "remaining_seconds": SESSION_TIMEOUT_SECONDS,
    })


# -------------------------------------------------------------------------
# RECORDS
# -------------------------------------------------------------------------

@app.route("/api/records", methods=["GET"])
def get_records():
    """
    Get all patient records with access information.

    Returns:
        List of records with active provider access for each.
    """
    result = []
    for record_id, record in records_db.items():
        active_providers = get_active_providers_for_record(record_id)
        record_copy = dict(record)
        record_copy["id"] = record_id
        record_copy["title"] = record.get("record_type", "")
        record_copy["access_grants"] = active_providers
        record_copy["access_count"] = len(active_providers)
        record_copy["is_private"] = len(active_providers) == 0
        result.append(record_copy)

    return jsonify({
        "patient_address": patient_wallet.address,
        "records": result,
        "total_records": len(result),
    })


@app.route("/api/records/<record_id>", methods=["GET"])
def get_record(record_id):
    """Get a specific record by ID."""
    record = records_db.get(record_id)
    if not record:
        return jsonify({"error": "Record not found"}), 404

    active_providers = get_active_providers_for_record(record_id)
    record_copy = dict(record)
    record_copy["id"] = record_id
    record_copy["title"] = record.get("record_type", "")
    record_copy["access_grants"] = active_providers
    record_copy["access_count"] = len(active_providers)
    record_copy["is_private"] = len(active_providers) == 0

    return jsonify({"record": record_copy})


# -------------------------------------------------------------------------
# ACCESS CONTROL
# -------------------------------------------------------------------------

@app.route("/api/access/grant", methods=["POST"])
def grant_access():
    """
    Initiate an access grant (enters PENDING state for 60 seconds).

    Request body:
    {
        "provider_id": "dr-sarah-chen",
        "record_ids": ["mri-scan"],
        "access_level": 1,  // 1 = VIEW_ONLY
        "expiration_days": 0  // Optional, 0 = no expiry
    }

    Response:
    {
        "success": true,
        "pending_id": "...",
        "pending_until": "...",
        "tx_hash": "...",
        "message": "..."
    }
    """
    data = request.get_json(silent=True) or {}
    provider_id = data.get("provider_id")
    record_ids = data.get("record_ids", [])
    access_level = data.get("access_level", 1)
    expiration_days = data.get("expiration_days", 0)

    if not provider_id or not record_ids:
        return jsonify({
            "success": False,
            "error": "provider_id and record_ids are required"
        }), 400

    provider = provider_registry.get(provider_id)
    if not provider:
        return jsonify({
            "success": False,
            "error": f"Provider '{provider_id}' not found"
        }), 404

    # Validate all records exist
    for rid in record_ids:
        if rid not in records_db:
            return jsonify({
                "success": False,
                "error": f"Record '{rid}' not found"
            }), 404

    # Create pending grant entries
    pending_id = f"pending_{secrets.token_hex(8)}"
    now = time.time()
    pending_until = now + PENDING_DURATION_SECONDS

    expiration = 0
    if expiration_days > 0:
        expiration = now + (expiration_days * 24 * 60 * 60)

    grant_entries = []
    for record_id in record_ids:
        record = records_db[record_id]

        # Send Solidity transaction for initiateGrant
        if w3.is_connected() and contract:
            record_hash_bytes = w3.to_bytes(hexstr=record["record_hash"])
            try:
                send_contract_tx(contract.functions.initiateGrant(
                    provider["address"],
                    record_hash_bytes,
                    int(access_level),
                    int(expiration)
                ))
            except Exception as e:
                print(f"Error on Solidity initiateGrant: {e}")

        # Create blockchain transaction for grant initiation
        tx = create_blockchain_transaction(
            tx_type=TxType.GRANT_INITIATE,
            from_addr=patient_wallet.address,
            to_addr=provider["address"],
            data={
                "provider_id": provider_id,
                "provider_name": provider["name"],
                "provider_specialty": provider["specialty"],
                "record_id": record_id,
                "record_hash": record["record_hash"],
                "record_type": record["record_type"],
                "access_level": access_level,
                "pending_until": pending_until,
                "expiration": expiration,
            }
        )

        # Mine a block to confirm the transaction
        mine_if_needed()

        grant_entry = {
            "pending_id": pending_id,
            "provider_id": provider_id,
            "provider_name": provider["name"],
            "provider_specialty": provider["specialty"],
            "provider_address": provider["address"],
            "record_id": record_id,
            "record_hash": record["record_hash"],
            "record_type": record["record_type"],
            "access_level": access_level,
            "status": "pending",
            "initiated_at": now,
            "pending_until": pending_until,
            "expiration": expiration,
            "tx_hash": tx.tx_hash,
            "block_number": tx.block_number,
            "gas_used": tx.gas_used,
        }
        grant_entries.append(grant_entry)

        # Store in pending grants
        pending_grants[pending_id] = {
            "pending_id": pending_id,
            "provider_id": provider_id,
            "record_ids": record_ids,
            "entries": grant_entries,
            "initiated_at": now,
            "pending_until": pending_until,
            "status": "pending",
        }

    return jsonify({
        "success": True,
        "pending_id": pending_id,
        "pending_until": pending_until,
        "pending_until_iso": datetime.fromtimestamp(pending_until, tz=timezone.utc).isoformat(),
        "countdown_seconds": PENDING_DURATION_SECONDS,
        "tx_hashes": [g["tx_hash"] for g in grant_entries],
        "provider": provider,
        "records": [records_db[rid] for rid in record_ids],
        "message": f"Access grant initiated for {provider['name']}. Confirm within {PENDING_DURATION_SECONDS} seconds.",
    })


@app.route("/api/access/confirm", methods=["POST"])
def confirm_access():
    """
    Confirm a pending access grant after the 60-second countdown.

    Request body: { "pending_id": "..." }

    Response:
    {
        "success": true,
        "tx_hash": "...",
        "block_number": 5,
        "message": "..."
    }
    """
    data = request.get_json(silent=True) or {}
    pending_id = data.get("pending_id")

    if not pending_id:
        return jsonify({"success": False, "error": "pending_id is required"}), 400

    pending = pending_grants.get(pending_id)
    if not pending:
        return jsonify({"success": False, "error": "Pending grant not found"}), 404

    if pending["status"] != "pending":
        return jsonify({"success": False, "error": f"Grant is already {pending['status']}"}), 400

    # Check if countdown has expired
    if time.time() < pending["pending_until"]:
        remaining = int(pending["pending_until"] - time.time())
        return jsonify({
            "success": False,
            "error": f"Still in pending period. {remaining} seconds remaining.",
            "remaining_seconds": remaining,
        }), 400

    # Finalize each grant entry
    tx_hashes = []
    for entry in pending["entries"]:
        record_id = entry["record_id"]
        provider_id = entry["provider_id"]
        record = records_db[record_id]
        provider = provider_registry[provider_id]

        # Send Solidity transaction for confirmGrant
        if w3.is_connected() and contract:
            record_hash_bytes = w3.to_bytes(hexstr=record["record_hash"])
            try:
                send_contract_tx(contract.functions.confirmGrant(
                    provider["address"],
                    record_hash_bytes
                ))
            except Exception as e:
                print(f"Error on Solidity confirmGrant: {e}")

        # Move from pending to active in access_grants_db
        access_grants_db[record_id][provider_id] = {
            "provider_id": provider_id,
            "provider_name": entry["provider_name"],
            "provider_specialty": entry["provider_specialty"],
            "provider_address": entry["provider_address"],
            "record_id": record_id,
            "record_hash": entry["record_hash"],
            "access_level": entry["access_level"],
            "status": "active",
            "grant_timestamp": time.time(),
            "expiration": entry["expiration"],
            "tx_hash": entry["tx_hash"],
            "block_number": entry.get("block_number"),
        }

        # Create blockchain confirmation transaction
        tx = create_blockchain_transaction(
            tx_type=TxType.GRANT_CONFIRM,
            from_addr=patient_wallet.address,
            to_addr=entry["provider_address"],
            data={
                "provider_id": provider_id,
                "record_id": record_id,
                "record_hash": entry["record_hash"],
                "access_level": entry["access_level"],
                "grant_timestamp": time.time(),
            }
        )
        tx_hashes.append(tx.tx_hash)

        # Add to audit log
        if record_id not in audit_logs_db:
            audit_logs_db[record_id] = []
        audit_logs_db[record_id].append({
            "actor": patient_wallet.address,
            "target_provider": entry["provider_address"],
            "action": "GRANT_CONFIRMED",
            "timestamp": time.time(),
            "details": f"Access granted to {entry['provider_name']} for {entry['record_type']}",
            "tx_hash": tx.tx_hash,
        })

    # Mine block
    mine_if_needed()

    # Update pending status
    pending["status"] = "confirmed"

    return jsonify({
        "success": True,
        "pending_id": pending_id,
        "tx_hashes": tx_hashes,
        "block_number": blockchain.get_latest_block().index,
        "provider_name": pending["entries"][0]["provider_name"],
        "records": [records_db[e["record_id"]] for e in pending["entries"]],
        "message": f"Access granted to {pending['entries'][0]['provider_name']}. Confirmed on blockchain.",
    })


@app.route("/api/access/cancel", methods=["POST"])
def cancel_access():
    """
    Cancel a pending access grant before the 60-second countdown expires.

    Request body: { "pending_id": "..." }
    """
    data = request.get_json(silent=True) or {}
    pending_id = data.get("pending_id")

    if not pending_id:
        return jsonify({"success": False, "error": "pending_id is required"}), 400

    pending = pending_grants.get(pending_id)
    if not pending:
        return jsonify({"success": False, "error": "Pending grant not found"}), 404

    if pending["status"] != "pending":
        return jsonify({"success": False, "error": f"Grant is already {pending['status']}"}), 400

    if time.time() >= pending["pending_until"]:
        return jsonify({"success": False, "error": "Pending period has already expired"}), 400

    # Send Solidity transaction for cancelPendingGrant
    if w3.is_connected() and contract:
        for entry in pending["entries"]:
            record_id = entry["record_id"]
            record = records_db[record_id]
            provider = provider_registry[pending["provider_id"]]
            record_hash_bytes = w3.to_bytes(hexstr=record["record_hash"])
            try:
                send_contract_tx(contract.functions.cancelPendingGrant(
                    provider["address"],
                    record_hash_bytes
                ))
            except Exception as e:
                print(f"Error on Solidity cancelPendingGrant: {e}")

    # Create cancellation transaction
    tx = create_blockchain_transaction(
        tx_type=TxType.GRANT_CANCEL,
        from_addr=patient_wallet.address,
        to_addr="system",
        data={
            "pending_id": pending_id,
            "provider_id": pending["provider_id"],
            "record_ids": pending["record_ids"],
            "reason": "Patient cancelled before confirmation",
        }
    )
    mine_if_needed()

    pending["status"] = "cancelled"

    return jsonify({
        "success": True,
        "pending_id": pending_id,
        "tx_hash": tx.tx_hash,
        "message": "Access grant cancelled. No changes were made.",
    })


@app.route("/api/access/revoke", methods=["POST"])
def revoke_access():
    """
    Revoke an active access grant immediately.

    Request body:
    {
        "provider_id": "dr-sarah-chen",
        "record_id": "mri-scan"
    }
    """
    data = request.get_json(silent=True) or {}
    provider_id = data.get("provider_id")
    record_id = data.get("record_id")

    if not provider_id or not record_id:
        return jsonify({"success": False, "error": "provider_id and record_id are required"}), 400

    record_grants = access_grants_db.get(record_id, {})
    grant = record_grants.get(provider_id)
    if not grant or grant.get("status") != "active":
        return jsonify({"success": False, "error": "No active grant found for this provider and record"}), 404

    provider = provider_registry.get(provider_id, {})
    provider_address = provider.get("address", "")

    # Remove the grant
    grant["status"] = "revoked"
    grant["revoked_at"] = time.time()

    # Send Solidity transaction for revokeAccess
    if w3.is_connected() and contract:
        record_hash_bytes = w3.to_bytes(hexstr=grant["record_hash"])
        try:
            send_contract_tx(contract.functions.revokeAccess(
                provider_address,
                record_hash_bytes
            ))
        except Exception as e:
            print(f"Error on Solidity revokeAccess: {e}")

    # Create blockchain revocation transaction
    tx = create_blockchain_transaction(
        tx_type=TxType.REVOKE,
        from_addr=patient_wallet.address,
        to_addr=provider_address,
        data={
            "provider_id": provider_id,
            "record_id": record_id,
            "record_hash": grant["record_hash"],
            "reason": "Patient revoked access",
        }
    )

    # Add to audit log
    if record_id not in audit_logs_db:
        audit_logs_db[record_id] = []
    
    record = records_db.get(record_id, {})
    record_type = record.get("record_type", "Medical Record")
    
    audit_logs_db[record_id].append({
        "actor": patient_wallet.address,
        "target_provider": provider_address,
        "action": "REVOKE",
        "timestamp": time.time(),
        "details": f"Access revoked from {provider.get('name', provider_id)} for {record_type}",
        "tx_hash": tx.tx_hash,
    })

    mine_if_needed()

    return jsonify({
        "success": True,
        "tx_hash": tx.tx_hash,
        "block_number": blockchain.get_latest_block().index,
        "provider_name": provider.get("name", provider_id),
        "record_type": record_type,
        "message": f"Access revoked from {provider.get('name', provider_id)} for {record_type}",
    })


@app.route("/api/access/check", methods=["GET"])
def check_access():
    """
    Check if a provider has access to a specific record.

    Query params:
        provider_id: The provider ID to check
        record_id: The record ID to check
    """
    provider_id = request.args.get("provider_id")
    record_id = request.args.get("record_id")

    if not provider_id or not record_id:
        return jsonify({"error": "provider_id and record_id are required"}), 400

    record = records_db.get(record_id)
    if not record:
        return jsonify({"error": "Record not found"}), 404

    provider = provider_registry.get(provider_id)
    if not provider:
        return jsonify({"error": "Provider not found"}), 404

    grant = access_grants_db.get(record_id, {}).get(provider_id)
    has_access = False
    access_level = 0
    details = {}

    if grant and grant.get("status") == "active":
        # Check expiration
        expiration = grant.get("expiration", 0)
        if expiration == 0 or time.time() < expiration:
            has_access = True
            access_level = grant.get("access_level", 0)
            details = {
                "granted_at": grant.get("grant_timestamp"),
                "expires_at": expiration if expiration > 0 else None,
                "tx_hash": grant.get("tx_hash"),
            }

    # Log the access check attempt
    tx = create_blockchain_transaction(
        tx_type=TxType.ACCESS_ATTEMPT,
        from_addr=provider.get("address", "unknown"),
        to_addr=patient_wallet.address,
        data={
            "provider_id": provider_id,
            "record_id": record_id,
            "success": has_access,
            "access_level": access_level,
        }
    )
    mine_if_needed()

    return jsonify({
        "provider_id": provider_id,
        "provider_name": provider.get("name"),
        "record_id": record_id,
        "record_type": record.get("record_type"),
        "has_access": has_access,
        "access_level": access_level,
        "access_level_name": "VIEW_ONLY" if access_level == 1 else "NONE",
        "details": details,
        "check_tx_hash": tx.tx_hash,
    })


# -------------------------------------------------------------------------
# AUDIT LOG
# -------------------------------------------------------------------------

@app.route("/api/audit/log", methods=["GET"])
def get_audit_log():
    """
    Get the complete audit log for a specific record or all records.

    Query params:
        record_id: The record ID to get audit log for, or "all"
    """
    record_id = request.args.get("record_id")

    if not record_id:
        return jsonify({"error": "record_id is required"}), 400

    if record_id == "all":
        all_logs = []
        for rid in records_db.keys():
            log = audit_logs_db.get(rid, [])
            for entry in log:
                formatted_entry = dict(entry)
                ts = entry.get("timestamp", 0)
                formatted_entry["timestamp_iso"] = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
                formatted_entry["timestamp"] = ts * 1000  # JS Date expects milliseconds
                formatted_entry["transaction_hash"] = entry.get("tx_hash", "0x0000000000000000000000000000000000000000")
                all_logs.append(formatted_entry)
        
        all_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        return jsonify({
            "entries": all_logs,
            "total": len(all_logs)
        })

    if record_id not in records_db:
        return jsonify({"error": "Record not found"}), 404

    log = audit_logs_db.get(record_id, [])

    # Format timestamps for readability
    formatted_log = []
    for entry in log:
        formatted_entry = dict(entry)
        ts = entry.get("timestamp", 0)
        formatted_entry["timestamp_iso"] = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        formatted_entry["timestamp"] = ts
        formatted_log.append(formatted_entry)

    # Add blockchain-level transaction events
    blockchain_events = []
    for block in blockchain.chain:
        for tx in block.transactions:
            if tx.data.get("record_id") == record_id:
                blockchain_events.append({
                    "action": f"BLOCKCHAIN_{tx.tx_type.value.upper()}",
                    "tx_hash": tx.tx_hash,
                    "block_number": block.index,
                    "block_hash": block.hash,
                    "timestamp": tx.timestamp,
                    "timestamp_iso": datetime.fromtimestamp(tx.timestamp, tz=timezone.utc).isoformat(),
                    "from": tx.from_address,
                    "to": tx.to_address,
                    "gas_used": tx.gas_used,
                    "confirmations": tx.confirmations,
                })

    return jsonify({
        "record_id": record_id,
        "record_hash": records_db[record_id]["record_hash"],
        "audit_entries": formatted_log,
        "blockchain_events": blockchain_events,
        "total_entries": len(formatted_log) + len(blockchain_events),
    })


# -------------------------------------------------------------------------
# BLOCKCHAIN STATUS & EXPLORER
# -------------------------------------------------------------------------

@app.route("/api/blockchain/status", methods=["GET"])
def blockchain_status():
    """
    Get the current blockchain connection and ledger status.

    Returns chain statistics, latest block info, and connection status.
    """
    stats = blockchain.get_chain_stats()
    latest = blockchain.get_latest_block()

    return jsonify({
        "connected": w3.is_connected(),
        "network": "EVM Local Node (Hardhat)" if w3.is_connected() else "Local Fallback Ledger",
        "chain_id": 1337,  # Local development chain ID (like Hardhat/Ganache)
        "stats": stats,
        "latest_block": {
            "index": latest.index,
            "hash": latest.hash,
            "timestamp": latest.timestamp,
            "timestamp_iso": datetime.fromtimestamp(latest.timestamp, tz=timezone.utc).isoformat(),
            "transaction_count": len(latest.transactions),
            "merkle_root": latest.merkle_root,
            "previous_hash": latest.previous_hash,
            "difficulty": latest.difficulty,
        },
        "mempool": {
            "size": len(blockchain.mempool),
            "transactions": [tx.to_dict() for tx in blockchain.mempool],
        },
        "gas_price": "20 gwei",
        "patient_wallet": patient_wallet.address,
    })


@app.route("/api/blockchain/explorer", methods=["GET"])
def blockchain_explorer():
    """
    Blockchain explorer - show the entire chain.

    Query params:
        page: Page number (default 1)
        per_page: Items per page (default 10)
    """
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    total_blocks = len(blockchain.chain)
    start = (page - 1) * per_page
    end = start + per_page

    blocks = []
    for block in blockchain.chain[start:end]:
        blocks.append({
            "index": block.index,
            "hash": block.hash,
            "timestamp": block.timestamp,
            "timestamp_iso": datetime.fromtimestamp(block.timestamp, tz=timezone.utc).isoformat(),
            "transaction_count": len(block.transactions),
            "merkle_root": block.merkle_root,
            "previous_hash": block.previous_hash,
            "nonce": block.nonce,
            "difficulty": block.difficulty,
        })

    return jsonify({
        "total_blocks": total_blocks,
        "page": page,
        "per_page": per_page,
        "total_pages": (total_blocks + per_page - 1) // per_page,
        "blocks": blocks,
        "chain_valid": blockchain.is_chain_valid(),
    })


@app.route("/api/blockchain/block/<block_hash>", methods=["GET"])
def get_block_detail(block_hash):
    """Get detailed information about a specific block by its hash."""
    block = blockchain.get_block_by_hash(block_hash)
    if not block:
        return jsonify({"error": "Block not found"}), 404

    return jsonify({
        "block": block.to_dict(),
        "transactions": [tx.to_dict() for tx in block.transactions],
    })


@app.route("/api/blockchain/transaction/<tx_hash>", methods=["GET"])
def get_transaction_detail(tx_hash):
    """Get detailed information about a specific transaction by its hash."""
    tx = blockchain.get_transaction(tx_hash)
    if not tx:
        return jsonify({"error": "Transaction not found"}), 404

    return jsonify({
        "transaction": tx.to_dict(),
    })


@app.route("/api/blockchain/verify", methods=["GET"])
def verify_chain():
    """Verify the integrity of the entire blockchain."""
    valid = blockchain.is_chain_valid()
    return jsonify({
        "valid": valid,
        "chain_length": len(blockchain.chain),
        "message": "Blockchain is valid" if valid else "BLOCKCHAIN CORRUPTED - Chain integrity check failed",
    })


# -------------------------------------------------------------------------
# PROVIDERS
# -------------------------------------------------------------------------

@app.route("/api/providers", methods=["GET"])
def get_providers():
    """Get all registered healthcare providers."""
    return jsonify({
        "providers": list(provider_registry.values()),
        "total": len(provider_registry),
    })


# -------------------------------------------------------------------------
# PENDING GRANTS
# -------------------------------------------------------------------------

@app.route("/api/access/pending", methods=["GET"])
def get_pending_grants():
    """Get all pending grants with their remaining countdown time."""
    active_pending = []
    now = time.time()

    for pending_id, pending in pending_grants.items():
        if pending["status"] == "pending":
            remaining = int(pending["pending_until"] - now)
            if remaining > 0:
                active_pending.append({
                    "pending_id": pending_id,
                    "provider_id": pending["provider_id"],
                    "record_ids": pending["record_ids"],
                    "remaining_seconds": remaining,
                    "pending_until": pending["pending_until"],
                    "pending_until_iso": datetime.fromtimestamp(pending["pending_until"], tz=timezone.utc).isoformat(),
                })
            else:
                # Expired - update status
                pending["status"] = "expired"

    return jsonify({
        "pending_grants": active_pending,
        "count": len(active_pending),
    })


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found", "path": request.path}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error", "message": str(e)}), 500


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # Pre-mine some blocks to establish initial state on the fallback ledger
    print("=" * 60)
    print("HEALTHCARE BLOCKCHAIN ACCESS CONTROL - BACKEND")
    print("=" * 60)
    print(f"Patient wallet: {patient_wallet.address}")
    print(f"Genesis block: {blockchain.chain[0].hash}")
    print(f"Chain length: {len(blockchain.chain)}")
    print("-" * 60)
    print("Pre-mining initial blocks...")

    # Mine a few blocks to establish the chain
    for _ in range(2):
        blockchain.mine_block(miner_address=patient_wallet.address)

    print(f"Chain length after pre-mine: {len(blockchain.chain)}")
    print(f"Latest block: {blockchain.get_latest_block().hash}")
    print("=" * 60)
    
    # Sync records to smart contract on start (avoid double-run in Flask reload mode)
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        sync_records_to_smart_contract()
    
    print("Starting Flask server on http://localhost:5000")
    print("API documentation: http://localhost:5000/api/health")
    print("=" * 60)

    # Run the Flask development server
    app.run(host="0.0.0.0", port=5000, debug=True)
