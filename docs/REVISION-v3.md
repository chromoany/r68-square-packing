# Preprint presentation revision — v3.0.0

30 October 2026. This revision updates presentation and source packaging. It introduces no new mathematical result and no new integral replay.

- English: retains the A4 color preprint design, with a public supplement link added to the reproducibility section.
- Chinese: replaces the active compact journal layout with a separate A4 color preprint matching the English design. All three vector figures have Chinese labels. The title, headings, spacing and page breaks are adapted for Chinese reading.
- Both editions: eight pages, three figures, embedded fonts, complete source archives and root-level `main.tex`. The Chinese source includes renamed, licensed Noto font subsets.
- Mathematical content: all 15 numbered equation/theorem/proposition blocks in each language are unchanged from v2. The English figures and all 27 proof files are byte-identical to v2. Chinese figures visualize the same exact data and frozen cover; no new search was run.
- Verification evidence: the full v2 replay, Slurm 126395001 (`COMPLETED / 0:0`), is retained. It is not relabeled as a new v3 run.

All pages of both PDFs were rendered and visually checked, including Chinese text, formulas, figure captions and pagination. Source archives were verified member by member and compiled after extraction into clean directories. See [release checks](../validation/release-checks.json), [PDF checks](../validation/pdf-qa.json) and [figure checks](../validation/chinese-figures.json).

The earlier [v1.0.0](https://github.com/chromoany/r68-square-packing/tree/v1.0.0) and [v2.0.0](https://github.com/chromoany/r68-square-packing/tree/v2.0.0) remain available. Previously submitted journal materials are unchanged. This update neither contacts the journal nor submits anything to arXiv.
