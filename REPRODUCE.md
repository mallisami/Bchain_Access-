# Reproducibility Guide (REPRODUCE.md)

This repository contains the code, de-identified data summaries, and configuration used for the paper **"BCHAIN-ACCESS: A Standards-Informed Framework for Accessible Blockchain Healthcare Consent Interfaces"**.

The corrected post-evaluation code and retained engineering evidence correspond to commit `360eaa2a26b2f2b4fef98c0667f87db09e5e5120`. This commit is distinct from the unpreserved historical expert-session build.

To make reproducing the results easy, helper scripts have been provided under the `experiments/scripts/` directory.

### Quick Commands for Reproduction
- **Windows Setup & Run:**
  ```cmd
  call experiments\scripts\setup.bat
  call experiments\scripts\run_reproduction.bat
  ```
- **Linux/macOS Setup & Run:**
  ```bash
  chmod +x experiments/scripts/*.sh
  ./experiments/scripts/setup.sh
  ./experiments/scripts/run_reproduction.sh
  ```

---

## 1. Expert Study Evaluation

The surviving package does not preserve the evaluated commit/tag, exact session dates, per-session backend mode, archived deployment URL, or complete evaluator browser/OS/assistive-technology matrix. E10 comments mention NVDA without a version. The quantitative summaries can be recomputed, but the original manual sessions cannot be exactly reconstructed from the deposited metadata.

All de-identified evaluator responses (E1–E10) are located under the `data/` directory.

### Setup
Ensure you have Python 3.8+ installed. No external packages are required to run the reproduction script (pure standard library).

### Execution
Run the following command from the root directory to reproduce the SUS, expert task-based walkthrough, questionnaire, and coarse heuristic summaries:
```bash
python experiments/scripts/compute_results.py
```

This script outputs:
* **System Usability Scale (SUS)**: mean 87.50, participant-level SD 5.27, 95% t interval [83.73, 91.27].
* **Expert task workbook**: overall recorded active-interaction mean 9.69 seconds; T6 excludes the fixed 60-second system wait. The workbook summary reports 80/80 completions, but the deposited CSV has no row-level completion field, so this outcome is disclosed and excluded from principal results.
* **Accessibility questionnaire**: true raw mean 4.44/5 and participant-level SD 0.36.
* **Heuristic inspection**: coarse source mean 0.10. The undocumented post-hoc finer re-rating is printed for provenance but excluded from principal results.

---

## 2. Smart Contract & Blockchain Backend

The smart contract backend `HealthAccessControl.sol` is located under `experiments/hardhat/contracts/`.

### Setup
Ensure you have [Node.js](https://nodejs.org/) installed, then install the hardhat dependencies:
```bash
cd experiments/hardhat
npm install
```

The repository pins `solc` 0.8.26 in `package.json`; Hardhat resolves that local compiler build.

### Run Tests and Gas Reports
To compile the Solidity contract and run the final 28-test suite covering the lifecycle, access guards, state and security invariants, authorized logging, gateway administration, and pause policy:
```bash
npx hardhat test
```
*Note: A convenience test script is also provided at `experiments/scripts/run_tests.bat` (Windows) and `experiments/scripts/run_tests.sh` (Linux/macOS) which outputs the test logs into `results/hardhat-test-output.txt`.*

To run a new gas report from the current suite:
```bash
# On Linux/macOS
REPORT_GAS=true npx hardhat test

# On Windows (cmd)
set REPORT_GAS=true&& npx hardhat test
```
The output gas consumption table will be displayed in the console. The retained `results/gas-report.txt` and Supplementary S1 values were regenerated on 15 July 2026 from the final corrected contract using the complete 28-test workload; all 28 tests passed during the reporting run.

### Run Static Analysis (Slither)
The final corrected contract was scanned with Slither 0.11.5 on 2026-07-15. To reproduce the scan:
```bash
# Install Slither (requires python & solc)
pip install slither-analyzer

# Run analyzer
cd experiments/hardhat
slither . --json ../../results/slither-report.json
```
The final raw output is deposited at `results/slither-report.json`, with a scope-aware summary at `results/slither-summary.txt`. It contains six low-severity `timestamp` findings associated with expiry/minimum-wait comparisons and 35 informational naming-convention findings; it contains no high- or medium-severity detector output. Static analysis does not replace fuzzing, dynamic adversarial analysis, or independent audit.

---

## 3. UI Prototype & Accessibility Claims

* The UI source code evaluated by the experts is located under the `core/frontend/` directory.
* Fresh initial-state scans are in `results/wcag/lighthouse_report_2026-07-15.json` (Lighthouse 13.4.0, 100/100 accessibility composite; embedded axe-core 4.12.1) and `results/wcag/axe_report_2026-07-15.json` (standalone axe-core 4.12.1, zero violations). These reports cover only the rendered initial page.
* Final standalone state reports are under `results/wcag/final-state-verification/`. All twelve JSON files record axe-core 4.10.0 and zero violations; five contain incomplete items retained for manual review. Matching screenshots are under `results/wcag/final-state-verification/screenshots/`.
* Lighthouse and standalone axe results are separate runs and must not be merged. Neither the initial-state nor twelve-state automated result establishes whole-artifact WCAG conformance or replaces live assistive-technology and disabled-participant evaluation.
* Earlier Lighthouse, WAVE, and Axe artifacts remain in `results/wcag/` for provenance, but their relationship to the unpreserved expert-session build is not established. The 12 July Lighthouse JSON is a baseline repository scan, not verified historical-session evidence.
* The color contrast coverage matrix of the 29 contrast pairs is located in `results/wcag/contrast_check.csv`.
