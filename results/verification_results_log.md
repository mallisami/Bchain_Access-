# Verification Results — 2026-07-15

This cumulative record preserves chronological verification checkpoints. Earlier gas figures and 16/12-page PDF counts below describe superseded intermediate states and must not be cited as final-package results. The authoritative final summary is the 15 July post-remediation section at the end of this file; final PDFs contain 18 main-paper pages and 15 supplementary pages.

## Historical 14 July smart-contract run (superseded for final-contract gas evidence)

The following 13-test measurements are retained only as the 14 July baseline. Final-contract gas evidence was regenerated on 15 July with the complete 28-test workload and is deposited at `results/gas-report.txt`.

- Solidity compiler: 0.8.26 (exactly and locally pinned)
- Optimizer: enabled, 200 runs; EVM target: Paris
- Hardhat tests: 13 passing
- Deployment: 2,816,201 gas (9.4% of the 30,000,000-gas test block limit)
- `registerRecord`: 341,845 average gas (13 calls)
- `initiateGrant`: 351,075–371,023 gas, 356,062 average (8 calls)
- `confirmGrant`: 198,723 average gas (4 calls)
- `cancelPendingGrant`: 213,319 average gas (4 calls)
- `revokeAccess`: 171,917 average gas (2 calls)
- `transferOwnership`: 28,600 average gas (2 calls)

The suite includes rejection of unsupported access levels, a regression test proving that a cancelled pending grant cannot subsequently be confirmed, and ownership-transfer event and zero-address tests.

## Fresh backend-to-contract lifecycle

A local Hardhat node and Flask backend were run against a newly deployed contract. The verified lifecycle was:

1. initiate a view-only grant;
2. retain the pending state through the 60-second minimum wait;
3. confirm successfully after the wait;
4. verify active access;
5. revoke successfully; and
6. verify that access is no longer active.

Final-bytecode deployment address: `0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6`.

The final rerun additionally verified four on-chain audit actions for the tested record (`RECORD_REGISTERED`, `GRANT_INITIATED`, `GRANT_CONFIRMED`, and `REVOKE`) and an on-chain access result of false after revocation. The backend now fails closed when a connected EVM transaction is rejected and preserves separate EVM and educational-ledger hashes; API grant/cancel hashes were checked against the corresponding real transaction hashes.

## Fresh expert-data reproduction

`experiments/scripts/compute_results.py` reproduced:

- SUS mean 87.50, participant SD 5.27, 95% t interval [83.73, 91.27];
- expert task-workbook active-interaction mean 9.69 seconds; the workbook's 80/80 completion summary is not reconstructible from the row-level CSV and is excluded from principal results;
- accessibility-questionnaire raw mean 4.44/5 and participant SD 0.36; and
- coarse heuristic mean 0.10.

The undocumented post-hoc heuristic re-rating is excluded from principal results.

## Fresh static and browser audits

- Slither 0.11.5 analyzed the final corrected contract with 101 detectors. The saved report contains six low-severity `timestamp` results intrinsic to the documented time-lock/expiry design, 35 informational naming-convention results, and no high- or medium-severity results.
- Lighthouse 13.4.0 scanned the initial rendered page in Headless Chrome 150 and scored accessibility 100/100 with 23 passed binary audits, 0 failed, 43 not applicable, and 10 manual checks.
- axe-core 4.12.1 independently scanned the same initial page and reported zero violations and zero incomplete results.
- These automated browser scans cover only the initial rendered state. They neither establish WCAG conformance nor replace keyboard, assistive-technology, and complete-process manual testing.

## Remaining limitations and other findings

- The historical WAVE report was not regenerated because WAVE does not provide an equivalent local CLI audit in this workflow.
- After non-breaking npm remediation, the development-tool dependency tree still reports 39 advisories (18 low, 17 moderate, 4 high, 0 critical). The remaining automatic remedy requires breaking toolchain upgrades and must be handled as a tested Hardhat migration rather than a forced lockfile rewrite. The application frontend does not ship this development dependency tree.
- Multi-record REST grants submit sequential contract writes rather than an atomic batch; a later-record failure can leave earlier records committed on-chain. The API now fails closed for the failing operation, but production work still needs an atomic batch design or tested compensation protocol.
- `logAccessAttempt` retains the caller address and corrects false success claims, but it is not restricted to an authenticated production gateway and remains susceptible to spam/misleading attempts.
- A portable Tectonic 0.16.9 engine compiled the final evidence-aware main manuscript (16 pages) and supplement (12 pages). The main and supplementary logs contain no duplicate PDF destinations, undefined references/citations, oversized-float warnings, or overfull boxes. Rendered inspection confirmed that the numbered tables appear in reading order and that the revised full-width and landscape tables remain within the page bounds. Final PDFs are stored under `output/pdf/`.

