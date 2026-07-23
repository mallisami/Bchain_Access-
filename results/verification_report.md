# BCHAIN-ACCESS Final Post-Remediation Engineering Verification Report

**Document type:** Researcher-led engineering verification report  
**Artifact:** BCHAIN-ACCESS healthcare blockchain access-control reference prototype  
**Verification date:** 15 July 2026  
**Corrected code/evidence commit:** `360eaa2a26b2f2b4fef98c0667f87db09e5e5120`  
**Historical archive:** Zenodo v1.0.0, published 13 July 2026, predates this verification and is not the archive of this corrected build

## Evidence boundary

This report records frontend, backend, and smart-contract engineering checks performed on the corrected post-evaluation reference artifact. It does not alter the historical expert-study results.

The listed accessibility and security remediations were verified within the recorded browser, automated-tool, contract-test, and static-analysis scope. The evidence does not establish whole-artifact WCAG conformance, accessibility effectiveness for disabled users, production security, legal compliance, or independent assurance.

The verification was researcher-led. It was not an independent audit. Live NVDA, JAWS, VoiceOver, alternative-input, disabled-participant, property-based fuzzing, dynamic adversarial, multi-node, and independent smart-contract audit activities were not performed.

## 1. Frontend Accessibility Remediation and WCAG 2.2-Oriented Verification

The corrected frontend was remediated against selected WCAG 2.2 Level A and AA criteria and technically verified across 12 enumerated interface states.

The final remediation includes:

- programmatic focus movement after authentication and between wizard states;
- accessible audit and revocation dialogs with programmatic names, focus containment, Escape handling, and trigger-focus restoration;
- visible and programmatically announced record-loading, audit-loading, and transaction-error presentations;
- minimum 24-by-24-CSS-pixel dimensions for the affected checkbox and compact-link targets;
- narrow-viewport placement of the blockchain-status panel in normal document flow; and
- retained live-region messaging for workflow transitions, confirmation availability, success, and errors.

### 1.1 Automated-tool versions are reported separately

- **Standalone state-by-state axe:** axe-core 4.10.0, as recorded in each final per-state JSON file.
- **Lighthouse corrected-initial-state report:** Lighthouse 13.4.0, 100/100 accessibility composite, 23 passed binary audits, 0 failed, 43 not applicable, and 10 requiring manual verification. Its environment records embedded axe-core 4.12.1.
- **Intermediate live dialog inspection:** axe-core 4.8.2 reported one moderate `region` finding before the final dialog remediation. It is retained as intermediate evidence and is not combined with the final state reports.

The standalone axe and Lighthouse results are different runs with different scopes and are not aggregated.

### 1.2 Final state-by-state evidence matrix

| State | Interface state | WCAG-oriented focus | Axe JSON | Screenshot | Standalone axe result | Recorded manual/browser result | Evidence boundary |
|---|---|---|---|---|---|---|---|
| A1 | Landing | Keyboard entry, focus visibility | `A1_landing_axe.json` | `A1_landing.png` | 0 violations; 0 incomplete | Keyboard entry and visible focus inspected | No live screen-reader confirmation |
| A2 | Dashboard | Focus order, status messages | `A2_dashboard_axe.json` | `A2_dashboard.png` | 0 violations; 0 incomplete | Dashboard-heading focus inspected after authentication | Corrected build only |
| A3 | Record selection | Keyboard, names, target size | `A3_record-selection_axe.json` | `A3_record-selection.png` | 0 violations; 0 incomplete | Provider selection, single-record choice, contextual names, and affected target dimensions inspected | No alternative-input test |
| A4 | Review | Focus order, labels and instructions | `A4_review_axe.json` | `A4_review.png` | 0 violations; 0 incomplete | Wizard-transition focus and keyboard controls inspected | Comprehension effectiveness not evaluated |
| A5 | Countdown | SC 2.4.3 Focus Order; SC 4.1.3 Status Messages | `A5_countdown_axe.json` | `A5_countdown.png` | 0 violations; 1 incomplete | Countdown state, confirmation availability, and focus behavior inspected | The minimum wait is not classified as an SC 2.2.1 pass or failure; delay acceptability remains unresolved |
| A6 | Confirmation success | Focus order, status messages | `A6_confirmation-success_axe.json` | `A6_confirmation-success.png` | 0 violations; 0 incomplete | Success focus and visible/programmatic status inspected | No live assistive-technology announcement confirmation |
| A7 | Audit dialog open | Keyboard, focus order, name/role/value | `A7_audit-dialog-open_axe.json` | `A7_audit-dialog-open.png` | 0 violations; 1 incomplete | Dialog name, focus containment, Escape handling, and focus restoration inspected | Manual browser result; no live screen reader |
| A8 | Revocation dialog open | Keyboard, focus order, name/role/value | `A8_revocation-dialog-open_axe.json` | `A8_revocation-dialog-open.png` | 0 violations; 1 incomplete | Focus containment, Escape handling, cancellation, and restoration inspected | No live screen reader |
| A9 | Expanded FAQ | Keyboard, state, target size | `A9_expanded-faq_axe.json` | `A9_expanded-faq.png` | 0 violations; 1 incomplete | Accordion keyboard states and affected targets inspected | Content comprehension not evaluated |
| A10 | Record-loading failure | Error identification, status message | `A10_record-loading-failure_axe.json` | `A10_record-loading-failure.png` | 0 violations; 0 incomplete | Verification harness invoked the implemented visible alert and programmatic announcement presentation | Presentation check, not dynamic RPC failure injection |
| A11 | Audit-loading failure | Error identification, dialog status | `A11_audit-loading-failure_axe.json` | `A11_audit-loading-failure.png` | 0 violations; 1 incomplete | Verification harness invoked the implemented audit-dialog error and focus presentation | Presentation check, not dynamic RPC failure injection |
| A12 | Transaction failure | Error identification, status message | `A12_transaction-failure_axe.json` | `A12_transaction-failure.png` | 0 violations; 0 incomplete | Verification harness invoked the implemented visible alert and programmatic announcement presentation | Presentation check, not adversarial transaction testing |

