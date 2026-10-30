# Revision 2 — 30 October 2026

The theorem is unchanged: `39/8 < r(68) <= Rhat < 5.031404629453352`. This revision strengthens reproducibility and clarifies contribution; it reports no new mathematical bound.

- Preserve the original reader edition as [v1.0.0](https://github.com/chromoany/r68-square-packing/tree/v1.0.0), commit `453ad1abbc536c85496a47329ba9fe5f437de671`. The previously submitted journal manuscript is not replaced by this repository revision.
- Replace certificate acceptance assertions with explicit checks. Both the official wrapper and core reject optimized Python. The old search/resume CLI and temporary-name CLI fail immediately with directions to the official wrapper. Mathematical expressions and all construction/weight/cover data are unchanged.
- Freshly replay all 11,837 lower-bound leaves on a Slurm compute node, with a genuine `COMPLETED / 0:0` result. Preserve the historical replay separately. Re-run the complete exact upper check and the documented small controls.
- Add one contribution paragraph comparing the lower bound with the elementary area baseline, and cite Friedman's collection with its limited coverage. Update the Arb citation to the published 2017 article. Add a short fresh-replay statement. All numbered theorem/lemma/proposition statements and numbered formulas remain unchanged.
- Recompile and visually inspect the English and Chinese manuscripts separately. Retain their existing layout and figures.

The fresh replay is a rerun of the existing mathematical algorithm; it is not a new independent implementation. Test doubles used in failure controls are labeled as such. Neither these changes nor the fresh replay resolve the exact optimum or the radius-5 question.

## 本次修订

上下界、精确构造和原证书数据不变。修改仅涉及验证入口鲁棒性、一次新鲜完整回放、简短贡献定位与正式文献引用。旧读者版保留于 v1.0.0；已经投出的期刊稿继续保留原件，本次没有联系编辑或重新投稿。

详见 [完整回放原件](../proof/lower/fresh-full-replay.json)、[环境与调度记录](../proof/lower/fresh-replay-provenance.json)及[中英文复核说明](../proof/README.zh.md)。