## Mandatory manuscript-correction audit

The final float-and-audit pass loads `hyperref` last, adds a float barrier before the SUS subsection, and replaces the SUS `[H]` placement with `[!t]`. Table III now explicitly presents only three illustrative access-need clusters and is full-width. Direct parsing of both deposited Lighthouse JSON files found the same accessibility breakdown (23 passed, 0 failed, 43 not applicable, 10 manual; Chrome 150); neither supports the conflicting 23/1/36/13 summary. The manuscript separates the 12 July baseline repository scan from the 14 July post-remediation initial-state scan and does not identify either as the historical expert-session build. The former Figure 8 was removed because its embedded WCAG 2.1 compliance statements exceeded the evidence.

The B2/SC~2.2.1 correction pass verifies from the contract and frontend that the 60-second mechanism is a minimum wait before consent confirmation, not an authentication timer or user-completion deadline. The manuscript now records real timed authentication as not assessed, maps the minimum wait to B9/CID, and treats the duration as an empirically unresolved usability-design choice rather than an SC~2.2.1 failure. The main-paper risk-to-evidence traceability matrix is full-width, the complete criterion-level inspection matrix is in Supplementary~S5, the implementation-scope detail is in Supplementary~S9, and the automated-audit table reports tool-native results rather than misleading passed/failed columns.

The latest targeted correction pass consistently characterizes the baseline work as a documentation-based evidence review, describes the framework as security-aware guidance with a three-stage evidence-review process, and limits the mixed-methods findings to exploratory feasibility. The PTD mapping now treats WCAG 2.2 SC 3.1.3 and 3.1.5 as Level AAA/advisory, and the traceability table distinguishes implemented responses from implementation status and design recommendations.

The manuscript records documented consent through WhatsApp, pseudonymization under identifiers E1--E10, aggregate reporting, and private retention of identifying consent records. Limitation L9 separately records that no formal institutional ethics-committee approval, exemption, or determination that review was unnecessary was obtained. Limitation L10 records that the historical evaluated commits and environment metadata were not preserved and that the corrected repository is a post-evaluation remediation artifact, not the exact build assessed by the ten experts.

The final source removes numerical baseline-document severity estimates, legal-adequacy overstatements, stale VC terminology, algorithmic gate/certification language, unsupported agreement/generalization claims, automated-table "Pass" labels, strong SUS interpretations, and fictional-scenario effectiveness claims. It adds categorical documentary evidence, credential-faithful evaluator prose, explicit missing assistive-technology metadata, evaluated-artifact provenance gaps, consistent WCAG mappings, and IEEE journal formatting. Because no approval or exemption record exists in the deposited package, the manuscript makes no verified institutional ethics-approval claim.

The final provenance-and-supplement pass removes the unsupported ``versioned'' label for the historical expert-session artifact, adds the Peffers DSRM process reference and adaptation, identifies Yaqub et al. as prior author work, and changes the title to ``Accessibility-Oriented.'' Task outcomes are now described as workbook-reported because the deposited files contain no timing telemetry, observer record, row-level completion/assistance field, restart rule, or incomplete-attempt log. Recruitment channel, evaluator-author relationships, disability status, expertise-label definitions, and credential verification are explicitly recorded as unavailable. Supplementary~S5 now contains separate rows for every WCAG~2.2 Level~A/AA criterion, excludes obsolete SC~4.1.1, and separates historical findings, later source remediation, and the 14 July initial-state scans. S7 now presents concise targeted narrative evidence-gathering notes and makes no systematic-review, exhaustive-coverage, or prevalence claim. Gas wording distinguishes off-chain `eth_call` from on-chain execution and limits gas determinism to identical EVM revision, bytecode, input, and storage state.

## Locked evidence-aware manuscript pass

