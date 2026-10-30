# Reproducibility supplement: 68 unit squares in a circle

This supplement supports the two bounds

\[
\frac{39}{8}<r(68)\leq U,
\qquad U=\frac{5031404629453352}{10^{15}}=5.031404629453352.
\]

Here squares may have arbitrary real translations and rotations; their interiors must be disjoint, and boundary contact is permitted. Neither the exact global optimum nor feasibility at radius 5 is determined by these bounds. The mathematical arguments, including the continuous-pose coverage argument for the lower bound, are in the accompanying paper. The programs check their finite certificates.

## Files and arithmetic

- `upper/` contains one exact 68-square construction, its exact fixed-origin radius, an independent standard-library verifier, and the result of the complete verification on 30 October 2026.
- `lower/` contains the frozen radial-weight and pose-cover data, two original proof kernels, the archived complete replay result, and a new verification wrapper with small failure-path controls.
- `inventory.json` records the size and SHA-256 of every other file in this supplement. `lower/proof-manifest.json` separately freezes the eight original lower-bound payload files; its SHA-256 is embedded in the wrapper.

The original coordinate, radius, cover, weight, cost and replay files are byte-preserving copies. Exact rational strings in the coordinate and cover files are authoritative. In particular, the verifier reads `shell_edges` and `shell_weights` from `translation-gradient-cover-state.json`; the auxiliary weight JSON/CSV files provide the same rational weights for convenient inspection. Figures and displayed decimal approximations are illustrations, not proof input.

All commands below are run from this supplement directory with Python 3. The upper verifier uses only the Python standard library. The lower integral replay additionally requires `python-flint==0.8.0` and uses Arb at 256-bit precision. The mathematical arguments and implementation assume correct Python integer/rational arithmetic and correct FLINT/Arb enclosure operations; this is not a proof-assistant formalization.

## Exact upper-bound verification

```text
python upper/verify-upper.py upper/best-68-exact-state.json --radius upper/best-68-exact-radius.json
```

A successful complete run prints `PASS_EXACT_68_SQUARE_UPPER_BOUND`. It checks 68 exact unit direction vectors, all 272 vertices, and all 2,278 unordered square pairs using exact rational separating-axis comparisons. Tangency is accepted. It also independently derives the largest squared vertex distance and checks the radius polynomial and isolating interval.

The complete target was freshly replayed for this edition. `upper/verification-result.json` records all 2,278 pairs and 272 vertices passing, with first successful separating-axis counts 1,847, 411, 10 and 10. Its recorded elapsed time is approximately 0.328 seconds on the machine used; this is an observation, not a runtime guarantee.

The supplied construction has fixed-origin radius

\[
\widehat R=\sqrt{p/q},\qquad q\widehat R^2-p=0,\quad\widehat R>0,
\]

where the coprime integers `p` and `q` are stored in `best-68-exact-radius.json` as `squared_radius_numerator` and `squared_radius_denominator`. They have 1,451 and 1,450 digits. The verifier checks

\[
5.031404629453350730787899409097
<\widehat R<
5.031404629453350730787899409098<U.
\]

This is the exact radius about the specified origin of this construction. It is not asserted to be its minimum enclosing radius after recentering, or to equal the global optimum `r(68)`. The unique farthest vertex has identifiers `(25, +1, +1)` in the data.

Small geometric controls can also be run:

```text
python upper/verify-upper.py --self-test
```

These controls are separate from the complete target replay.

## Lower-bound replay

Install the pinned dependency in a suitable Python environment:

```text
python -m pip install -r lower/requirements.txt
```

Then run the complete frozen certificate:

```text
python lower/verify-lower.py
```

The default invocation preserves the archived successful replay settings: 16 workers and a 300-second replay budget. Options are available, for example:

```text
python lower/verify-lower.py --workers 16 --budget 300 --scratch-parent .
```

`--scratch-parent` must name an existing writable directory. Each invocation creates its own temporary child directory and removes that child when finished; the packaged original files are not modified. Standard output contains the resulting JSON and may be redirected to a new result file if desired.

The frozen original verifier accepts 1–32 workers and a replay budget of 1–600 seconds. These limits are its preserved per-invocation interface, not a claim about a platform limit or a scientific search stopping rule. Budget exhaustion produces an incomplete result, never a lower-bound certificate. Do not invoke the wrapper with Python `-O` or `-OO`: its preserved proof kernels use assertions, and the wrapper explicitly rejects optimized mode.

Before replay, the wrapper verifies every frozen source/data identity, the rational problem parameters, the nonnegative weights, the exact cost comparison and the prefix-free binary cover topology. It checks that the 11,837 leaves consist of 1,583 inner-rectangle leaves, 8,923 gradient leaves and 1,331 excluded leaves, with no pending leaves or strict-gap witnesses. These preflight checks do not evaluate any integral.

For an actual replay the wrapper runs the frozen verifier in fresh scratch, without copying the historical result into it. It checks the process exit code, newly generated result, exact status and leaf counts, all-gradient completion, input identity and unchanged proof files. Only a complete fresh replay prints `PASS_GLOBAL_REAL_R68_LOWER_GRADIENT` together with `fresh_full_replay: true`. The kernel also recomputes the outward-rounded integral and derivative bounds and the required upper enclosure of π. An exit code of zero, an archived `PASS`, or completed file transport alone is insufficient.

### What was and was not rerun for this edition

`lower/translation-gradient-independent-replay.json` is the preserved historical complete replay: all 11,837 leaves passed with 16 workers and a recorded duration of approximately 19.596 seconds. The full integral replay was **not rerun** when this submission supplement was assembled. That historical result is not relabeled as a fresh result.

The new wrapper was checked with small controls only. `lower/wrapper-control-result.json` records 17 rejected malformed or incomplete cases, including modified source/data, missing or partial output, unsuccessful subprocess exit, altered proof inputs and an actual Python `-O` invocation. The subprocess-output failure controls are simulations, as the result explicitly records. These tests do not establish the integral inequalities again.

The following commands require only the Python standard library:

```text
python lower/verify-lower.py --check-inputs
python lower/test-wrapper.py
```

Run `test-wrapper.py` from a writable current directory. The preflight status is `INPUTS_CHECKED_NO_INTEGRAL_REPLAY`; it does not recompute π or any leaf integral. The control-test status is `SMALL_WRAPPER_CONTROLS_OK`. Neither status means that the complete lower-bound replay has just run.

No optimization, layout generation, remote login or job submission is performed by these reader entry points.
