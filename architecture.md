# BCHAIN-ACCESS Reference Architecture

This document describes the implemented research artifact. Anything listed as future work is not part of the tested system.

## Implemented path

```text
HTML/CSS/JavaScript interface
          |
          | HTTP/JSON
          v
Flask gateway and API-managed session/state
          |
          +-------------------------------+
          |                               |
          v                               v
Configured Web3.py contract binding       Explicit in-memory fallback
          |                               (when no contract is bound)
          v
HealthAccessControl.sol on local Hardhat EVM
```

The Cycle 2 interface in `core/frontend/index.html` contains its API client directly. `core/integration/frontend_integration.js` is a legacy optional adapter and is not loaded by, or evidence for, the Cycle 2 reference interface.

## Interface behavior

The interface provides:

- simulated fingerprint entry, not biometric authentication;
- three seeded demonstration records and four seeded providers;
- selection of exactly one record for a state-changing grant request;
- plain-language review showing view-only access and no expiry in the current demonstration;
- a 60-second minimum wait before confirmation;
- cancellation at any point until confirmation;
- confirmation, revocation, audit display, and help content; and
- keyboard-operable controls, focus handling, dialogs, status announcements, and responsive styling within the verified states.

The minimum wait is not a deadline. Once it has elapsed, confirmation becomes available and cancellation remains available until the user chooses an action.

## Flask gateway

`core/backend/app.py` provides session, records, providers, grant, confirmation, cancellation, revocation, access-check, audit, status, and educational explorer endpoints.

For a local-EVM session, all of the following must be valid:

- `WEB3_PROVIDER_URI`;
- `CONTRACT_ADDRESS`;
- `CONTRACT_ABI_PATH`; and
- the development private key used by the gateway.

If a usable contract binding is not created, state-changing calls use the explicitly labelled in-memory fallback. RPC reachability by itself is not proof that the contract binding succeeded.

The gateway rejects state-changing grant requests unless `record_ids` is a list containing exactly one identifier. When `expiration_days` is omitted or `0`, the grant has no expiry.

## Contract

`experiments/hardhat/contracts/HealthAccessControl.sol` registers application-supplied 32-byte identifiers and implements:

- `registerRecord`;
- `initiateGrant`;
- `confirmGrant`;
- `cancelPendingGrant`;
- `revokeAccess`;
- `checkAccess`;
- `getAuditLog`;
- authorized `logAccessAttempt`;
- gateway administration;
- pause/unpause policy; and
- ownership transfer.

The owner/reference patient address controls the modeled consent lifecycle. The backend signs local development transactions using a Hardhat account; there is no user-controlled wallet integration.

Contract events and audit-array entries provide local consent-state evidence. They do not make the whole system immutable, verify clinical-record integrity, prove provider identity, or establish legal compliance.

## Data boundary

The repository contains no clinical files, IPFS client, production metadata repository, or clinical-record hashing pipeline. It creates deterministic seeded identifiers for demonstration records. Therefore:

- the on-chain values must be called seeded record identifiers, not clinical-record hashes;
- no IPFS or encrypted off-chain storage is implemented;
- the prototype does not prove integrity of external medical data; and
- legal status and privacy consequences of production hashes/metadata require separate engineering and review.

The educational `blockchain_engine.py` is a local teaching/fallback component using SHA-256, a simplified proof-of-work chain, Merkle trees, and illustrative gas estimates. Its gas estimate is not EVM contract evidence.

## Evidence boundary

The expert-assessed Cycle 1 build was not archived. Cycle 2 contract/browser evidence corresponds to commit `360eaa2a26b2f2b4fef98c0667f87db09e5e5120` and the retained 15 July 2026 artifacts. A 19 July text-only working-tree correction aligns the review-screen duration with the API's no-expiry default and is not attributed to the 15 July Axe reports.

Authoritative technical evidence is under `results/`:

- 28 passing Hardhat tests and final-contract gas measurements;
- Slither 0.11.5 JSON and scope-aware summary;
- separate initial-state Lighthouse/axe reports; and
- twelve final standalone axe-core state reports plus screenshots.

These results do not establish WCAG conformance, accessibility effectiveness for disabled users, production security, or independent assurance.

## Not implemented / future architecture

Production-oriented future work includes accessible user-controlled wallet and identity flows, real WebAuthn/FIDO2 or equivalent authentication, durable encrypted clinical storage, deployment governance, representative-access safeguards, monitoring, rate limiting, TLS, key custody, independent audit, fuzzing, adversarial/failure-injection tests, live assistive-technology evaluation, and co-designed studies with disabled participants.