All twelve retained standalone axe reports recorded zero violations. Five reports contain tool-marked incomplete items that require manual review and are not represented as passes.

### 1.3 Countdown criterion

The 60-second mechanism is a minimum wait before confirmation, not a deadline requiring the user to finish within a time limit. State A5 is therefore recorded under SC 2.4.3 Focus Order and SC 4.1.3 Status Messages. SC 2.2.1 is not applied to the countdown because no post-wait completion deadline exists. Timing-related acceptability remains a target-user research question.

### 1.4 Accessibility conclusion

The corrected interface added the listed focus, dialog, target-size, responsive-layout, and error-presentation remediations. The final standalone axe-core reports recorded zero violations across the 12 tested corrected states; five reports contained incomplete items retained for manual review. The recorded manual browser checks passed within their stated scope. These results do not constitute whole-product WCAG conformance or live assistive-technology validation.

## 2. Smart-Contract and Backend Remediation

The corrected contract and Flask gateway implement the following changes:

- access-attempt logging is restricted to the owner or configured authorized gateway;
- the owner controls gateway administration, and a zero-address gateway is rejected;
- grant initiation and confirmation are blocked while the contract is paused;
- patient cancellation and revocation remain available while paused;
- normal operation resumes after unpausing; and
- state-changing Flask endpoints reject a request before transaction submission unless exactly one record identifier is supplied.

The pause change verifies the documented operational policy by preventing new grant initiation and confirmation during an administrative pause. It is not presented as proof of front-running prevention. Single-record enforcement mitigates the previously identified partial multi-record commit condition; atomic batching was not implemented.

### 2.1 Final Hardhat result

The final Hardhat suite contained 28 tests, all of which passed.

The retained output covers:

- lifecycle and access guards;
- repeated confirmation and expired-access behavior;
- zero-address provider rejection;
- pending-grant revocation rejection and re-initiation after revocation;
- owner and authorized-gateway audit logging;
- rejection of unauthorized audit logging;
- owner-controlled gateway administration and zero-address rejection;
- owner and non-owner pause administration;
- blocked grant initiation and confirmation while paused;
- continued cancellation and revocation while paused; and
- operation after unpausing.

The single-record API boundary was verified separately from the Hardhat contract suite. It is not counted as a Hardhat test.

### 2.2 Gas evidence

The gas report was regenerated on 15 July 2026 from the final corrected contract at code/evidence commit `360eaa2a26b2f2b4fef98c0667f87db09e5e5120`, using the complete 28-test workload. All 28 tests passed during the gas-reporting run. The retained `results/gas-report.txt` records deployment gas of 2,934,432 and the transaction-method values reproduced in Supplementary S1; these local-development figures do not predict production-network fees.

### 2.3 Final Slither result

