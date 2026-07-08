# Reproducibility Guide (REPRODUCE.md)

This repository contains all code, data, and configuration files to reproduce the findings reported in the paper **"BCHAIN-ACCESS: An Accessibility-by-Design Framework Integrating Blockchain and HCI for Healthcare Interfaces"**.

The reproducibility is organized into three tracks:
1. **Expert Study Evaluation (SUS, Walkthrough, Questionnaire, Heuristics)**
2. **Smart Contract Verification (Hardhat Tests, Gas Reporting, Slither Audits)**
3. **UI Prototype & Accessibility Audits (WCAG Reports)**

---

## 1. Expert Study Evaluation

All de-identified evaluator responses (E1–E10) are located under the `data/` directory.

### Setup
Ensure you have Python 3.8+ installed. No external packages are required to run the reproduction script (pure standard library).

### Execution
Run the following command from the root directory to reproduce the statistical summaries (Table VII, Cognitive Walkthrough table, and Heuristic consensus metrics):
```bash
python analysis/compute_results.py
```

This script outputs:
* **System Usability Scale (SUS)**: Mean score (87.25), standard deviation (4.78), and 95% Confidence Intervals (`[83.83, 90.67]`) with Bangor et al. adjective mappings.
* **Cognitive Walkthrough**: Mean task completion times (overall mean: 9.69 seconds), success rates (100% success rate across all 80 tasks), and average difficulties.
* **Accessibility Questionnaire**: Overall mean rating (4.42/5 on Excel averaged-means; 4.44/5 true raw rating) and SD.
* **Heuristic Severity Re-Analysis**: Comparison of the original coarse 0/1 consensus model (Mean 0.10) against a finer-grained re-rating model (Mean 0.30, SD 0.5025) derived from qualitative evaluator comments, demonstrating non-zero variance.

---

## 2. Smart Contract & Blockchain Backend

The smart contract backend `HealthAccessControl.sol` is located under `smart_contracts/contracts/`.

### Setup
Ensure you have [Node.js](https://nodejs.org/) installed, then install the hardhat dependencies:
```bash
cd smart_contracts
npm install
```

### Run Tests and Gas Reports
To compile the Solidity contract and run the integration test suite (covering the `grant -> time-lock -> confirm -> revoke` lifecycle, the `cancel` path, and access guards):
```bash
npx hardhat test
```

To run tests with the EVM gas consumption report enabled (matching Supplementary S1):
```bash
# On Linux/macOS
REPORT_GAS=true npx hardhat test

# On Windows (cmd)
set REPORT_GAS=true&& npx hardhat test
```
The output gas consumption table will be displayed in the console and is mirrored in `smart_contracts/test/gas-report.txt`.

### Run Static Analysis (Slither)
To perform static analysis using Slither (reproducing Section S6 in supplementary):
```bash
# Install Slither (requires python & solc)
pip install slither-analyzer

# Run analyzer
slither .
```
Slither results are recorded in the supplementary manuscript and the full raw output is deposited at `analysis/slither_report.json`.

---

## 3. UI Prototype & Accessibility Claims

* The UI source code evaluated by the experts is located under the `frontend/` directory.
* Lighthouse, WAVE, and Axe DevTools automated accessibility reports backing the accessibility claims are available in the `analysis/wcag/` folder.
* The color contrast coverage matrix of the 29 contrast pairs is located in `analysis/wcag/contrast_check.csv`.
