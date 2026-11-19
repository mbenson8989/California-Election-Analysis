> **\*2026 figures are UNOFFICIAL.** The California Secretary of State (SOS) results site, electionresults.sos.ca.gov, labels the November 3, 2026 general election results "Unofficial" (semi-final unofficial results with county updates; statewide figures as of November 19, 2026, 1:59 p.m. Pacific; pulled November 19, 2026). Counties are still in the canvass: the SOS Unprocessed Ballots Report (as of 11/18/2026 5:33 p.m.) estimated 100,313 ballots statewide still to process, plus 96,238 ballots left to cure. Counties must report final official results by December 4, 2026, and the SOS certifies on December 11, 2026, so these pages need a re-run after certification. 2022 figures are the certified Statement of Vote (certificate dated the 16th day of December, 2022). **P** = Democratic share of registered voters in the SOS 15-day Report of Registration (close of registration: as of October 24, 2022 and as of October 19, 2026). Governor race only. Votes are votes for the Democratic candidate, not a count of registered Democrats who voted. These pages measure a pattern; they make no claim about intent, fraud or cause.

**[Download: California_58_County_Democratic_Registration_and_Vote_Change.pdf](https://github.com/mbenson8989/California-Election-Analysis/raw/main/California_58_County_Democratic_Registration_and_Vote_Change.pdf)** (4 landscape pages) · [Excel version](https://github.com/mbenson8989/California-Election-Analysis/raw/main/California_58_County_Democratic_Registration_and_Vote_Change.xlsx)

All 58 counties, sorted by 2026 Democratic share of registration (highest first, San Francisco first): Democratic registration on the 15-day reports for 2022 and 2026, Democratic governor votes for 2022 and 2026\*, and total ballots cast for 2022 and 2026\*, each with the change as a number and a percent, plus a statewide totals row. The second table shows the Democratic share of ballots and of registration. Counties where Democratic registration rose are shaded blue; no county's Democratic governor vote fell.

## Columns

| Column | Meaning |
|---|---|
| County | County name |
| Dem Reg Share 2026 % | Democratic registered voters ÷ Total Registered, 15-day Report of Registration as of October 19, 2026 (the sort key) |
| Dem Reg 2022 (Oct 24) / Dem Reg 2026 (Oct 19) | Democratic registered voters on the 15-day Report of Registration for each election |
| Reg Change # / Reg Change % | Dem Reg 2026 minus Dem Reg 2022, and that change as a percent of Dem Reg 2022 |
| Dem Gov Votes 2022 / 2026\* | Votes for the Democratic governor candidate (2022 Statement of Vote; 2026\* SOS unofficial results) |
| Vote Change # / Vote Change % (on 2022 base) | Dem Gov Votes 2026\* minus 2022, and that change as a percent of the 2022 votes |
| Total Ballots 2022 / 2026\* | Total ballots cast in the county (all contests), not governor votes |
| Ballot Change # / Ballot Change % | Total Ballots 2026\* minus 2022, and that change as a percent of 2022 |
| Second table | Dem share of ballots (Dem governor votes ÷ total ballots) for each year, its change in points, Dem share of registration for each year, and Total Registered |

## Statewide totals row

| Column | Value |
|---|---|
| Dem Reg Share 2026 % | 45.0% |
| Dem Reg 2022 | 10,283,258 |
| Dem Reg 2026 | 10,464,099 |
| Reg Change # | +180,841 |
| Reg Change % | +1.8% |
| Dem Gov Votes 2022 | 6,470,104 |
| Dem Gov Votes 2026\* | 8,669,071 |
| Vote Change # | +2,198,967 |
| Vote Change % | +34.0% |
| Total Ballots 2022 | 11,146,620 |
| Total Ballots 2026\* | 13,422,913 |
| Ballot Change # | +2,276,293 |
| Ballot Change % | +20.4% |

## How the PDF was checked

Every cell was recomputed from the raw SOS files through two independent parsers (pass A and pass B), with exact arithmetic rounded to the decimals the PDF prints, and compared with the text actually printed in the PDF: **1,180 of 1,180 cells matched, 0 mismatched.** The sort order, page numbers and row count were checked too. See `verification/pdf_cell_check.csv` and `verification/pdf_cell_check_summary.json` in the [repository](https://github.com/mbenson8989/California-Election-Analysis).

---
**Related:** [Home](Home) · [Bottom-Up Reverse Math](Reverse-Math) · [Locked California Formula](Locked-California-Formula) · [Floor and Ceiling Counties](Floor-and-Ceiling) · [Graphs](Graphs) · [Cedar County Audit (Nebraska)](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit)