Slither 0.11.5 completed successfully against the final corrected contract. The retained JSON contains:

- 0 high-severity detector findings;
- 0 medium-severity detector findings;
- 6 low-severity timestamp-dependency findings associated with the intended confirmation-delay and expiration logic; and
- 35 informational naming-convention findings.

No high- or medium-severity Slither detector findings were reported. This wording does not claim that no vulnerabilities exist. Static analysis does not replace property-based fuzzing, dynamic adversarial testing, multi-node evaluation, or independent audit.

## 3. Security and Accessibility Verification Matrix

| Area | Corrected control | Verification evidence | Result | Residual boundary |
|---|---|---|---|---|
| Workflow status | Programmatic heading focus and concise transition announcements | A2, A4-A6 browser states and source inspection | Remediated and technically verified | Live screen-reader confirmation outstanding |
| Error handling | Visible and programmatically announced record, audit, and transaction errors | A10-A12 state reports and screenshots | Remediated and technically verified | Presentation checks were not dynamic RPC-loss injection |
| Dynamic updates | Live regions, confirmation availability, success messaging, transition focus | A2, A4-A6 and source inspection | Remediated and technically verified | Assistive-technology compatibility unconfirmed |
| Keyboard and target size | Principal workflow, two dialogs, focus restoration, affected 24-by-24 targets | Manual browser checks, A3, A7-A9 screenshots | Remediated and technically verified | Alternative-input testing not performed |
| Responsive layout | Status panel moves into normal flow at narrow widths | 320-CSS-pixel browser inspection | Remediated and technically verified in tested layout | Not exhaustive device coverage |
| Audit logging | Owner or authorized gateway required | Final Hardhat output | Remediated and contract-tested | Production gateway identity and key governance remain |
| Pause policy | Initiation and confirmation blocked; cancellation and revocation retained | Final Hardhat output | Remediated and contract-tested | Incident-response governance not evaluated |
| Multi-record consistency | API rejects state-changing requests unless exactly one record is supplied | Flask source and API-boundary inspection | Mitigated and API-verified | No atomic batch transaction implemented |

## 4. Retained Evidence Inventory

The final package is expected to contain:

- twelve standalone axe-core 4.10.0 JSON files under `results/wcag/final-state-verification/`;
- twelve matching screenshots under `results/wcag/final-state-verification/screenshots/`;
- `results/hardhat-test-output.txt`, showing 28 passing tests and no failures;
- `results/slither-report.json`;
- `results/slither-summary.txt`;
- `results/gas-report.txt`, regenerated against the final corrected contract with the complete 28-test workload;
- the retained Lighthouse JSON, including Lighthouse 13.4.0 and embedded axe-core 4.12.1 metadata;
- the accessibility and security matrices in this report and the manuscript supplement;
- final source code;
- `.env.example`;
- updated `README.md` and `REPRODUCE.md`;
- `ARTIFACT_MANIFEST.md`;
- this final verification report; and
- corrected Cycle 2 code/evidence commit `360eaa2a26b2f2b4fef98c0667f87db09e5e5120`; and
- a 19 July 2026 text-only working-tree correction aligning the review-screen duration with the API's no-expiry default. This later edit is not attributed to the 15 July Axe reports.

## 5. Residual Limitations and Future Work

Further accessibility research should conduct reproducible live testing with NVDA and VoiceOver, alternative-input technologies, and disabled participants, including evaluation of announcement quality, comprehension, independence, and the acceptability of the mandatory confirmation delay.

Further engineering work should add property-based fuzzing, dynamic failure-injection and adversarial tests, multi-node permissioned-network evaluation, production identity and key management, durable encrypted off-chain storage, dependency maintenance, and independent smart-contract audit before any production use.

## 6. Final Engineering Conclusion

A final post-remediation engineering cycle corrected selected identified interface, contract, and backend issues and verified the corrected artifact across 12 enumerated interface states, a 28-test Hardhat suite, and Slither static analysis. The corrected build added accessible dialog behavior, programmatic workflow focus, user-visible error states, corrected interactive targets, authorized audit logging, a safety-preserving pause policy, and single-record state-change enforcement. The final standalone axe-core reports recorded zero violations across the 12 tested corrected states; five reports contained incomplete items retained for manual review. All 28 contract tests passed.

These results strengthen the technical feasibility evidence but do not establish whole-artifact WCAG conformance, accessibility effectiveness for disabled users, production security, or independent assurance.
