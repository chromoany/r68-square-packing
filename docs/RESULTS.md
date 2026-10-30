# Results and mathematical scope

The problem concerns **68 closed unit squares**, arbitrary real translations and rotations, pairwise disjoint interiors, and a closed enclosing disk. Tangency is permitted. Let `r(68)` denote the infimum of feasible radii; the compactness argument in the paper supplies attainment where needed for the strict exclusion bound.

## Proved statement

$$
\frac{39}{8}<r(68)\le\widehat R<U,
\qquad U=\frac{5031404629453352}{10^{15}}.
$$

The lower endpoint is 4.875, and the upper endpoint is the exact terminating decimal 5.031404629453352. The interval contains 5. No conclusion about feasibility at radius 5 follows.

## The explicit packing

For each square the [coordinate file](../proof/upper/best-68-exact-state.json) gives rational center `c`, rational unit vector `u`, and its perpendicular `v`. Its vertices are `c + (epsilon*u + eta*v)/2`, for `epsilon, eta` in `{-1, 1}`. The verifier checks exact unit lengths and all pairs using separating axes, accepting tangency.

The maximum squared vertex norm is the exact rational `p/q`. The complete coprime integers are in [best-68-exact-radius.json](../proof/upper/best-68-exact-radius.json). The positive root of `q*R^2-p=0` is isolated by

```text
5.031404629453350730787899409097 < R
R < 5.031404629453350730787899409098
```

The maximum occurs uniquely at vertex `(25, +1, +1)`. This is the exact radius **about the specified origin**. Neither optimality after recentering nor global optimality is asserted. The radius file's original metadata separates its radius calculation from earlier pairwise geometry checks; the independent upper verifier in this repository freshly checks both properties together.

## The exclusion certificate

The lower-bound proof rescales a hypothetical radius-39/8 unit-square packing into a radius-5 packing of squares of side 40/39. A nonnegative radial weight on 80 annuli assigns a uniformly positive weighted area to every admissible square. The exact disk-cost comparison contradicts the presence of 68 such squares.

Rotation invariance fixes the orientation of a single square. Reflections reduce its center to a two-dimensional first-octant domain. The proof covers that continuous domain using a prefix-free binary subdivision with these leaves:

| Accepted or excluded leaf type | Count |
| --- | ---: |
| Common inner rectangle | 1583 |
| Derivative bound | 8923 |
| Geometrically excluded | 1331 |
| Total | 11837 |

There are no pending leaves in the frozen certificate. The [English manuscript](../paper/english/manuscript.pdf) proves the geometric reductions, integral formulas, enclosure estimates and counting argument. [The replay guide](../proof/README.en.md) explains how the finite certificate is checked and the distinction between a preflight and a complete integral replay.

## Claims not made

- The exact global value of `r(68)` has not been determined.
- Feasibility of 68 squares at radius 5 remains undecided.
- A floating-point tolerance, a local optimum, an unsuccessful heuristic or a restricted family is not used as a global exclusion proof.
- The algebraic equation describes this construction, not the unknown global optimum.
- The direct historical comparison in the paper is to the cited Jelliss construction of radius `sqrt(26)`; it is not a claim to a current world record or exhaustive novelty.
- The result is computer-assisted and relies on the stated arithmetic implementations; no Lean/Coq formalization is supplied.

The manuscript bibliography records the literature used. This reader archive intentionally focuses on the two `r(68)` bounds and their evidence.
