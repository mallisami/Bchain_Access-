# BCHAIN-ACCESS Final Artifact Manifest

**Verification date:** 15 July 2026; repository consistency audit 19 July 2026  
**Corrected code/evidence commit:** `360eaa2a26b2f2b4fef98c0667f87db09e5e5120`  
**Historical Zenodo release:** v1.0.0, published 13 July 2026; not the archive of this final corrected package

## Final verification evidence

- `results/hardhat-test-output.txt` - retained final test output showing 28 passing tests and no failures.
- `results/slither-report.json` - final Slither 0.11.5 JSON.
- `results/slither-summary.txt` - scope-aware Slither result summary.
- `results/gas-report.txt` - final-contract gas report regenerated with the complete 28-test workload.
- `results/wcag/lighthouse_report_2026-07-15.json` - Lighthouse 13.4.0 corrected-initial-state report; embedded axe-core 4.12.1.
- `results/wcag/axe_report_2026-07-15.json` - separate initial-state standalone axe-core 4.12.1 report.
- `results/wcag/final-state-verification/` - twelve final standalone axe-core 4.10.0 JSON reports.
- `results/wcag/final-state-verification/screenshots/` - twelve matching state screenshots.
- `results/verification_report.md` - final scope-bounded engineering verification report.

All twelve final standalone state reports record zero violations. Five contain tool-marked incomplete items retained for manual review. These results do not constitute whole-artifact WCAG conformance.

## Accessibility state files

All twelve Axe JSON files and screenshots listed below are located under `results/wcag/final-state-verification/` (and its `screenshots/` subdirectory):

| State | Axe JSON | Screenshot |
|---|---|---|
| A1 Landing | `A1_landing_axe.json` | `A1_landing.png` |
| A2 Dashboard | `A2_dashboard_axe.json` | `A2_dashboard.png` |
| A3 Record selection | `A3_record-selection_axe.json` | `A3_record-selection.png` |
| A4 Review | `A4_review_axe.json` | `A4_review.png` |
| A5 Countdown | `A5_countdown_axe.json` | `A5_countdown.png` |
| A6 Confirmation success | `A6_confirmation-success_axe.json` | `A6_confirmation-success.png` |
| A7 Audit dialog open | `A7_audit-dialog-open_axe.json` | `A7_audit-dialog-open.png` |
| A8 Revocation dialog open | `A8_revocation-dialog-open_axe.json` | `A8_revocation-dialog-open.png` |
| A9 Expanded FAQ | `A9_expanded-faq_axe.json` | `A9_expanded-faq.png` |
| A10 Record-loading failure | `A10_record-loading-failure_axe.json` | `A10_record-loading-failure.png` |
| A11 Audit-loading failure | `A11_audit-loading-failure_axe.json` | `A11_audit-loading-failure.png` |
| A12 Transaction failure | `A12_transaction-failure_axe.json` | `A12_transaction-failure.png` |

## Source and reproducibility files

- `core/frontend/index.html`
- `core/backend/app.py`
- `core/backend/blockchain_engine.py`
- `core/backend/config.py`
- `experiments/hardhat/contracts/HealthAccessControl.sol`
- `experiments/hardhat/test/HealthAccessControl.test.js`
- `experiments/hardhat/hardhat.config.cjs`
- `experiments/hardhat/package.json`
- `experiments/hardhat/package-lock.json`
- `core/integration/frontend_integration.js` - legacy optional adapter, not loaded by the Cycle 2 reference interface and excluded from its evidence claims.
- `experiments/scripts/setup.bat` / `setup.sh`
- `experiments/scripts/run_tests.bat` / `run_tests.sh`
- `experiments/scripts/run_reproduction.bat` / `run_reproduction.sh`
- `experiments/scripts/compute_results.py`
- `.env.example`
- `README.md`
- `REPRODUCE.md`

## Manuscript files

- `paper/main_revised.tex`
- `paper/supplementary_revised.tex`
- `paper/ref_revised.bib`
- `paper/IEEEtran.cls`
- `output/pdf/BCHAIN-ACCESS_main_revised.pdf`
- `output/pdf/BCHAIN-ACCESS_supplementary_revised.pdf`

The manuscript and verification report identify corrected Cycle 2 code/evidence commit `360eaa2a26b2f2b4fef98c0667f87db09e5e5120`. The current working tree additionally corrects the review-screen expiry label and analysis-script terminology on 19 July 2026; those edits are not historical expert-study evidence. The older Zenodo DOI must not be represented as the archive of these final files; a new release must deposit the final working tree together with the manuscript, supplement, report, and PDFs.