The paper's locked title, abstract, index terms, Introduction opening, research gap, RQ1--RQ3, five contributions, novelty statement, evidence boundary, and organization paragraph were preserved. Sections IV--VII now use predicted accessibility-risk propositions, accessibility-oriented design principles, explicit risk-to-evidence traceability, a three-stage evidence-review procedure, and evidence dimensions ED1--ED5; legacy PB/ERQ and benchmark terminology was removed.

Sections VIII--IX now distinguish the reference artifact from the historical evaluated build, separate implemented behavior from unimplemented or simulated functions, and frame the expert work as exploratory issue identification and feasibility assessment. Detailed documentary heuristics, evaluator metadata, the coarse matrix, SUS calculations, questionnaire results, and hypothetical workflow mappings were moved to Supplementary~S8; implementation and reproducibility detail remains in S9.

Final source and deposited-PDF audits found no PB1--PB5 or ERQ1--ERQ5 labels, prohibited benchmark or validation claims, ``cognitive walkthrough'' wording, unsupported 100\% task-success claims, or ``documented informed consent'' wording. All 18 unique manuscript citation keys resolve, all labels and references resolve without duplication, and Supplementary~S5 contains 55 unique WCAG~2.2 Level~A/AA criterion rows. Both final PDFs were rendered page by page and visually inspected.

## Phase 5 discussion and conclusion revision

Section X is now ``Discussion, Limitations, and Future Work.'' It answers RQ1--RQ3 directly, distinguishes research and practice implications, consolidates the former validity and limitation material into ten ordered limitations, and replaces the speculative participant protocol with focused target-user and engineering research priorities. The prevalence sentence and the separate conceptual-contribution defence were removed.

Section XI now concludes with the framework's auditable risk--principle--response--criterion--evidence contribution rather than a chronological restatement of the study. Repeated evidence-boundary caveats were removed from the editable derivation, framework, scenario, and intermediate-result passages while the substantive boundary remains in the designated central locations.

The supplement retains ED1--ED5 terminology, S7 is titled ``Targeted Narrative Evidence-Gathering Notes,'' detailed evidence remains in S8--S9, and technical limitation references now point to consolidated Limitation L9. A future archival-release availability note was added, and the unused bibliography commands were removed so the compiled supplement has no empty References heading.

The Phase 5 sources compile to a 16-page main paper and 12-page supplement. The logs contain no LaTeX errors, undefined citations or references, duplicate destinations, overfull boxes, or oversized-float warnings. Text extraction confirmed the new Section X/XI headings and the absence of a supplementary References heading; all pages were rendered and visually inspected.

## Final title, abstract, index terms, and Introduction pass

The main and supplementary titles now identify BCHAIN-ACCESS as ``A Standards-Informed, Evidence-Aware Framework for Accessibility-Oriented Blockchain Healthcare Consent Interfaces.'' The abstract was replaced in full: it no longer reports the SUS score or enumerates the five-stage process, and it presents the problem, traceability framework, reference artifact, concrete findings, local-environment verification, and a single evidence boundary.

The index terms are now accessibility, blockchain, consent management, design science research, digital health, human--computer interaction, smart contracts, and WCAG~2.2. The Introduction now contains the revised problem opening, explicit traceability gap, RQ1--RQ3, five framework-centred contributions, the evidence-aware novelty statement, concise evidence boundary, and section-by-section organization paragraph. The remaining ``predicted barriers'' wording in related-work positioning was changed to ``predicted accessibility risks.''

Both revised sources compile successfully to a 16-page main paper and 12-page supplement. All citations, labels, and references resolve; the logs contain no duplicate destinations, overfull boxes, oversized floats, or LaTeX errors. PDF text extraction confirmed the exact new title, absence of 87.5 from the abstract, all five contribution headings, and the synchronized supplementary title. All pages were rendered and visually inspected, with detailed checks of the revised first two main-paper pages and supplementary title page.

## Final-submission terminology, sources, layout, and metadata pass

All remaining ``numbered WCAG checks'' and barrier--principle--feature terminology was replaced with criterion-level WCAG~2.2 and risk--principle--response--criterion--evidence terminology. Tables I and II, RQ3, the abstract, Introduction, novelty paragraph, and Section V cross-reference now use the requested wording. The abstract separates the three actionable accessibility issues from the confirmation-wait usability concern, uses ``demonstrate'' rather than ``establish,'' and describes BCHAIN-ACCESS as a framework developed through Design Science Research.

