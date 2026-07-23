# BCHAIN-ACCESS Reference Prototype

Accessibility-oriented blockchain healthcare consent interface research artifact.

**Status:** Research prototype; not for clinical or production use  
**Licenses:** MIT (code), CC BY 4.0 (data)  
**Cycle 2 code/evidence commit:** `360eaa2a26b2f2b4fef98c0667f87db09e5e5120`  
**Historical Zenodo release:** [10.5281/zenodo.21345578](https://doi.org/10.5281/zenodo.21345578)

The 13 July 2026 Zenodo release predates the final 15 July evidence package and must not be described as its archive. A new deposit is still required. The current working tree also contains a 19 July text-only consistency correction to the review-screen expiry label; that change is not historical expert-study evidence.

## Scope

The prototype demonstrates a reference patient address controlling consent for seeded record identifiers through:

- a single-page HTML/CSS/JavaScript interface;
- a Flask REST gateway;
- `HealthAccessControl.sol` on a local Hardhat EVM; and
- an explicitly labelled in-memory Python fallback when the EVM contract is unavailable.

It implements grant initiation, a 60-second minimum wait before confirmation, cancellation, confirmation, revocation, access checking, and contract audit entries/events. The wait is not a completion deadline: cancellation remains available until confirmation.

It does **not** contain clinical records, an IPFS repository, production record encryption, a user-controlled wallet, real biometric authentication, a production identity system, or a security/compliance guarantee. Seeded 32-byte identifiers are registered in the demonstration; they are not hashes derived from clinical files.

The retained accessibility evidence is state- and tool-specific. Twelve final standalone axe-core reports recorded zero violations, while five contained incomplete items retained for manual review. This does not establish WCAG 2.2 conformance or accessibility effectiveness for disabled users.

## Repository layout

```text
core/
  backend/                    Flask gateway and educational fallback engine
  frontend/index.html         Cycle 2 reference interface
  integration/                legacy optional adapter; not loaded by Cycle 2 UI
experiments/
  hardhat/contracts/          HealthAccessControl.sol
  hardhat/test/               28-test Hardhat suite
  scripts/                    reproduction and descriptive-analysis helpers
paper/
  main_revised.tex
  supplementary_revised.tex
  ref_revised.bib
  IEEEtran.cls
results/                      retained gas, Slither, browser, and test evidence
output/pdf/                   compiled manuscript and supplement
```

## Quick start

Prerequisites: Python 3.10+, Node.js 18+, and npm.

### Backend fallback mode

```powershell
cd core/backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

The API listens on `http://localhost:5000`. Serve the frontend separately:

```powershell
cd core/frontend
python -m http.server 3000
```

Open `http://localhost:3000`. The current interface already calls the Flask API directly. Do not add `core/integration/frontend_integration.js`; it is a legacy adapter and is not part of the verified Cycle 2 interface.

### Local EVM mode

Install and test the contract:

```powershell
cd experiments/hardhat
npm install
npm test
```

For gas output:

```powershell
$env:REPORT_GAS='true'
npm test
```

To connect Flask to a deployed local contract, copy `.env.example` to `.env` and ensure `WEB3_PROVIDER_URI`, `CONTRACT_ADDRESS`, and `CONTRACT_ABI_PATH` point to the running node, deployed address, and generated Hardhat artifact. RPC reachability alone does not prove that the configured contract binding succeeded; check backend startup output before treating the status as local-EVM evidence.

## Key API behavior

- `POST /api/auth/unlock` simulates entry and creates a 15-minute session.
- `GET /api/records` returns three seeded demonstration records.
- `POST /api/access/grant` requires exactly one `record_ids` entry for a state-changing request.
- The grant response states that confirmation becomes available after 60 seconds and cancellation remains available until confirmation.
- Omitting `expiration_days` means no expiry (`0`). The Cycle 2 interface now labels this accurately.
- `POST /api/access/confirm`, `/cancel`, and `/revoke` operate on the reference consent lifecycle.
- `GET /api/audit/log` returns the available contract or fallback audit entries.
- `GET /api/blockchain/verify` checks the educational fallback chain's internal structure; it does not verify clinical-data integrity.

The educational engine's printed gas estimate is illustrative and is not the contract gas evidence. Authoritative final-contract measurements are in `results/gas-report.txt` and Supplementary S1.

## Reproduction and evidence

See [REPRODUCE.md](REPRODUCE.md) for exact commands and [ARTIFACT_MANIFEST.md](ARTIFACT_MANIFEST.md) for authoritative filenames. Important retained results are:

- 28 passing Hardhat tests;
- final-contract deployment gas of 2,934,432 and method values in `results/gas-report.txt`;
- Slither 0.11.5 output in `results/slither-report.json` and its scope-aware summary;
- twelve final axe-core state reports and screenshots under `results/wcag/final-state-verification/`; and
- initial-state Lighthouse and standalone axe reports kept separate from state-by-state evidence.

The expert-study build was not preserved. Historical expert findings must not be presented as observations of the corrected Cycle 2 code.

## Research limitations

Before production use, the system requires disabled-participant and live assistive-technology evaluation, real accessible authentication and wallet integration, independent smart-contract audit, property-based fuzzing, adversarial and failure-injection testing, production key/identity management, durable encrypted off-chain storage, governance, and jurisdiction-specific legal review.
