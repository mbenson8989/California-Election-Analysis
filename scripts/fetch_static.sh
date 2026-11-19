#!/bin/bash
# Download CA SOS static source files (Statement of Vote 2022, Report of Registration 15-day 2022 & 2026, 2026 results API JSON) with a fetch log.
set -e
R=/workspace/california-elections/raw
get(){ d=$1; u=$2; f=$d/$(basename "$u"); [ -n "$3" ] && f=$d/$3; code=$(curl -sL -A 'Mozilla/5.0' -o "$f" -w '%{http_code}' "$u"); echo "{\"url\":\"$u\",\"file\":\"$(basename $f)\",\"status\":$code,\"bytes\":$(stat -c%s "$f"),\"sha256\":\"$(sha256sum "$f"|cut -c1-64)\",\"fetched\":\"$(date -Iseconds)\"}," >> $d/fetch_log.jsonl; echo "$code $f"; }
S=https://elections.cdn.sos.ca.gov/sov/2022-general/sov
for f in 19-governor.xlsx 19-governor.pdf 03-voter-participation-stats-by-county.pdf 02-county-voter-reg-stats-by-county.pdf 06-summary.xlsx 06-summary.pdf csv-candidates.xlsx sov-certificate.pdf; do get $R/2022 $S/$f; done
get $R/2022 https://elections.cdn.sos.ca.gov/sov/2022-general/ssov/governor-summary.xlsx
for y in 2022 2026; do b=https://elections.cdn.sos.ca.gov/ror/15day-general-2022; [ $y = 2026 ] && b=https://elections.cdn.sos.ca.gov/ror/15day-gen-2026
  for f in county.xlsx county.pdf; do get $R/registration $b/$f ROR_15day_general_${y}_$f; done; done
curl -sL -A 'Mozilla/5.0' https://www.sos.ca.gov/elections/report-registration/15day-general-2022 -o $R/registration/sos_ror_page_15day-general-2022.html
curl -sL -A 'Mozilla/5.0' https://www.sos.ca.gov/elections/report-registration/15day-general-2026 -o $R/registration/sos_ror_page_15day-general-2026.html
curl -sL -A 'Mozilla/5.0' https://www.sos.ca.gov/elections/prior-elections/statewide-election-results/general-election-nov-8-2022/statement-vote -o $R/2022/sos_sov_page_2022-general.html