The Section VI blockchain perspective now states that the production consensus mechanism is deployment-specific rather than naming PBFT. Section VIII defines the supplied 256-bit contract identifier separately from the possible production pattern $H(\text{record data}\parallel\text{salt})$ and records that the reference artifact uses seeded 32-byte identifiers without clinical-record storage or a salt store.

The main reference list now includes and cites official primary sources for Regulation (EU) 2016/679, ETSI EN~301~549 V3.2.1, the U.S. Section~508 Refresh final rule, and the Health Insurance Portability and Accountability Act of 1996. All four official URLs returned HTTP~200 during verification. The main manuscript now resolves 21 unique citation keys with no missing bibliography entries.

The detailed automated-report table was moved from the main paper to Supplementary~S5.1, and the detailed task-workbook table was moved to S8.4. The main paper retains the qualitative-issues and evaluation-evidence-dimensions tables. Rendered page~12 is now fully occupied, page~13 contains one retained results table rather than three, and the evidence-dimensions table begins on page~14. The supplement remains 12 pages and the added tables are within page bounds.

Both PDFs now contain title, author, subject, keyword, language, and display-title metadata. The main PDF has 54 bookmarks and the supplement now has 21 hierarchical bookmarks. Poppler reports `Tagged: no`: the available Tectonic workflow uses LaTeX2e 2021-11-15 and does not provide the modern PDF-management/tagging path needed for reliable PDF/UA output; Pandoc is also unavailable for an HTML companion. This optional limitation is reported explicitly rather than representing either PDF as tagged.

The final-submission main and supplementary PDFs remain 16 and 12 pages. Their logs contain no LaTeX errors, undefined citations or references, duplicate destinations, overfull boxes, oversized floats, or PDF-string warnings. All pages were rendered and visually inspected.

## 15 July post-remediation engineering verification

The historical expert-study findings remain unchanged. A separately dated engineering-verification layer records the corrected post-evaluation artifact rather than presenting it as the build assessed by the experts. The manuscript and Supplementary S10 distinguish the 15 July initial-state browser scan from the 15 July final state-by-state and engineering checks.

The corrected code and retained raw engineering evidence were committed as `360eaa2a26b2f2b4fef98c0667f87db09e5e5120`. This post-evaluation commit is distinct from the unpreserved historical expert-session build.

- The contract's minimum confirmation wait and both application fallbacks are reconciled at 60 seconds.
- The final Hardhat suite contains 28 tests covering the lifecycle, access guards, state/security invariants, authorized logging, gateway administration, and pause policy. All 28 pass. The single-record API boundary was verified separately and is not counted as a Hardhat test.
- Slither 0.11.5 completed successfully against the final contract. `results/slither-report.json` records 41 detector results: six Low timestamp findings associated with the documented time-dependent consent design and 35 Informational naming-convention findings, with no High or Medium findings. The scope-aware summary is `results/slither-summary.txt`. This is static-analysis evidence, not an independent security audit.
- The post-remediation browser evidence remains scoped to the tested rendered states. The 15 July initial-state scan reported no axe violations, and an intermediate 15 July axe-core 4.8.2 dialog check reported one moderate `region` finding. After dialog remediation, twelve final standalone axe-core 4.10.0 state reports recorded zero violations; five contain incomplete items retained for manual review. Keyboard/focus, responsive-width, dialog, error-presentation, and target-size checks are recorded separately, and no live screen-reader session was performed.
- The gas report was regenerated on 15 July 2026 from the final corrected contract at commit `360eaa2a26b2f2b4fef98c0667f87db09e5e5120`, using the complete 28-test workload. All 28 tests passed during the reporting run; `results/gas-report.txt` retains the final-contract values.
- The existing Zenodo DOI resolves to the earlier v1.0.0 deposit published on 13 July 2026. It therefore does not archive the corrected 15 July working tree; a new committed, versioned release and archive deposit are still required for final artifact provenance.

After the final twelve-state evidence inventory was added, the editable sources compile to an 18-page main paper and a 15-page supplement. Both logs contain no LaTeX errors, undefined citations or references, duplicate destinations, overfull boxes, oversized floats, or fatal errors. Both PDFs carry title, author, subject, and keyword metadata; Poppler still reports `Tagged: no` under the available Tectonic workflow. Every page of both final PDFs was rendered and visually inspected.
