"""
blockchain_engine.py
A Python module that implements a local blockchain ledger database for indexing and fallback metadata purposes.

This module provides the core blockchain primitives needed to back the
healthcare access control system:
- Blocks with SHA-256 hashing and simple proof-of-work
- Transactions with digital signatures
- Merkle tree roots for transaction integrity
- Wallets with keypair generation
- Chain validation

The engine is designed to be transparent, lightweight, and functionally
equivalent (at the API level) to real blockchain interactions.
"""

import hashlib
import json
import time
import secrets
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def sha256_hash(data: str) -> str:
    """Compute the SHA-256 hash of a string and return as a hex string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def sha256_hash_bytes(data: bytes) -> str:
    """Compute the SHA-256 hash of bytes and return as a hex string."""
    return hashlib.sha256(data).hexdigest()

def current_timestamp() -> float:
    """Return the current UTC timestamp as a float."""
    return datetime.now(timezone.utc).timestamp()


# =============================================================================
# TRANSACTION CLASS
# =============================================================================

class TxType(Enum):
    """Types of transactions in the health access control system."""
    GRANT_INITIATE = "grant_initiate"
    GRANT_CONFIRM = "grant_confirm"
    GRANT_CANCEL = "grant_cancel"
    REVOKE = "revoke"
    ACCESS_ATTEMPT = "access_attempt"
    RECORD_REGISTER = "record_register"
    SYSTEM = "system"


@dataclass
class Transaction:
    """
    Represents a single blockchain transaction.

    In a real blockchain, this is signed by the sender's private key.
    In our local ledger, we include a 'signature' field that is a SHA-256 hash
    of the transaction data plus the sender's private key, proving authenticity.
    """
    from_address: str                  # Sender's wallet address
    to_address: str                      # Recipient (contract or user) address
    tx_type: TxType                     # Transaction type
    data: Dict[str, Any]                # Payload (JSON-serializable dict)
    timestamp: float                    # Unix timestamp
    tx_hash: str                        # Unique transaction hash
    signature: str                      # Digital signature (simulated)
    gas_price: int = 0                  # Gas price in gwei (simulated)
    gas_limit: int = 0                  # Gas limit (simulated)
    gas_used: int = 0                   # Actual gas used (simulated)
    status: str = "pending"             # Transaction status: pending, confirmed, failed
    block_hash: Optional[str] = None    # Block hash after mining
    block_number: Optional[int] = None  # Block index after mining
    confirmations: int = 0              # Number of confirmation blocks
    nonce: int = 0                      # Transaction nonce (anti-replay)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a dictionary."""
        d = asdict(self)
        d["tx_type"] = self.tx_type.value
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Transaction":
        """Deserialize from a dictionary."""
        d = d.copy()
        d["tx_type"] = TxType(d["tx_type"])
        return Transaction(**d)

    def compute_hash(self) -> str:
        """Compute the deterministic transaction hash."""
        payload = json.dumps({
            "from": self.from_address,
            "to": self.to_address,
            "type": self.tx_type.value,
            "data": self.data,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
        }, sort_keys=True, default=str)
        return sha256_hash(payload)

    def verify_signature(self, wallet) -> bool:
        """Verify the transaction signature using the associated wallet."""
        expected = self._compute_signature(wallet)
        return self.signature == expected

    def _compute_signature(self, wallet) -> str:
        """Compute the expected signature for this transaction."""
        payload = f"{self.compute_hash()}:{wallet.private_key}"
        return sha256_hash(payload)

    def sign(self, wallet):
        """Sign this transaction with the given wallet."""
        self.signature = self._compute_signature(wallet)

    def estimate_gas(self) -> int:
        """
        Simulate gas estimation based on transaction complexity.
        In a real EVM, gas is computed based on opcodes executed.
        """
        base_gas = 21000  # Standard transaction base cost
        data_size = len(json.dumps(self.data, default=str))
        data_gas = data_size * 68  # Cost per byte of calldata (non-zero byte)
        type_multiplier = {
            TxType.GRANT_INITIATE: 1.5,
            TxType.GRANT_CONFIRM: 1.2,
            TxType.REVOKE: 1.1,
            TxType.ACCESS_ATTEMPT: 1.3,
            TxType.RECORD_REGISTER: 1.4,
        }.get(self.tx_type, 1.0)
        self.gas_used = int((base_gas + data_gas) * type_multiplier)
        self.gas_limit = int(self.gas_used * 1.5)  # Buffer
        return self.gas_used


