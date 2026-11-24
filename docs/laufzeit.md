# Run time: Windows vs. Linux (WSL2)

Measured on 24.11.2026 with `uv run serts bench` on the same laptop (Intel Core i7-1185G7, 4 cores / 8 threads,
32 GB RAM), first on Windows 11, then on Ubuntu 26.04 under WSL2 (8 threads, 15 GB). Same code (git `7053b0c`),
same package versions from `uv.lock` (Python 3.12, PyPSA 1.4, linopy 0.10, HiGHS 1.15). On Linux the repo was
cloned into the Linux file system (`~/serts`), not run from `/mnt/c`. Raw data: `benchmarks/bench.csv`.

Median per step, small network, full year (8760 h):

| Step | fixed sizes, Windows | fixed sizes, WSL | sizes optimised, Windows | sizes optimised, WSL |
|---|---|---|---|---|
| Time series | 1.5 s | 1.2 s | 2.1 s | 1.4 s |
| Model build (network) | 0.4 s | 0.3 s | 29.5 s | 7.5 s |
| Model generation (PyPSA/linopy) | 4.3 s | 3.0 s | 49.1 s | 38.4 s |
| Solver (HiGHS) | 86.4 s | 77.1 s | 1,821 s | 1,391 s |
| **Total (wall time)** | **95.7 s** | **81.7 s (−15 %)** | **460 s** | **334 s (−27 %)** |
| Heat price (check) | 227.08 €/MWh | 227.08 €/MWh | 225.94 €/MWh | 225.94 €/MWh |

*Fixed sizes* (`--modus fest`, 4,000 m² / 6,000 m³): one optimisation, 3 repetitions. *Sizes optimised*
(`--modus voll --jobs 5`): the five storage cost segments solved in parallel as in a real run, 2 repetitions. In this
mode the step times are summed over the five parallel segments and are therefore larger than the wall time.

**Reading:**
- Results are identical on both systems, so the model can move to Linux without changing any result.
- The solver takes over 90 % of the time. HiGHS itself runs 11 % faster under WSL with one process and 24 % faster
  with five parallel processes; Python/PyPSA steps are 20–75 % faster.
- With parallel segments Linux gains most (−27 %): building the networks in five processes at once costs four times
  as long on Windows, where every worker process starts from scratch.
- Run order was Windows first, then WSL, for each mode. WSL never ran on a cooler CPU, so thermal throttling does not
  explain its lead. Small samples (2–3 runs); repetitions spread by ±5 %.

**Side finding:** `serts run` currently solves the segments one after another (≈ 14 min for the small network on
Windows). Solved in parallel as in the benchmark, the same run takes ≈ 8 min on Windows and ≈ 5.5 min under WSL.

To repeat the comparison: `uv run serts bench --modus fest` (≈ 5 min) or `--modus voll --jobs 5` (≈ 15 min) on each
system; every run appends to `benchmarks/bench.csv`. Every `serts run` also records its step times and the platform in
`meta.json`.
