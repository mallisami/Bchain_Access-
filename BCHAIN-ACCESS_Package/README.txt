BCHAIN-ACCESS - Complete Figure Package
=======================================

WHAT'S INSIDE
  images/            Figure_1..Figure_7, each as .png .pdf .svg .pptx
  Sami_v22.tex       Your manuscript, PROOFED + renumbered (see EDITS_SUMMARY.txt)
                     to match reading order (see "TEX CHANGES" below).
  ref.bib            Your bibliography (unchanged content; named ref.bib
                     to match \bibliography{ref} in the paper).
  BCHAIN-ACCESS_All_Figures.pptx
                     All 7 figures, one per slide, in order, image-based
                     (renders reliably in PowerPoint).

FIGURE ORDER (compiled number = filename = reading order)
  Figure 1  images/Figure_1.png  Design Science Research methodology        (fig:workflow)
  Figure 2  images/Figure_2.png  Heuristic severity, three apps             (fig:severity)
  Figure 3  images/Figure_3.png  Barrier -> principle -> objective -> impl  (fig:barrier-principle-map)
  Figure 4  images/Figure_4.png  Integrated BCHAIN-ACCESS framework         (fig:integrated)
  Figure 5  images/Figure_5.png  Four-layer architecture                    (fig:architecture)
  Figure 6  images/Figure_6.png  Automated audit (Lighthouse/WAVE/Axe)      (fig:auto-eval)
  Figure 7  images/Figure_7.png  Expert evaluation                          (fig:expert-eval)

TEX CHANGES (only \includegraphics filenames were renumbered; nothing else)
  line 507  Figure_6.png -> Figure_4.png   (integrated framework)
  line 1066 Figure_7.png -> Figure_6.png   (automated audit)
  line 1553 Figure_8.png -> Figure_7.png   (expert evaluation)
  (Figure_1/2/3/5 already matched their positions.)
  Reason: LaTeX numbers figures by position, so the old filenames were
  misleading (e.g. Figure_6.png was really Figure 4). Now they agree.

FILE FORMATS
  .pdf  - vector; recommended for LaTeX. To use, change .png to .pdf in the
          \includegraphics lines (or keep .png - high-res 250 dpi is included).
  .svg  - vector, editable in Illustrator / Inkscape (live text).
  .png  - 250 dpi raster (what the .tex currently references).
  .pptx - figure embedded as editable vector (right-click > Group > Ungroup).

DATA VERIFIED AGAINST THE MANUSCRIPT
  Fig 2: H8 = 2/1/2; means 2.9/2.3/2.8; major+catastrophic 7/4/6.
  Fig 4: Healthcare x Blockchain = PBFT / smart-contract consent;
         4-way convergence = biometric key binding + time-locked pending state.
  Fig 6: Lighthouse 100/100 composite; 23/73 passed, 1 cosmetic (deliberate).
  Fig 7: heuristic mean 0.1 (H9=1); task success 100% (80/80), 8 tasks;
         SUS 87.25 (SD 4.78, Grade A); questionnaire mean 4.42/5.

COMPILED PDF
  Sami_v22_compiled.pdf - the paper compiled to PDF (41 pages) with all
  seven figures integrated at their correct places (Figures 1-7 land on
  pages 5, 10, 12, 13, 14, 27, 34). Verified: 0 LaTeX errors, 0 undefined
  citations or references.
  NOTE: This preview was produced with the fallback class in preview_only/
  because the official IEEEtran.cls is not installed in the build sandbox.
  For submission, compile Sami_v22.tex with the real IEEEtran (Overleaf /
  TeX Live) - the .tex is unchanged apart from the figure-file renumbering.