# =============================================================================
# MERKLE TREE
# =============================================================================

def build_merkle_root(leaves: List[str]) -> str:
    """
    Build a Merkle tree root from a list of leaf hashes.

    The Merkle tree is a binary hash tree where each parent node is the
    hash of its two children concatenated. If there's an odd number of nodes
    at any level, the last node is duplicated (self-paired).

    This is how Ethereum and Bitcoin verify transaction integrity in a block:
    changing any transaction changes the Merkle root, which changes the block hash.

    Args:
        leaves: List of hex string hashes (transaction hashes)

    Returns:
        The Merkle root hash as a hex string, or the empty hash if no leaves.
    """
    if not leaves:
        return sha256_hash("")

    # Start with leaf hashes
    level = [h for h in leaves]

    while len(level) > 1:
        next_level = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if (i + 1) < len(level) else left
            combined = left + right
            next_level.append(sha256_hash(combined))
        level = next_level

    return level[0]


def merkle_proof(leaves: List[str], leaf_index: int) -> List[str]:
    """
    Generate a Merkle proof for a leaf at a given index.

    Returns a list of sibling hashes at each level, which can be used to
    verify that the leaf is part of the tree with the given root.

    Args:
        leaves: List of leaf hashes
        leaf_index: Index of the leaf to prove

    Returns:
        List of sibling hashes (one per level)
    """
    if not leaves or leaf_index >= len(leaves):
        return []

    proof = []
    level = list(leaves)

    while len(level) > 1:
        is_odd = len(level) % 2 == 1
        if is_odd:
            level.append(level[-1])  # Duplicate last node

        sibling_index = leaf_index + 1 if leaf_index % 2 == 0 else leaf_index - 1
        proof.append(level[sibling_index])

        # Move up to parent level
        next_level = []
        for i in range(0, len(level), 2):
            combined = level[i] + level[i + 1]
            next_level.append(sha256_hash(combined))

        level = next_level
        leaf_index //= 2

    return proof


def verify_merkle_proof(root: str, leaf: str, leaf_index: int, proof: List[str]) -> bool:
    """Verify a Merkle proof that a leaf belongs to a tree with the given root."""
    current = leaf
    for sibling in proof:
        if leaf_index % 2 == 0:
            combined = current + sibling
        else:
            combined = sibling + current
        current = sha256_hash(combined)
        leaf_index //= 2
    return current == root


# =============================================================================
# BLOCK CLASS
# =============================================================================

