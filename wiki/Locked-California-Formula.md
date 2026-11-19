> **\*2026 figures are UNOFFICIAL.** The California Secretary of State (SOS) results site, electionresults.sos.ca.gov, labels the November 3, 2026 general election results "Unofficial" (semi-final unofficial results with county updates; statewide figures as of November 19, 2026, 1:59 p.m. Pacific; pulled November 19, 2026). Counties are still in the canvass: the SOS Unprocessed Ballots Report (as of 11/18/2026 5:33 p.m.) estimated 100,313 ballots statewide still to process, plus 96,238 ballots left to cure. Counties must report final official results by December 4, 2026, and the SOS certifies on December 11, 2026, so these pages need a re-run after certification. 2022 figures are the certified Statement of Vote (certificate dated the 16th day of December, 2022). **P** = Democratic share of registered voters in the SOS 15-day Report of Registration (close of registration: as of October 24, 2022 and as of October 19, 2026). Governor race only. Votes are votes for the Democratic candidate, not a count of registered Democrats who voted. These pages measure a pattern; they make no claim about intent, fraud or cause.

## California fitted equation (final)

```
California equation:  ΔG = +6.09 + 1.53 × (Dem registration-share drop, points)
Four decimals:        ΔG = +6.0938 + 1.5300 × (Dem registration-share drop, points)
```

| Item | Rounded | Four decimals |
|---|---|---|
| Constant (intercept) | +6.09 | +6.0938 |
| Multiplier (slope) | 1.53 | 1.5300 |
| Intercept standard error | 1.05 | 1.0516 |
| Slope standard error | 0.54 | 0.5396 |
| R² | 0.13 | 0.1255 |

Fitted by ordinary least squares across all 58 counties (n = 58), each county weighted equally: 2022 to 2026\* governor race, registration from the SOS 15-day Reports of Registration, S denominator = total ballots cast, locked gap formula. Registration-share drop = P 2022 − P 2026, in points. 2026 figures are UNOFFICIAL. Computed separately in Pass A (numpy least squares) and Pass B (closed-form, pure Python); the two agree to within one part in a billion.

**What it means:** across California's counties, each one-point drop in Democratic registration share goes with about 1.53 points of ΔG, starting from about +6.09 when the share does not fall. The fit explains little of the county-to-county differences in ΔG (R² 0.13); the slope's standard error is 0.54.

**Worked example: Los Angeles.** P fell from 53.49 to 51.00, a drop of 2.4908 points. Predicted ΔG = +6.0938 + 1.5300 × 2.4908 = +9.90. Actual ΔG = +8.17\*. Difference from the fitted line (actual − predicted) = −1.74\*. Statewide (pooled totals): drop 1.9081, predicted +9.01, actual +8.45\*.

## The equation

- **S** (Democratic vote share) = Democratic governor votes ÷ total ballots cast × 100. Ballots cast is the county's total ballots cast (2022: SOV Voter Participation Statistics, Total Voters; 2026\*: SOS County Reporting Status, Ballots Cast).
- **P** (Democratic registration share) = Democratic registered voters ÷ Total Registered × 100, from the SOS 15-day Report of Registration (Registration by County) for each general election.
- **G** = S − P
- **ΔG** = G(2026) − G(2022) = (S2026 − S2022) − (P2026 − P2022)
- **Reverse step (residual).** Run it only where the Democratic registration count fell. Residual = ΔG − |P2026 − P2022|.
- **Solved backward: implied extra votes** = D2026 − (S2022 ÷ 100) × ballots2026
- **Registration-scaled gap** = D2026 − D2022 × (DemReg2026 ÷ DemReg2022)

### Why these files

- **Registration date.** The 15-day Report of Registration is the SOS's close-of-registration snapshot for each general election (as of October 24, 2022 and as of October 19, 2026). It is the same point in both election cycles, and it is the registration figure the SOS itself uses for turnout on its results pages.
- **Ballots, not governor votes.** S divides by total ballots cast in the county, so ballots with no governor vote stay in the denominator.
- **2022 is certified; 2026 is not.** The 2022 Statement of Vote is the certified canvass. The 2026 figures are the SOS's semi-final unofficial results with county updates, pulled November 19, 2026.

## Blank template

| Line | Item | 2022 | 2026 |
|---|---|---|---|
| L1 | Democratic governor votes | ______ | ______ |
| L2 | Total ballots cast | ______ | ______ |
| L3 | S = L1 ÷ L2 × 100 | ______ | ______ |
| L4 | Democratic registered voters (15-day Report of Registration) | ______ | ______ |
| L5 | Total Registered (same report) | ______ | ______ |
| L6 | P = L4 ÷ L5 × 100 | ______ | ______ |
| L7 | G = L3 − L6 | ______ | ______ |
| L8 | ΔG = G 2026 − G 2022 |  | ______ |
| L9 | Registration-share change = P 2026 − P 2022 |  | ______ |
| L10 | Did the Democratic registration count fall? (L4: 2026 below 2022) |  | Yes / No |
| L11 | If yes: residual = L8 − \\|L9\\| |  | ______ |
| L12 | Implied extra votes = L1 (2026) − L3 (2022) ÷ 100 × L2 (2026) |  | ______ |
| L13 | Registration-scaled gap = L1 (2026) − L1 (2022) × (L4 2026 ÷ L4 2022) |  | ______ |
| L14 | Fitted G = m × (L6 ÷ 100) + b, CA constants for that year | ______ | ______ |
| L15 | Distance from the CA line = L7 − L14 | ______ | ______ |
| L16 | Fitted-equation prediction = constant + multiplier × (− L9) |  | ______ |

