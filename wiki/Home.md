> **\*2026 figures are UNOFFICIAL.** The California Secretary of State (SOS) results site, electionresults.sos.ca.gov, labels the November 3, 2026 general election results "Unofficial" (semi-final unofficial results with county updates; statewide figures as of November 19, 2026, 1:59 p.m. Pacific; pulled November 19, 2026). Counties are still in the canvass: the SOS Unprocessed Ballots Report (as of 11/18/2026 5:33 p.m.) estimated 100,313 ballots statewide still to process, plus 96,238 ballots left to cure. Counties must report final official results by December 4, 2026, and the SOS certifies on December 11, 2026, so these pages need a re-run after certification. 2022 figures are the certified Statement of Vote (certificate dated the 16th day of December, 2022). **P** = Democratic share of registered voters in the SOS 15-day Report of Registration (close of registration: as of October 24, 2022 and as of October 19, 2026). Governor race only. Votes are votes for the Democratic candidate, not a count of registered Democrats who voted. These pages measure a pattern; they make no claim about intent, fraud or cause.

Method developed by Morissa Benson (CD3 Vice Chair, Nebraska GOP). It began with her [Cedar County Audit](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit) on the [Nebraska Election Analysis wiki](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki). That audit is where the ΔG method and the reverse step come from. This wiki applies the same arithmetic to all 58 California counties. California has party registration, so it uses the registration baseline, as the Nevada, North Carolina, Kansas and Pennsylvania analyses do. Data: California Secretary of State Statement of Vote, Reports of Registration and election-night results ([sos.ca.gov](https://www.sos.ca.gov/elections/prior-elections/statewide-election-results/general-election-nov-8-2022/statement-vote), [Report of Registration](https://www.sos.ca.gov/elections/report-registration/15day-general-2026), [electionresults.sos.ca.gov](https://electionresults.sos.ca.gov/)). Population (sort order only) comes from the U.S. Census Bureau. Compiled November 19, 2026. Code and data: [California-Election-Analysis](https://github.com/mbenson8989/California-Election-Analysis).

## Pages

1. [Cedar County Audit](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit) (Nebraska wiki): where the method started
2. [Bottom-Up Reverse Math](Reverse-Math): Colusa (the ceiling county), the five largest counties, then all counties, solved backward for implied extra votes
3. [Locked California Formula](Locked-California-Formula): the California fitted equation, a blank template, a worked example and the California-only constants
4. [Floor and Ceiling Counties](Floor-and-Ceiling): the floor and ceiling counties, the counties narrowed out of the fit, and the over-ballot check
5. [Graphs](Graphs): slope chart, ΔG by population, the ΔS and ΔP components, forward fit, residuals and the over-ballot check
6. [California County PDF Information](California-County-PDF-Information): the county PDF (download), what each column means, and its cell-by-cell check

## Statewide at a glance

| Measure | 2022 | 2026\* | Change |
|---|---|---|---|
| Democratic registered voters (15-day report) | 10,283,258 | 10,464,099 | +180,841 |
| Total registered voters (15-day report) | 21,940,274 | 23,273,590 | +1,333,316 |
| **P**: Democratic share of registration | 46.87% | 44.96% | −1.91 pts |
| Democratic governor votes | 6,470,104 | 8,669,071 | +2,198,967 |
| Republican governor votes | 4,462,914 | 4,542,458 | +79,544 |
| Total ballots cast | 11,146,620 | 13,422,913 | +2,276,293 |
| **S**: Democratic share of ballots cast | 58.05% | 64.58% | +6.54 pts |
| **G** = S − P | +11.18 | +19.62 | ΔG +8.45 |

Candidates (top-two general election): 2022 Gavin Newsom (DEM, incumbent) and Brian Dahle (REP). 2026\* Xavier Becerra (DEM) and Steve Hilton (REP). Write-in votes are not in the SOS county tables used here.

## County results in brief

- **Democratic registration share P fell in 57 of 58 counties** (statewide 46.87% to 44.96%). The Democratic registration *count* fell in 25 counties and rose statewide by +180,841; total registration rose +1,333,316.
- **The Democratic share of ballots (S) rose in 57 of 58 counties.** County ΔS ranges from −1.19\* (San Francisco) to +15.65\* (Colusa), median +6.75\*.
- **ΔG is positive in 57 counties and negative in 1** (San Francisco). County median +8.08\*; range −0.34\* (San Francisco) to +16.75\* (Colusa). Statewide ΔG = +8.45\*: S rose +6.54\* points and P fell 1.91 points.
- **Ceiling counties** (five largest ΔG): Colusa (+16.75\*), Merced (+16.69\*), Tulare (+15.44\*), Kings (+15.10\*), Kern (+15.07\*). **Floor counties** (most Republican baseline, five lowest 2022 P): Lassen (17.04%), Modoc (20.32%), Shasta (22.70%), Tehama (23.60%), Calaveras (26.51%). No county is in both groups. See [Floor and Ceiling Counties](Floor-and-Ceiling).
- **Residual step:** the 25 counties whose Democratic registration count fell run it. Residuals range from +3.02\* (Calaveras) to +12.75\* (Kings), median +6.09\*. The other 33 counties (including Los Angeles, San Diego and Orange) gained or kept Democratic registrants and are non-loss counties.
- **Solved backward (hypothesis):** implied extra votes sum to +876,786\* across the 58 counties (+877,683\* on pooled statewide numbers); Los Angeles accounts for +180,569\*. See [Bottom-Up Reverse Math](Reverse-Math).
- **California fitted equation (Locked page):** ΔG = +6.09 + 1.53 × (Democratic registration-share drop, points), R² 0.13. See [Locked California Formula](Locked-California-Formula#california-fitted-equation-final).
- **Over-ballot check:** in both years, no county has more ballots cast than registered voters on the 15-day report, none has more ballots than eligible residents, none has more registered voters than eligible residents, and none has Democratic + Republican governor votes above ballots cast. The tightest margin is Alpine (4 ballots without a governor vote in 2022, 6 in 2026\*). **No over-ballot flags.**

## Verification: two independent passes over the raw SOS files

- **Pass A** read structured files with structured parsers: the 2022 Statement of Vote governor table (`19-governor.xlsx`), the SOV Voter Participation Statistics by County PDF (word geometry with pdfplumber), the 2026 results site's own data API JSON (governor by county; County Reporting Status), and the 15-day Report of Registration `county.xlsx` for each year.
- **Pass B** used separate code on different artifacts, text and regex only: the SOV governor **PDF**, the participation PDF as plain text, the **rendered** 2026 results pages a reader sees (each county's governor page and the County Reporting Status table), and the Report of Registration **PDFs**.
- **Result:** 1,160 figure comparisons (58 counties × 20 figures). **1,160 matched, 0 mismatched.** Every statewide sum matched the SOS's own published statewide total (14 of 14), and the fitted equation and every county's inputs to it agreed in both passes (122 checks).
- **Every number on these pages** was recomputed from the raw files through both passes and matched as displayed (see `verification/wiki_number_check.csv`). **Every cell of the county PDF** (1,180 cells) was recomputed from the raw files and matched the printed value (1,180 of 1,180).

## Read this before using the numbers

- **2026 is UNOFFICIAL and incomplete.** Ballots were still being processed when these figures were pulled. Every 2026 figure carries an asterisk and will change before certification.
- **Registration date.** P uses the 15-day Report of Registration, the SOS's close-of-registration snapshot for each general election. California has same-day (conditional) voter registration, so people who registered after the 15-day report could still vote; the 15-day count is a baseline, not the final roll.
- **Ballots cast** is the county's total ballots cast in the election (SOV "Total Voters" in 2022; "Ballots Cast" on the County Reporting Status page in 2026\*), not governor votes. Ballots without a governor vote stay in the denominator of S.
- **No other state's constant is used.** All fitted values on these pages come from California's own counties.

---
**Related:** [Bottom-Up Reverse Math](Reverse-Math) · [Locked California Formula](Locked-California-Formula) · [Floor and Ceiling Counties](Floor-and-Ceiling) · [Graphs](Graphs) · [California County PDF Information](California-County-PDF-Information) · [Cedar County Audit (Nebraska)](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit)
