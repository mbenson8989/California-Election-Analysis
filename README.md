# California Election Analysis: 2022 vs 2026 Governor (ΔG method)

**\*2026 figures are UNOFFICIAL** (CA SOS semi-final unofficial results, statewide as of November 19, 2026, 1:59 p.m. Pacific). The SOS certifies on December 11, 2026. 2022 figures are the certified Statement of Vote.

County-level analysis of the California governor race, 2022 vs 2026, for all 58 counties. It uses the ΔG method from Morissa Benson's [Cedar County Audit](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit). The full write-up is on the **[wiki](https://github.com/mbenson8989/California-Election-Analysis/wiki)**.

- **S** = Democratic governor votes ÷ total ballots cast
- **P** = Democratic registered voters ÷ Total Registered, SOS 15-day Report of Registration
- **G** = S − P; **ΔG** = G2026 − G2022; residual = ΔG − |ΔP| for counties whose Democratic registration count fell; implied extra votes = D2026 − S2022 × ballots2026
- **California fitted equation:** ΔG = +6.09 + 1.53 × (Dem registration-share drop, points)
- **CA-only constants** (G = m × P ÷ 100 + b, all counties): 2022 m = +36.93, b = −6.35; 2026\* m = +24.89, b = +7.61

## Contents

| Path | What |
|---|---|
| CA_*.png | The charts used on the wiki |
| California_58_County_Democratic_Registration_and_Vote_Change.pdf | The county PDF (Democratic registration, Democratic governor votes and total ballots, 2022 vs 2026\*), with its Excel source |
| data/CA_Governor_2022_2026_DeltaG_by_County.csv | All counties, every input and computed figure, sorted by population |
| data/CA_results_summary.json | Fits, narrowed fits, floor and ceiling, over-ballot checks, statewide totals |
| verification/ | Pass A and Pass B county tables, the figure-by-figure comparison, the PDF cell check, the wiki number check, the render check |
| raw/ | Untouched source files: 2022 Statement of Vote, 15-day Reports of Registration, 2026 results-site API JSON and rendered pages, Census file, fetch logs |
| scripts/ | run_all.sh runs the whole build in order |
| wiki/ | The wiki pages and _Sidebar.md, as they will be pushed to the wiki |

## Verification

Two independent passes over the raw SOS files: 1,160 figure comparisons, 1,160 matched and 0 mismatched. The county PDF: 1,180 of 1,180 cells matched a recomputation from the raw files. Every number on the wiki pages and in this README was traced to both passes.

These pages measure a pattern. They make no claim about intent, fraud or cause.