@dataclass
class Block:
    """
    Represents a single block in the blockchain.

    Each block contains:
    - index: Position in the chain
    - timestamp: When the block was mined
    - transactions: List of included transactions
    - previous_hash: Hash of the previous block (creates the chain link)
    - merkle_root: Root hash of the Merkle tree over transactions
    - nonce: Number used in proof-of-work (tuned until hash meets difficulty)
    - hash: The block's own SHA-256 hash
    """
    index: int
    timestamp: float
    transactions: List[Transaction] = field(default_factory=list)
    previous_hash: str = ""
    merkle_root: str = ""
    nonce: int = 0
    hash: str = ""
    difficulty: int = 4  # Number of leading zeros required (e.g., 4 = "0000...")

    def compute_hash(self) -> str:
        """Compute the block hash from its contents (excluding the cached hash)."""
        tx_hashes = [tx.tx_hash for tx in self.transactions]
        self.merkle_root = build_merkle_root(tx_hashes)

        block_data = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "merkle_root": self.merkle_root,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }, sort_keys=True, default=str)
        return sha256_hash(block_data)

    def mine(self, difficulty: int) -> str:
        """
        Simple proof-of-work: find a nonce such that the block hash
        starts with `difficulty` number of zeros.

        In real Bitcoin/Ethereum, the difficulty is much higher and the
        hash function is different (Ethash, Keccak-256), but the concept
        is identical: miners compete to find a valid nonce first.

        Args:
            difficulty: Number of leading zeros required

        Returns:
            The mined block hash
        """
        target = "0" * difficulty
        self.difficulty = difficulty
        while True:
            self.hash = self.compute_hash()
            if self.hash.startswith(target):
                break
            self.nonce += 1
        return self.hash

    def to_dict(self) -> Dict[str, Any]:
        """Serialize block to dictionary."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "nonce": self.nonce,
            "hash": self.hash,
            "difficulty": self.difficulty,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Block":
        """Deserialize block from dictionary."""
        block = Block(
            index=d["index"],
            timestamp=d["timestamp"],
            previous_hash=d["previous_hash"],
            merkle_root=d.get("merkle_root", ""),
            nonce=d.get("nonce", 0),
            hash=d.get("hash", ""),
            difficulty=d.get("difficulty", 4),
        )
        block.transactions = [Transaction.from_dict(tx) for tx in d.get("transactions", [])]
        return block

    def is_valid(self, previous_hash: str, difficulty: int) -> bool:
        """Validate this block independently."""
        if self.previous_hash != previous_hash:
            return False
        if not self.hash.startswith("0" * difficulty):
            return False
        # Recompute hash and verify it matches
        computed = self.compute_hash()
        if computed != self.hash:
            return False
        return True


# =============================================================================
# WALLET CLASS
# =============================================================================

class Wallet:
    """
    Simulates an Ethereum wallet with a public/private keypair.

    In a real blockchain, these would be secp256k1 ECDSA keys (like Bitcoin/Ethereum).
    Here we simulate with SHA-256-based "keys" for simplicity and education.
    """

    def __init__(self, private_key: Optional[str] = None):
        """
        Create a wallet. If no private key is provided, generate a random one.
        """
        if private_key:
            self.private_key = private_key
        else:
            self.private_key = "0x" + secrets.token_hex(32)

        # "Address" is derived from the public key hash
        self.public_key = sha256_hash(self.private_key)
        self.address = "0x" + sha256_hash(self.public_key)[:40]

    def sign_transaction(self, tx: Transaction) -> str:
        """Sign a transaction with this wallet's private key."""
        tx.sign(self)
        return tx.signature

    def verify_signature(self, tx: Transaction) -> bool:
        """Verify that a transaction was signed by this wallet."""
        return tx.verify_signature(self)

    def to_dict(self) -> Dict[str, str]:
        """Serialize wallet (for debugging - NEVER share private keys in production!)."""
        return {
            "address": self.address,
            "public_key": self.public_key,
            "private_key": self.private_key,  # In production, never expose this!
        }

    @staticmethod
    def generate_keypair() -> "Wallet":
        """Generate a new random wallet."""
        return Wallet()


# =============================================================================
# BLOCKCHAIN CLASS
# =============================================================================

