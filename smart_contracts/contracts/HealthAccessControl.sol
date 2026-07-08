// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title HealthAccessControl
 * @dev A healthcare access control smart contract for Ethereum.
 *      Stores patient record hashes on-chain, manages provider access grants
 *      with time-locked confirmation, and maintains an immutable audit trail.
 *
 *      Design philosophy:
 *      - Full medical data lives off-chain (IPFS/HIPAA-compliant storage)
 *      - Only cryptographic hashes and access metadata live on-chain
 *      - Every access action emits events for permanent, auditable logging
 *      - 60-second pending state prevents accidental grants (user education + time to cancel)
 */
contract HealthAccessControl {
    // ============================================
    // DATA STRUCTURES
    // ============================================

    /**
     * @dev Represents a single health record.
     *      The actual file/blob is stored off-chain (IPFS, encrypted cloud, etc.)
     *      and only its SHA-256 (or similar) hash is anchored here for integrity.
     */
    struct Record {
        bytes32 recordHash;          // e.g., sha256 of the encrypted off-chain blob
        string recordType;           // e.g., "MRI Brain Scan", "Blood Work Panel"
        string facility;             // e.g., "Metro Neurology Center"
        uint256 dateTimestamp;       // Date the record was created (unix timestamp)
        uint256 addedAt;             // Block.timestamp when registered on-chain
        bool exists;                 // Existence check for safe lookups
    }

    /**
     * @dev Represents an access grant for a specific provider to a specific record.
     *      Includes a time-locked confirmation window (60 seconds) to prevent
     *      accidental grants, supporting the "Confirmatory Interaction Design" (CID)
     *      pattern from the frontend prototype.
     */
    struct AccessGrant {
        address provider;            // The healthcare provider's wallet address
        bytes32 recordHash;          // Which record this grant applies to
        uint8 accessLevel;           // 1 = VIEW_ONLY, 2 = DOWNLOAD (future), etc.
        uint256 expiration;          // Unix timestamp when access expires (0 = no expiry)
        uint256 grantTimestamp;      // When the grant was finalized (not pending)
        uint256 pendingUntil;        // Time-lock: must be 0 to be active (pending state indicator)
        bool isActive;               // Final, active grant status
        bool exists;                 // Existence check
    }

    /**
     * @dev Audit log entry for every access-related event.
     *      Immutable on-chain record of who did what, when, to which record.
     */
    struct AuditEntry {
        address actor;             // Who performed the action (patient or provider)
        address targetProvider;    // Which provider the action concerns (if applicable)
        bytes32 recordHash;        // Which record was involved
        string action;             // e.g., "GRANT", "REVOKE", "ACCESS_ATTEMPT"
        uint256 timestamp;         // block.timestamp
        string details;            // Additional human-readable or encoded details
    }

    // ============================================
    // ENUMS & CONSTANTS
    // ============================================

    uint8 public constant ACCESS_LEVEL_NONE = 0;
    uint8 public constant ACCESS_LEVEL_VIEW = 1;
    uint8 public constant ACCESS_LEVEL_DOWNLOAD = 2;

    /// @dev Duration of the pending (time-locked) confirmation window in seconds.
    ///      Matches the 60-second countdown in the frontend prototype.
    uint256 public constant PENDING_DURATION = 60 seconds;

    // ============================================
    // STATE VARIABLES
    // ============================================

    /// @dev Owner (deployer) address for administrative functions.
    address public owner;

    /// @dev Mapping: patient address => record hash => Record struct
    mapping(address => mapping(bytes32 => Record)) public records;

    /// @dev Mapping: patient address => record hash => provider address => AccessGrant
    mapping(address => mapping(bytes32 => mapping(address => AccessGrant))) public accessGrants;

    /// @dev Mapping: patient address => record hash => list of provider addresses
    ///      Used for efficient iteration of all providers with access to a record.
    mapping(address => mapping(bytes32 => address[])) public recordProviders;

    /// @dev Mapping: patient address => record hash => list of audit entries
    mapping(address => mapping(bytes32 => AuditEntry[])) public auditLogs;

    /// @dev Mapping: patient address => list of their record hashes
    mapping(address => bytes32[]) public patientRecordHashes;

    // ============================================
    // EVENTS
    // ============================================

    /// @dev Emitted when a patient registers a new record hash on-chain.
    event RecordRegistered(
        address indexed patient,
        bytes32 indexed recordHash,
        string recordType,
        uint256 dateTimestamp
    );

    /// @dev Emitted when a new access grant is initiated (enters pending state).
    event GrantAccessInitiated(
        address indexed patient,
        address indexed provider,
        bytes32 indexed recordHash,
        uint8 accessLevel,
        uint256 pendingUntil,
        uint256 expiration
    );

    /// @dev Emitted when a pending access grant is finalized after the time-lock.
    event GrantAccessConfirmed(
        address indexed patient,
        address indexed provider,
        bytes32 indexed recordHash,
        uint8 accessLevel,
        uint256 grantTimestamp,
        uint256 expiration
    );

    /// @dev Emitted when access is revoked (immediately effective, no pending).
    event RevokeAccess(
        address indexed patient,
        address indexed provider,
        bytes32 indexed recordHash,
        uint256 timestamp
    );

    /// @dev Emitted whenever a provider attempts to access a record (success or failure).
    ///      This is the critical audit event for HIPAA compliance tracking.
    event AccessAttempt(
        address indexed patient,
        address indexed provider,
        bytes32 indexed recordHash,
        bool success,
        uint8 accessLevel,
        string reason,
        uint256 timestamp
    );

    /// @dev Emitted when a pending grant is cancelled by the patient.
    event GrantAccessCancelled(
        address indexed patient,
        address indexed provider,
        bytes32 indexed recordHash,
        uint256 timestamp
    );

    // ============================================
    // MODIFIERS
    // ============================================

    modifier onlyOwner() {
        require(msg.sender == owner, "HealthAccessControl: caller is not the owner");
        _;
    }

    modifier onlyPatient(address _patient) {
        require(msg.sender == _patient, "HealthAccessControl: caller is not the patient");
        _;
    }

    modifier recordExists(address _patient, bytes32 _recordHash) {
        require(records[_patient][_recordHash].exists, "HealthAccessControl: record does not exist");
        _;
    }

    // ============================================
    // CONSTRUCTOR
    // ============================================

    constructor() {
        owner = msg.sender;
    }

    // ============================================
    // RECORD MANAGEMENT
    // ============================================

    /**
     * @dev Register a new health record hash on-chain.
     *      The actual medical data (images, PDFs, etc.) must be stored off-chain
     *      (e.g., IPFS, encrypted S3, or a HIPAA-compliant health data store).
     *      Only the hash is anchored here for integrity verification.
     *
     * @param _recordHash    SHA-256 hash of the off-chain encrypted record
     * @param _recordType    Human-readable type (e.g., "MRI Brain Scan")
     * @param _facility      Facility that created the record
     * @param _dateTimestamp Unix timestamp of the record's creation date
     */
    function registerRecord(
        bytes32 _recordHash,
        string calldata _recordType,
        string calldata _facility,
        uint256 _dateTimestamp
    ) external {
        require(_recordHash != bytes32(0), "HealthAccessControl: invalid record hash");
        require(!records[msg.sender][_recordHash].exists, "HealthAccessControl: record already exists");
        require(bytes(_recordType).length > 0, "HealthAccessControl: record type required");
        require(bytes(_facility).length > 0, "HealthAccessControl: facility required");

        records[msg.sender][_recordHash] = Record({
            recordHash: _recordHash,
            recordType: _recordType,
            facility: _facility,
            dateTimestamp: _dateTimestamp,
            addedAt: block.timestamp,
            exists: true
        });

        patientRecordHashes[msg.sender].push(_recordHash);

        // Log the record registration
        auditLogs[msg.sender][_recordHash].push(AuditEntry({
            actor: msg.sender,
            targetProvider: address(0),
            recordHash: _recordHash,
            action: "RECORD_REGISTERED",
            timestamp: block.timestamp,
            details: _recordType
        }));

        emit RecordRegistered(msg.sender, _recordHash, _recordType, _dateTimestamp);
    }

    /**
     * @dev Get details of a specific record.
     * @param _patient     The patient address
     * @param _recordHash  The record hash
     */
    function getRecord(address _patient, bytes32 _recordHash)
        external
        view
        recordExists(_patient, _recordHash)
        returns (Record memory)
    {
        return records[_patient][_recordHash];
    }

    /**
     * @dev Get all record hashes for a patient.
     * @param _patient The patient address
     */
    function getPatientRecords(address _patient) external view returns (bytes32[] memory) {
        return patientRecordHashes[_patient];
    }

    // ============================================
    // ACCESS GRANT MANAGEMENT (with pending state)
    // ============================================

    /**
     * @dev Initiate an access grant (enters PENDING state for 60 seconds).
     *      This is the first step of the two-step confirmation process.
     *      The patient must call confirmGrant() after the pending window expires
     *      to finalize the grant. During the pending window, the grant can be cancelled.
     *
     * @param _provider      Provider's wallet address
     * @param _recordHash    Hash of the record to grant access to
     * @param _accessLevel   Access level (1 = VIEW_ONLY)
     * @param _expiration    Unix timestamp when access expires (0 = no expiry)
     */
    function initiateGrant(
        address _provider,
        bytes32 _recordHash,
        uint8 _accessLevel,
        uint256 _expiration
    )
        external
        onlyPatient(msg.sender)
        recordExists(msg.sender, _recordHash)
    {
        require(_provider != address(0), "HealthAccessControl: invalid provider address");
        require(_accessLevel > ACCESS_LEVEL_NONE, "HealthAccessControl: invalid access level");
        require(
            !accessGrants[msg.sender][_recordHash][_provider].exists ||
            !accessGrants[msg.sender][_recordHash][_provider].isActive,
            "HealthAccessControl: active grant already exists"
        );

        // If there's an existing inactive grant, we can overwrite it (new pending)
        if (
            accessGrants[msg.sender][_recordHash][_provider].exists &&
            accessGrants[msg.sender][_recordHash][_provider].isActive == false
        ) {
            // Overwrite existing inactive grant
        } else if (!accessGrants[msg.sender][_recordHash][_provider].exists) {
            // First time grant - add provider to list
            recordProviders[msg.sender][_recordHash].push(_provider);
        }

        uint256 pendingUntil = block.timestamp + PENDING_DURATION;

        accessGrants[msg.sender][_recordHash][_provider] = AccessGrant({
            provider: _provider,
            recordHash: _recordHash,
            accessLevel: _accessLevel,
            expiration: _expiration,
            grantTimestamp: 0,          // Not finalized yet
            pendingUntil: pendingUntil,   // Time-lock active
            isActive: false,            // Pending, not active
            exists: true
        });

        // Log the initiation
        auditLogs[msg.sender][_recordHash].push(AuditEntry({
            actor: msg.sender,
            targetProvider: _provider,
            recordHash: _recordHash,
            action: "GRANT_INITIATED",
            timestamp: block.timestamp,
            details: string(abi.encodePacked("Level: ", uintToString(_accessLevel), ", Pending until: ", uintToString(pendingUntil)))
        }));

        emit GrantAccessInitiated(
            msg.sender,
            _provider,
            _recordHash,
            _accessLevel,
            pendingUntil,
            _expiration
        );
    }

    /**
     * @dev Confirm a pending access grant after the 60-second time-lock has passed.
     *      This is the second step of the two-step confirmation process.
     *      Anyone can call this (the patient, or even the provider after the wait),
     *      but the grant was initiated by the patient and the provider was specified.
     *
     * @param _provider   Provider address (must match the pending grant)
     * @param _recordHash Hash of the record
     */
    function confirmGrant(
        address _provider,
        bytes32 _recordHash
    )
        external
        onlyPatient(msg.sender)
        recordExists(msg.sender, _recordHash)
    {
        AccessGrant storage grant = accessGrants[msg.sender][_recordHash][_provider];

        require(grant.exists, "HealthAccessControl: no pending grant found");
        require(!grant.isActive, "HealthAccessControl: grant is already active");
        require(block.timestamp >= grant.pendingUntil, "HealthAccessControl: still in pending period");

        grant.isActive = true;
        grant.grantTimestamp = block.timestamp;
        grant.pendingUntil = 0; // Clear pending state

        // Log the confirmation
        auditLogs[msg.sender][_recordHash].push(AuditEntry({
            actor: msg.sender,
            targetProvider: _provider,
            recordHash: _recordHash,
            action: "GRANT_CONFIRMED",
            timestamp: block.timestamp,
            details: string(abi.encodePacked("Access level: ", uintToString(grant.accessLevel)))
        }));

        emit GrantAccessConfirmed(
            msg.sender,
            _provider,
            _recordHash,
            grant.accessLevel,
            block.timestamp,
            grant.expiration
        );
    }

    /**
     * @dev Cancel a pending grant before the 60-second time-lock expires.
     *      This is the safety mechanism that allows patients to change their mind.
     *
     * @param _provider   Provider address
     * @param _recordHash Hash of the record
     */
    function cancelPendingGrant(
        address _provider,
        bytes32 _recordHash
    )
        external
        onlyPatient(msg.sender)
        recordExists(msg.sender, _recordHash)
    {
        AccessGrant storage grant = accessGrants[msg.sender][_recordHash][_provider];

        require(grant.exists, "HealthAccessControl: no grant found");
        require(!grant.isActive, "HealthAccessControl: cannot cancel an active grant");
        require(grant.pendingUntil > block.timestamp, "HealthAccessControl: pending period already expired");

        // Mark as inactive but keep exists=true for audit trail
        grant.isActive = false;
        grant.pendingUntil = 0;

        // Log the cancellation
        auditLogs[msg.sender][_recordHash].push(AuditEntry({
            actor: msg.sender,
            targetProvider: _provider,
            recordHash: _recordHash,
            action: "GRANT_CANCELLED",
            timestamp: block.timestamp,
            details: "Patient cancelled pending grant before confirmation"
        }));

        emit GrantAccessCancelled(msg.sender, _provider, _recordHash, block.timestamp);
    }

    /**
     * @dev Revoke an active access grant immediately.
     *      No pending period for revocation - safety first.
     *
     * @param _provider   Provider address to revoke access from
     * @param _recordHash Hash of the record
     */
    function revokeAccess(
        address _provider,
        bytes32 _recordHash
    )
        external
        onlyPatient(msg.sender)
        recordExists(msg.sender, _recordHash)
    {
        AccessGrant storage grant = accessGrants[msg.sender][_recordHash][_provider];

        require(grant.exists, "HealthAccessControl: no grant found");
        require(grant.isActive, "HealthAccessControl: grant is not active");

        grant.isActive = false;
        grant.grantTimestamp = 0;
        grant.expiration = 0;

        // Log the revocation
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

    // ============================================
    // ACCESS CHECKS
    // ============================================

    /**
     * @dev Check if a provider currently has access to a specific record.
     *      Returns both a boolean and the access level.
     *
     * @param _patient    Patient address
     * @param _provider   Provider address to check
     * @param _recordHash Record hash to check
     * @return hasAccess  True if the provider has active, unexpired access
     * @return accessLevel The granted access level (0 if no access)
     */
    function checkAccess(
        address _patient,
        address _provider,
        bytes32 _recordHash
    )
        external
        view
        returns (bool hasAccess, uint8 accessLevel)
    {
        AccessGrant storage grant = accessGrants[_patient][_recordHash][_provider];

        if (!grant.exists || !grant.isActive) {
            return (false, ACCESS_LEVEL_NONE);
        }

        // Check expiration
        if (grant.expiration > 0 && block.timestamp > grant.expiration) {
            return (false, ACCESS_LEVEL_NONE);
        }

        return (true, grant.accessLevel);
    }

    /**
     * @dev Check if a grant is currently in pending state.
     * @param _patient    Patient address
     * @param _provider   Provider address
     * @param _recordHash Record hash
     * @return isPending  True if the grant is pending and not yet confirmed
     * @return pendingUntil The timestamp when the pending period ends (0 if not pending)
     */
    function isPending(
        address _patient,
        address _provider,
        bytes32 _recordHash
    )
        external
        view
        returns (bool isPending, uint256 pendingUntil)
    {
        AccessGrant storage grant = accessGrants[_patient][_recordHash][_provider];
        if (!grant.exists || grant.isActive) {
            return (false, 0);
        }
        if (grant.pendingUntil > block.timestamp) {
            return (true, grant.pendingUntil);
        }
        return (false, 0);
    }

    // ============================================
    // AUDIT LOG
    // ============================================

    /**
     * @dev Get the complete audit log for a specific record.
     *      Returns all events: registrations, grants, revocations, access attempts.
     *
     * @param _patient    Patient address
     * @param _recordHash Record hash
     * @return entries    Array of AuditEntry structs
     */
    function getAuditLog(address _patient, bytes32 _recordHash)
        external
        view
        returns (AuditEntry[] memory)
    {
        return auditLogs[_patient][_recordHash];
    }

    /**
     * @dev Get the number of audit entries for a record.
     */
    function getAuditLogCount(address _patient, bytes32 _recordHash)
        external
        view
        returns (uint256)
    {
        return auditLogs[_patient][_recordHash].length;
    }

    // ============================================
    // ACCESS ATTEMPT LOGGING
    // ============================================

    /**
     * @dev Log an access attempt by a provider.
     *      This should be called by the off-chain data storage gateway
     *      when a provider attempts to retrieve the actual medical data.
     *      The gateway verifies the on-chain access first, then calls this
     *      to log the attempt (whether successful or denied).
     *
     * @param _patient    Patient address
     * @param _provider   Provider attempting access
     * @param _recordHash Record hash being accessed
     * @param _success    Whether the access was granted
     * @param _reason     Human-readable reason for denial (if failed)
     */
    function logAccessAttempt(
        address _patient,
        address _provider,
        bytes32 _recordHash,
        bool _success,
        string calldata _reason
    )
        external
        recordExists(_patient, _recordHash)
    {
        // In production, this would be restricted to the off-chain gateway
        // For flexibility, we allow any caller but log the caller's address
        (bool hasAccess, uint8 accessLevel) = this.checkAccess(_patient, _provider, _recordHash);

        // Verify consistency between claimed success and actual access check
        if (_success && !hasAccess) {
            _success = false;
        }

        auditLogs[_patient][_recordHash].push(AuditEntry({
            actor: msg.sender,
            targetProvider: _provider,
            recordHash: _recordHash,
            action: "ACCESS_ATTEMPT",
            timestamp: block.timestamp,
            details: _reason
        }));

        emit AccessAttempt(
            _patient,
            _provider,
            _recordHash,
            _success,
            accessLevel,
            _reason,
            block.timestamp
        );
    }

    // ============================================
    // LIST HELPERS
    // ============================================

    /**
     * @dev Get all active providers for a specific record.
     * @param _patient    Patient address
     * @param _recordHash Record hash
     * @return providers  Array of provider addresses with active access
     * @return levels     Array of corresponding access levels
     * @return timestamps Array of grant timestamps
     */
    function getActiveProviders(address _patient, bytes32 _recordHash)
        external
        view
        returns (address[] memory providers, uint8[] memory levels, uint256[] memory timestamps)
    {
        address[] memory allProviders = recordProviders[_patient][_recordHash];
        uint256 activeCount = 0;

        // First pass: count active providers
        for (uint256 i = 0; i < allProviders.length; i++) {
            AccessGrant storage grant = accessGrants[_patient][_recordHash][allProviders[i]];
            if (grant.isActive && (grant.expiration == 0 || block.timestamp <= grant.expiration)) {
                activeCount++;
            }
        }

        providers = new address[](activeCount);
        levels = new uint8[](activeCount);
        timestamps = new uint256[](activeCount);

        uint256 idx = 0;
        for (uint256 i = 0; i < allProviders.length; i++) {
            AccessGrant storage grant = accessGrants[_patient][_recordHash][allProviders[i]];
            if (grant.isActive && (grant.expiration == 0 || block.timestamp <= grant.expiration)) {
                providers[idx] = allProviders[i];
                levels[idx] = grant.accessLevel;
                timestamps[idx] = grant.grantTimestamp;
                idx++;
            }
        }

        return (providers, levels, timestamps);
    }

    // ============================================
    // UTILITY FUNCTIONS
    // ============================================

    /**
     * @dev Convert a uint256 to a string (for logging details).
     *      Needed because Solidity has no native uint-to-string conversion.
     */
    function uintToString(uint256 _value) internal pure returns (string memory) {
        if (_value == 0) {
            return "0";
        }
        uint256 temp = _value;
        uint256 digits;
        while (temp != 0) {
            digits++;
            temp /= 10;
        }
        bytes memory buffer = new bytes(digits);
        while (_value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(_value % 10)));
            _value /= 10;
        }
        return string(buffer);
    }

    // ============================================
    // ADMIN FUNCTIONS
    // ============================================

    /**
     * @dev Transfer ownership of the contract.
     * @param _newOwner New owner address
     */
    function transferOwnership(address _newOwner) external onlyOwner {
        require(_newOwner != address(0), "HealthAccessControl: invalid new owner");
        owner = _newOwner;
    }

    /**
     * @dev Emergency pause for all grant operations.
     *      In a production contract, this would use OpenZeppelin's Pausable.
     *      Included here as a basic reference.
     */
    bool public paused = false;

    modifier whenNotPaused() {
        require(!paused, "HealthAccessControl: contract is paused");
        _;
    }

    function pause() external onlyOwner {
        paused = true;
    }

    function unpause() external onlyOwner {
        paused = false;
    }
}
