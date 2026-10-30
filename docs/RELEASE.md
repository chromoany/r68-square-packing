# Bilingual color preprints — v3.0.0

30 October 2026. Both default reader manuscripts now use an A4 color preprint design. Each has eight pages and three vector figures. This is a presentation and packaging update; the mathematical bounds and all 27 proof files are unchanged from v2.

| Artifact | Edition | SHA-256 |
| --- | --- | --- |
| [English PDF](../paper/english/manuscript.pdf) | 8-page arXiv-format preprint | `36a428651796e40b4c91ba0a52936c079f278f140d642ffbf751bb30979e3dbd` |
| [Chinese PDF](../paper/chinese/manuscript.pdf) | 8-page Chinese color preprint | `c34f4485a5539a86cafffaf71359630121891f1c9c386cfcf2c65d644dac2af0` |
| [English source archive](../paper/english/arxiv-source.zip) | 33 files, including `anc/` | `3264a15bdccd66643451e162689632b6b2b8387610afb7c7f30362d511c41d67` |
| [Chinese source archive](../paper/chinese/preprint-source.zip) | 41 files, including fonts and `anc/` | `5c809a8bad6eca098903273585f518290c5c21108c223849a8353765f2e53910` |

## Checks for this presentation revision

- All pages rendered and visually checked in both languages. All fonts embedded; Chinese text remains visible without system fonts or external PDF.js CMaps. No missing-character, overflow, underflow or unresolved-reference warnings.
- Both source archives extracted and compiled in clean directories. The resulting PDFs match the reviewed reader PDFs page by page in text and rendered pixels.
- All 15 numbered mathematical blocks per language unchanged. Chinese figures use the same exact coordinates, 80 weights and 11,837-leaf cover; English figure bytes are unchanged.
- All 27 proof files byte-identical to v2. Source archive members, previous-version archive, relative links and release hashes checked. No new scientific computation or integral replay was run for v3.
- [v1.0.0](https://github.com/chromoany/r68-square-packing/tree/v1.0.0) and [v2.0.0](https://github.com/chromoany/r68-square-packing/tree/v2.0.0) are retained. Previously submitted journal materials were checked and remain unchanged.

See [v3 changes](REVISION-v3.md), [PDF checks](../validation/pdf-qa.json), [source checks](../validation/source-archive-checks.json) and [release checks](../validation/release-checks.json).

## Retained verification evidence from v2

Version 2 completed the exact upper check and a fresh full lower replay of all 11,837 leaves on Slurm job **126395001**, `COMPLETED`, exit `0:0`. The integral replay took approximately 20.245 seconds, using Arb256 and 16 workers. Environment: CPython 3.12.6, python-flint 0.8.0, FLINT 3.3.1, Linux x86_64. Its [raw result](../proof/lower/fresh-full-replay.json) and [provenance](../proof/lower/fresh-replay-provenance.json) are preserved, not regenerated for this layout update. The replay is a rerun of the same mathematical algorithm, not an independent reimplementation. The [v2 note](REVISION-v2.md) records the verification-entry repairs and small control tests.

## Integrity and status

[artifact-manifest.json](../artifact-manifest.json) records release bytes and SHA-256 values, excluding itself. Run `python -B tools/check_integrity.py` to check both release and proof inventories. These hashes identify the files; they are not a signature or a mathematical proof.

This update does not contact the journal or submit to arXiv. The English source archive is prepared for the author's arXiv workflow; the Chinese source archive is a separate reader edition. Local compilation does not replace checking arXiv's generated PDF during actual submission.