class Blockchain:
    """
    Implements a complete blockchain with blocks, mempool, mining, and validation.

    This is the core engine that powers the backend local ledger. It provides:
    - A genesis block (the first block in the chain)
    - A mempool (pending transaction pool)
    - Mining (proof-of-work block creation)
    - Chain validation (integrity checks)
    - Block lookup by hash
    """

    def __init__(self, difficulty: int = 4):
        """
        Initialize a new blockchain with a genesis block.

        Args:
            difficulty: Proof-of-work difficulty (number of leading zeros)
        """
        self.chain: List[Block] = []
        self.mempool: List[Transaction] = []
        self.difficulty: int = difficulty
        self.pending_transactions: List[Transaction] = []
        self.create_genesis_block()

    # -------------------------------------------------------------------------
    # GENESIS BLOCK
    # -------------------------------------------------------------------------

    def create_genesis_block(self) -> Block:
        """
        Create the first block in the chain (genesis block).
        The genesis block has no previous block, so its previous_hash is empty.
        """
        genesis = Block(
            index=0,
            timestamp=current_timestamp(),
            transactions=[],
            previous_hash="0" * 64,
        )
        genesis.mine(self.difficulty)
        self.chain.append(genesis)
        return genesis

    # -------------------------------------------------------------------------
    # TRANSACTIONS & MEMPOOL
    # -------------------------------------------------------------------------

    def add_transaction(self, tx: Transaction) -> bool:
        """
        Add a transaction to the mempool after validating it.

        Validation checks:
        - Transaction has a valid hash
        - Transaction has a valid signature
        - No duplicate transaction in mempool
        - Transaction is not already in a confirmed block

        Args:
            tx: The transaction to add

        Returns:
            True if added to mempool, False otherwise
        """
        # Verify transaction hash is correct
        expected_hash = tx.compute_hash()
        if tx.tx_hash != expected_hash:
            tx.tx_hash = expected_hash  # Auto-correct if mismatch

        # Check for duplicate in mempool
        for pending in self.mempool:
            if pending.tx_hash == tx.tx_hash:
                return False

        # Check for duplicate in chain
        for block in self.chain:
            for confirmed_tx in block.transactions:
                if confirmed_tx.tx_hash == tx.tx_hash:
                    return False

        tx.status = "pending"
        tx.estimate_gas()
        self.mempool.append(tx)
        return True

    def get_pending_transactions(self) -> List[Transaction]:
        """Return all transactions currently in the mempool."""
        return self.mempool

    def remove_from_mempool(self, tx_hash: str) -> bool:
        """Remove a transaction from the mempool by hash."""
        for i, tx in enumerate(self.mempool):
            if tx.tx_hash == tx_hash:
                self.mempool.pop(i)
                return True
        return False

    # -------------------------------------------------------------------------
    # MINING
    # -------------------------------------------------------------------------

    def mine_block(self, miner_address: str = "0x0000000000000000000000000000000000000000") -> Block:
        """
        Mine a new block containing all current mempool transactions.

        Simulates the mining process by:
        1. Taking all transactions from the mempool
        2. Creating a new block with the previous block's hash
        3. Running proof-of-work to find a valid nonce
        4. Adding the block to the chain
        5. Clearing the mempool
        6. Updating transaction statuses and confirmation counts

        Args:
            miner_address: The address that "mined" the block (reward recipient)

        Returns:
            The newly mined block
        """
        # Create a system reward transaction for the miner
        reward_tx = Transaction(
            from_address="0x0000000000000000000000000000000000000000",
            to_address=miner_address,
            tx_type=TxType.SYSTEM,
            data={"reward": 2.0, "message": "Block mining reward"},
            timestamp=current_timestamp(),
            tx_hash="",
            signature="system",
            nonce=0,
        )
        reward_tx.tx_hash = reward_tx.compute_hash()

        # Collect mempool transactions + reward
        block_transactions = self.mempool.copy()
        block_transactions.insert(0, reward_tx)

        previous_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            timestamp=current_timestamp(),
            transactions=block_transactions,
            previous_hash=previous_block.hash,
        )
        new_block.mine(self.difficulty)

        # Update transaction statuses
        for tx in block_transactions:
            tx.status = "confirmed"
            if not tx.block_hash:
                tx.block_hash = new_block.hash
            if tx.block_number is None:
                tx.block_number = new_block.index
            tx.confirmations = 1

        self.chain.append(new_block)
        self.mempool = []

        # Update confirmations for older blocks
        self._update_confirmations()

        return new_block

    def _update_confirmations(self):
        """Increment confirmation count for transactions in older blocks."""
        for block in self.chain:
            for tx in block.transactions:
                tx.confirmations = len(self.chain) - block.index

    # -------------------------------------------------------------------------
    # VALIDATION
    # -------------------------------------------------------------------------

    def is_chain_valid(self) -> bool:
        """
        Validate the entire blockchain integrity.

        Checks:
        - Genesis block exists and has correct properties
        - Each block's previous_hash matches the actual hash of the previous block
        - Each block's hash meets the difficulty target
        - Each block's Merkle root is correct

        Returns:
            True if the chain is valid, False otherwise
        """
        if len(self.chain) == 0:
            return False

        # Validate genesis block
        genesis = self.chain[0]
        if genesis.index != 0:
            return False
        if genesis.previous_hash != "0" * 64:
            return False

        # Validate each block in sequence
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if not current.is_valid(previous.hash, self.difficulty):
                return False

            # Verify Merkle root
            tx_hashes = [tx.tx_hash for tx in current.transactions]
            expected_merkle = build_merkle_root(tx_hashes)
            if current.merkle_root != expected_merkle:
                return False

        return True

    # -------------------------------------------------------------------------
    # LOOKUP
    # -------------------------------------------------------------------------

    def get_latest_block(self) -> Block:
        """Return the most recently mined block."""
        return self.chain[-1]

    def get_block_by_hash(self, block_hash: str) -> Optional[Block]:
        """Find a block by its hash."""
        for block in self.chain:
            if block.hash == block_hash:
                return block
        return None

    def get_block_by_index(self, index: int) -> Optional[Block]:
        """Find a block by its index (block number)."""
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None

    def get_transaction(self, tx_hash: str) -> Optional[Transaction]:
        """Find a transaction by its hash (searches mempool and chain)."""
        # Check mempool first
        for tx in self.mempool:
            if tx.tx_hash == tx_hash:
                return tx
        # Search chain
        for block in self.chain:
            for tx in block.transactions:
                if tx.tx_hash == tx_hash:
                    return tx
        return None

    # -------------------------------------------------------------------------
    # CHAIN STATS
    # -------------------------------------------------------------------------

    def get_chain_stats(self) -> Dict[str, Any]:
        """Return statistics about the blockchain."""
        total_tx = sum(len(block.transactions) for block in self.chain)
        return {
            "chain_length": len(self.chain),
            "difficulty": self.difficulty,
            "mempool_size": len(self.mempool),
            "total_confirmed_transactions": total_tx,
            "latest_block_hash": self.chain[-1].hash if self.chain else None,
            "latest_block_index": self.chain[-1].index if self.chain else None,
            "is_valid": self.is_chain_valid(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the entire blockchain to a dictionary."""
        return {
            "chain": [block.to_dict() for block in self.chain],
            "mempool": [tx.to_dict() for tx in self.mempool],
            "difficulty": self.difficulty,
        }

    # -------------------------------------------------------------------------
    # DIFFICULTY ADJUSTMENT (EDUCATIONAL)
    # -------------------------------------------------------------------------

    def adjust_difficulty(self, target_block_time: float = 10.0) -> int:
        """
        Adjust mining difficulty based on actual block time.
        This is how Bitcoin's difficulty adjustment works (every 2016 blocks).

        Args:
            target_block_time: Target time between blocks in seconds

        Returns:
            The new difficulty level
        """
        if len(self.chain) < 2:
            return self.difficulty

        last_block = self.chain[-1]
        prev_block = self.chain[-2]
        actual_time = last_block.timestamp - prev_block.timestamp

        if actual_time < target_block_time / 2:
            self.difficulty += 1
        elif actual_time > target_block_time * 2 and self.difficulty > 1:
            self.difficulty -= 1

        return self.difficulty


# =============================================================================
# DEMO / TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("LOCAL BLOCKCHAIN LEDGER ENGINE - DEMONSTRATION")
    print("=" * 60)

    # Create wallets
    patient_wallet = Wallet.generate_keypair()
    provider_wallet = Wallet.generate_keypair()
    print(f"\nPatient Wallet: {patient_wallet.address}")
    print(f"Provider Wallet: {provider_wallet.address}")

    # Create blockchain
    blockchain = Blockchain(difficulty=3)  # Lower difficulty for fast demo
    print(f"\nGenesis block created: {blockchain.chain[0].hash}")

    # Create and sign transactions
    tx1 = Transaction(
        from_address=patient_wallet.address,
        to_address="contract_health_access",
        tx_type=TxType.GRANT_INITIATE,
        data={
            "provider": provider_wallet.address,
            "record_hash": "abc123...",
            "access_level": 1,
        },
        timestamp=current_timestamp(),
        tx_hash="",
        signature="",
        nonce=1,
    )
    tx1.tx_hash = tx1.compute_hash()
    patient_wallet.sign_transaction(tx1)
    blockchain.add_transaction(tx1)
    print(f"\nTransaction added to mempool: {tx1.tx_hash}")
    print(f"Gas estimate: {tx1.gas_used} gas units")

    # Mine the block
    block = blockchain.mine_block(miner_address=patient_wallet.address)
    print(f"\nBlock {block.index} mined: {block.hash}")
    print(f"Merkle root: {block.merkle_root}")
    print(f"Nonce: {block.nonce}")
    print(f"Transactions in block: {len(block.transactions)}")

    # Validate chain
    print(f"\nChain valid: {blockchain.is_chain_valid()}")
    print(f"Chain stats: {blockchain.get_chain_stats()}")

    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
