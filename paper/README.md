# Separate English and Chinese color preprints

| Edition | PDF | Source | Complete archive |
| --- | --- | --- | --- |
| English arXiv-format preprint | [8-page PDF](english/manuscript.pdf) | [main.tex](english/source/main.tex) | [arxiv-source.zip](english/arxiv-source.zip) |
| 中文彩色预印本 | [8 页 PDF](chinese/manuscript.pdf) | [main.tex](chinese/source/main.tex) | [preprint-source.zip](chinese/preprint-source.zip) |

Both editions use the same A4 single-column design, blue-green headings and three color vector figures. They remain separate documents with the same numbered mathematical statements and formulas. The Chinese edition adapts line spacing, typography and page breaks for Chinese readers. It is a reader edition, not an additional arXiv submission.

## Compilation

Use XeLaTeX with TeX Live. Latin text and mathematics use the TeX Live fonts TeX Gyre Termes/Heros, Latin Modern Mono and TeX Gyre Termes Math. The Chinese project additionally uses `xeCJK` and the four TrueType font subsets included under `fonts/`; no installed Chinese system font is required. Their SIL Open Font License and provenance are included. See [font notes](chinese/source/fonts/README.md) before adding new Chinese characters.

From the repository root, choose one source directory:

```sh
cd paper/english/source
# Or, for Chinese: cd paper/chinese/source
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
```

The result is `main.pdf` in that source directory; the distributed reader PDF `manuscript.pdf` is not overwritten. The packaged sources were also compiled from clean extracted directories with Tectonic 0.17.0 (XeTeX). All figures and styles use relative paths.

## Archive contents

The English archive contains six TeX/style/figure files plus the unchanged 27-file proof supplement under `anc/` (33 files total). The Chinese archive contains its TeX files, three vector figures, font subsets and notices, plus the same supplement. References to `upper/` and `lower/` in the paper are relative to `anc/`; the supplement is unpacked under [`proof/`](../proof) in this repository.

For the English arXiv workflow, use [the upload guide](ARXIV.md). Upload the English source archive, not the entire GitHub repository or the compiled reader PDF. The package has a root-level `main.tex`; no temporary TeX outputs are included. Preparation and local compilation do not imply arXiv acceptance or announcement.

Both current PDFs were rendered with PDFium and PDF.js and reviewed page by page, including a PDF.js run without system fonts or external CMaps. All fonts are embedded. See [v3 changes](../docs/REVISION-v3.md) and [PDF checks](../validation/pdf-qa.json). Earlier editions remain in [v1.0.0](https://github.com/chromoany/r68-square-packing/tree/v1.0.0) and [v2.0.0](https://github.com/chromoany/r68-square-packing/tree/v2.0.0).
