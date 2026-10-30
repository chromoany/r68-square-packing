# Manuscripts and source editions

| Edition | PDF | Source |
| --- | --- | --- |
| English color preprint | [manuscript.pdf](english/manuscript.pdf) | [source/main.tex](english/source/main.tex) |
| 中文独立稿 | [manuscript.pdf](chinese/manuscript.pdf) | [source/latex/chinese/main.tex](chinese/source/latex/chinese/main.tex) |

Both PDFs have eight pages. The English preprint uses an A4 color layout with three figures. The Chinese edition retains its compact journal layout and two figures. They state the same bounds; the typography and pagination are intentionally independent.

## English source

Use XeLaTeX with TeX Live, TeX Gyre Termes/Heros, Latin Modern Mono and TeX Gyre Termes Math. The style names the font files provided through TeX Live rather than local Windows font paths. The original edition was compiled using TeX Live 2025.

From the repository root:

```sh
cd paper/english/source
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
```

The result is `main.pdf` in that source directory. The distributed `manuscript.pdf` is the frozen reader PDF; it is not overwritten by these commands.

[arxiv-source.zip](english/arxiv-source.zip) preserves the complete 25-file upload package. It contains the same TeX and figure sources plus the 19-file proof supplement in `anc/`. In the repository, that supplement is unpacked at [`proof/`](../proof). References to `upper/` and `lower/` in the paper are relative to the supplement directory. No arXiv identifier has been assigned in this archive.

## 中文源码

中文版使用 XeLaTeX 与 `xeCJK`。原版要求 Times New Roman、SimSun（宋体）、SimHei（黑体）、KaiTi（楷体），以及 TeX Live 提供的数学与等宽字体。字体文件不随仓库分发；未安装这些字体时可直接阅读预编译 PDF。替换字体后应重新检查缺字、公式和分页。

在仓库根目录执行：

```sh
cd paper/chinese/source/latex/chinese
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
```

生成文件为当前源码目录下的 `main.pdf`，不会覆盖冻结的中文版 `manuscript.pdf`。保留已有目录层级，因为样式、参考文献与图片使用相对路径。

The PDFs and source bytes were preserved during GitHub packaging. These build instructions describe the source requirements; both manuscripts were **not recompiled** as part of this repository upload. The source archive's identity and every copied file are independently checked by the release manifest.
