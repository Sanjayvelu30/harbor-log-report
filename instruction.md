Determine the high‑precision value of oscillatory integrals of the form

    I(ω) = ∫_{a}^{b} f(x)·cos(ω x) dx

for a set of synthetic test cases covering a wide range of frequencies, function families, and phase behaviours.

### Input Contract

The harness provides a JSON file **`/app/integral_cases.json`** containing a list of case objects, each with the following fields:

```json
{
  "id": "0",
  "f": "poly3",            // identifier from the whitelist (see below)
  "f_params": {"coeffs": [1.2, -0.3, 0.0, 2.5]}, // polynomial coefficients highest‑degree first
  "g": "linear",           // "linear" for cos(ω·x) or "quadratic" / "sin" for non‑linear phase
  "g_params": {"expr": "x**2"},   // required only when g ≠ "linear"
  "a": 0.0,
  "b": 1.0,
  "omega": 12345.0
}
```

**Function whitelist** – The solver may only use the following predefined functions (provided as Python callables via a small helper module):

- `polyN` – polynomial of degree *N* (coefficients supplied in `f_params.coeffs`).
- `exp` – exponential `exp(k·x)` (parameter `k`).
- `besselJ` – Bessel function of the first kind `jv(n, x)` (order `n` supplied).

**Phase `g`** – Determines the argument of the cosine. `"linear"` corresponds to `g(x)=x`; other values require the expression given in `g_params.expr` (a safe subset of Python arithmetic, parsed by the harness). The solver receives the callable `g(x)` when `g` is non‑linear.

### Required Output

The agent must write a JSON dictionary **`/app/results.json`** mapping each case `id` to an object with the exact schema:

```json
{
  "integral": <float>,          // computed value
  "error_estimate": <float>,    // reported tolerance (must be ≤ 1e‑12)
  "nodes_used": <int>,          // number of function evaluations (instrumented by the harness)
  "method": "filon" | "levin" | "mpmath" | "custom"
}
```

The `method` field may contain any non‑empty string, but it must truthfully describe the algorithm used. The harness will verify that the reported `nodes_used` matches an independent call counter; the field is **not** self‑reported.

### Evaluation Criteria

1. **Correctness** – For each case, either
   * `abs(computed – reference) ≤ 1e‑10`, or
   * `abs(computed – reference) / |reference| ≤ 1e‑10`.
   The hidden reference values are generated with 400‑digit MPFR precision.
2. **Efficiency** – The harness enforces a hard evaluation budget (function‑call count) that depends on the frequency:
   * `ω ≤ 1e4` → ≤ 10 000 calls
   * `ω > 1e4` → ≤ 100 000 calls
3. **Robustness** – All 100 hidden cases must satisfy both correctness and efficiency.
4. **Method Transparency** – The `method` string is checked for consistency with the observed call pattern; no subjective grading is performed.

### Implementation Hint

Provide a clean Python module **`oscint.py`** exposing:

```python
from typing import Callable, Tuple

def oscillatory_integral(
    f: Callable[[float], float],
    g: Callable[[float], float],
    a: float,
    b: float,
    omega: float,
    *,
    tol: float = 1e-12,
) -> Tuple[float, int, str]:
    """Return (integral, nodes_used, method_name)."""
```

The solution should combine:
- Phase‑aware interval splitting
- Filon‑type quadrature on linear‑phase sub‑intervals
- Levin‑type collocation for non‑linear phases
- Adaptive refinement via Richardson extrapolation
- High‑precision fallback with `mpmath` when `omega` is large or the error estimate stalls.

### Time Estimate

≈ 2 person‑weeks (≈ 80 h) for a production‑ready implementation, tests, and documentation.

You have **1800 seconds** to complete this task. The clock starts now.

