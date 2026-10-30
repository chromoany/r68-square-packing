# Reader revision 2 — 30 October 2026

This revision hardens verification and adds a fresh complete replay. It introduces no new mathematical bound. The original reader release is preserved as [v1.0.0](https://github.com/chromoany/r68-square-packing/tree/v1.0.0), commit `453ad1abbc536c85496a47329ba9fe5f437de671`.

| Artifact | Edition | SHA-256 |
| --- | --- | --- |
| [English PDF](../paper/english/manuscript.pdf) | 8-page color preprint, v2 | `6685348530a1a6f3e485fc1b1499503f38cf624a3165a4f3643cbb58566541d3` |
| [Chinese PDF](../paper/chinese/manuscript.pdf) | 8-page separate manuscript, v2 | `45dbf839e90773577cc5516a97076729ae68f5b2854f8576c1e3ef3378e99306` |
| [English source archive](../paper/english/arxiv-source.zip) | 33 files, including `anc/` | `334a52139081ea3cdd9fdc12ac753269f62bbf33a247e6b7bcc1d905ff9bc924` |

## Checks executed

- Complete exact upper verification: all 68 unit directions, 272 vertices, 2278 pairs, the radius equation and isolation interval.
- Complete fresh lower replay: all 11,837 leaves, Arb256, 16 workers; Slurm **126395001**, `COMPLETED`, exit `0:0`. Integral replay: approximately 20.245 seconds; full job: 27 seconds.
- CPython 3.12.6, python-flint 0.8.0, FLINT 3.3.1, Linux x86_64. See [raw result](../proof/lower/fresh-full-replay.json) and [provenance](../proof/lower/fresh-replay-provenance.json).
- Lower preflight, 17 wrapper controls, 20 entry-point controls and area-kernel self-check. Simulated controls are explicitly distinguished from real integral replay.
- Numbered mathematical statements/formulas and all original figures unchanged; construction/weight/cover data and historical replay byte-identical to v1.
- Both PDFs compiled and all pages rendered with PDFium and PDF.js; PDF.js visual review completed without system fonts or external CMaps. Embedded fonts, Chinese glyphs, formulas and pagination checked.
- Source archive members checked against the corresponding published sources and supplement.

The fresh replay uses the same mathematical verification algorithm, with explicit runtime checks replacing assertions. It is not an independent reimplementation. [The revision note](REVISION-v2.md) lists the narrow manuscript changes.

## Integrity

[artifact-manifest.json](../artifact-manifest.json) records release bytes and SHA-256 values, excluding itself. Run `python -B tools/check_integrity.py` to check the release and proof inventories. These hashes identify the release; they are neither a signature nor an additional mathematical proof.

Git line-ending conversion remains disabled because the proof manifest pins raw source bytes. Original submitted materials remain unchanged in their separate archive. No editor contact or resubmission is performed by this repository update. The prepared arXiv source archive does not imply that the paper has been announced on arXiv.
