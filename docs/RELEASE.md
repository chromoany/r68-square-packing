# Reader release — 30 October 2026

This repository packages the completed `r(68)` manuscripts and their verification material. It introduces no new mathematical bound.

## Edition identity

| Artifact | Edition | SHA-256 |
| --- | --- | --- |
| [English PDF](../paper/english/manuscript.pdf) | 8-page color preprint | `0b757cbe885e774caab3738a522432e0580bec05d525b45fa65d301a149b7e5f` |
| [Chinese PDF](../paper/chinese/manuscript.pdf) | 8-page separate Chinese manuscript | `be96c99a3254db9d8315edc86294491fa19629f9e29223eb9788324f2b25e639` |
| [English source archive](../paper/english/arxiv-source.zip) | 25 files, including `anc/` | `2dbcb7e03fbe8fb1aeb5ca3411507efc9f308a63e179ef45b0b74a49ce380f84` |

The papers, supplied figures and all 19 files under `proof/` are byte-preserving copies of the reader editions. No proof kernel or certificate has been rewritten for GitHub. English and Chinese PDF page counts, glyphs, formulas and pagination were checked during the manuscript release; this packaging step preserves those exact PDFs.

## Check status

[validation/release-checks.json](../validation/release-checks.json) records the checks freshly executed for the GitHub package:

- every copied artifact and every frozen supplement entry matches its source hash;
- the complete 68-square upper-bound verifier;
- its small valid and invalid geometric controls;
- the lower input, cover and exact cost preflight;
- the lower wrapper's failure-path controls;
- the source ZIP's member identities and integrity.

The original complete lower replay, [translation-gradient-independent-replay.json](../proof/lower/translation-gradient-independent-replay.json), remains historical evidence. **No new integral replay was performed during GitHub packaging.** The preflight and wrapper controls do not replace it. Readers can run the complete verifier using [the documented entry point](../proof/README.en.md).

## Integrity and reproducibility

[artifact-manifest.json](../artifact-manifest.json) records the bytes and SHA-256 of the release files, excluding the manifest itself. `python -B tools/check_integrity.py` validates these entries and checks the inner proof inventory. The hash inventory detects changes relative to this release; it is not a cryptographic signature or an additional mathematical proof.

Git attributes disable line-ending conversion for the imported proof artifacts, manuscript sources and validation records. This is necessary because the lower verifier pins raw source/data bytes. Preserve those bytes when copying the package.

The runtime stack for exact checks is documented in [proof/README.en.md](../proof/README.en.md); typesetting dependencies are in [paper/README.md](../paper/README.md). Prebuilt PDFs can be read without a TeX installation. The name `arxiv-source.zip` identifies a prepared source format; it is not evidence that the paper has been announced on arXiv.