## Worked example: Colusa (ceiling county)

| Line | Item | 2022 | 2026\* |
|---|---|---|---|
| L1 | Democratic governor votes | 1,553 | 2,682 |
| L2 | Total ballots cast | 5,617 | 6,194 |
| L3 | S | 27.65 | 43.30 |
| L4 | Democratic registered voters | 3,214 | 3,346 |
| L5 | Total Registered | 10,144 | 10,940 |
| L6 | P | 31.68 | 30.59 |
| L7 | G | −4.04 | +12.71 |
| L8 | ΔG |  | +16.75 |
| L9 | Registration-share change |  | −1.10 |
| L10 | Democratic registration count fell? |  | No |
| L11 | Residual |  | not run (non-loss county) |
| L12 | Implied extra votes |  | +969 |
| L13 | Registration-scaled gap |  | +1,065 |
| L14 | Fitted G | +5.35 | +15.22 |
| L15 | Distance from the CA line | −9.39 | −2.51 |
| L16 | Fitted-equation prediction |  | +7.77 |

## CA-only constants (forward fit)

The forward surplus equation is fit by least squares across all 58 California counties, each weighted equally: **G = m × (P ÷ 100) + b**. It uses California data only. No other state's constant is reused.

| Fit | n | m (SE) | b (SE) | R² | Residual SE | Within one / two / three pts | Median abs. residual |
|---|---|---|---|---|---|---|---|
| 2022, all counties | 58 | +36.93 (4.43) | −6.35 (1.82) | 0.554 | 3.77 | 17% / 36% / 53% | 2.98 |
| 2026\*, all counties | 58 | +24.89 (2.69) | +7.61 (1.06) | 0.604 | 2.29 | 36% / 64% / 83% | 1.37 |
| 2022, narrowed | 51 | +30.86 (4.77) | −3.71 (1.96) | 0.460 | 3.40 | 25% / 43% / 57% | 2.29 |
| 2026\*, narrowed | 51 | +23.96 (2.43) | +8.33 (0.96) | 0.665 | 1.72 | 47% / 75% / 94% | 1.03 |
| 2022, ballot-weighted | 58 | +38.10 (4.31) | −6.58 (2.05) | 0.582 | 3.78 | 17% / 34% / 55% | 2.72 |
| 2026\*, ballot-weighted | 58 | +13.27 (2.45) | +13.56 (1.12) | 0.344 | 3.08 | 28% / 62% / 74% | 1.71 |
| 2022 + 2026\* pooled | 116 | +27.70 (4.67) | +1.93 (1.89) | 0.236 | 5.64 | 9% / 19% / 33% | 4.50 |

**The locked CA constants are the all-county fits: 2022 m = +36.93, b = −6.35; 2026\* m = +24.89, b = +7.61.** Narrowed fits leave out San Francisco, Marin, Glenn, Lassen, Colusa, Modoc, Alpine (see [Floor and Ceiling Counties](Floor-and-Ceiling#counties-narrowed-out-of-the-fit)).

- **What m means.** G already contains −P, so an m of minus one hundred would mean S does not move with P at all, and an m of zero would mean S moves point for point with P. It is not an "injection multiplier."
- **Intercepts.** 2022 b 95% interval −10.00 to −2.70; 2026\* +5.48 to +9.74.

## Rules for using this formula

1. **Use registration from the same report in both years.** California's are the SOS 15-day Reports of Registration.
2. **If a county lost Democratic registrants, run the residual step.** In California that is 25 counties; the other 33 are non-loss counties.
3. **The starting point is different in every state.** California's constants come from California's own 58 counties. Los Angeles alone cast 3,180,986\* of 13,422,913\* ballots, but the equal-weight fit counts it once, like Alpine.
4. **Always pull out the ceiling and floor counties.** The ceiling county is Colusa (+16.75\*), and the lowest ΔG is San Francisco (−0.34\*). The floor (most Republican baseline) is Lassen, Modoc, Shasta, Tehama, Calaveras. See [Floor and Ceiling Counties](Floor-and-Ceiling).

---
**Related:** [Home](Home) · [Bottom-Up Reverse Math](Reverse-Math) · [Floor and Ceiling Counties](Floor-and-Ceiling) · [Graphs](Graphs) · [California County PDF Information](California-County-PDF-Information) · [Cedar County Audit (Nebraska)](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit)
