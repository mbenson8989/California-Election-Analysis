"""Compare pass A vs pass B figure by figure (58 counties x 20 figures), plus statewide sums vs the SOS's own published totals
(transcribed from the SOS documents/pages listed in SRC, not computed from either pass).
Analysis figures (everything any calculation or check on the wiki uses) must match with ZERO mismatches.
reg_elec_YYYY (the 'registered voters' figure printed beside the turnout: SOV participation table 2022; County Reporting Status 2026)
is shown for reference only; P uses the 15-day Report of Registration."""
import csv, json, sys
V='/workspace/california-elections/verification/'
A={r['county']:r for r in csv.DictReader(open(V+'passA_counties.csv'))}; B={r['county']:r for r in csv.DictReader(open(V+'passB_counties.csv'))}
assert set(A)==set(B) and len(A)==58
F=[k for k in B['Alameda'] if k!='county']; REF=['reg_elec_2022','reg_elec_2026']; USED=[k for k in F if k not in REF]
rows=[]; mm=[]; mmu=[]
for c in A:
    for k in F:
        a,b=int(A[c][k]),int(B[c][k]); ok=a==b
        rows.append(dict(county=c,field=k,used_in_analysis=k in USED,passA=a,passB=b,match=ok))
        if not ok: (mmu if k in USED else mm).append(dict(county=c,field=k,passA=a,passB=b))
with open(V+'compare_A_B_figure_by_figure.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
S=lambda D,k:sum(int(D[c][k]) for c in D)
SOS={'dem_2022':6470104,'rep_2022':4462914,'ballots_2022':11146620,'regdem_2022':10283258,'regrep_2022':5232094,'regtot_2022':21940274,'eligible_2022':26876800,
     'dem_2026':8669071,'rep_2026':4542458,'ballots_2026':13422913,'regdem_2026':10464099,'regrep_2026':5746921,'regtot_2026':23273590,'eligible_2026':27168679}
SRC={'2022':'State Totals row of the 2022 SOV governor table (19-governor.pdf/.xlsx; SOV certified Dec 16, 2022); State Total row of SOV Voter Participation Statistics by County (Total Voters)',
     '2026':'Governor statewide card (as of Nov 19, 2026, 1:59 p.m. PT) and Statewide row of County Reporting Status (Ballots Cast) on electionresults.sos.ca.gov, UNOFFICIAL',
     'reg':'State Total row of each 15-day Report of Registration (as of Oct 24, 2022 and Oct 19, 2026)'}
st=[dict(item=k,SOS_published=v,passA_sum=S(A,k),passB_sum=S(B,k),ok=S(A,k)==v==S(B,k)) for k,v in SOS.items()]
rep=dict(counties=len(A),figures_per_county=len(F),comparisons=len(rows),matched=len(rows)-len(mm)-len(mmu),mismatches_total=len(mm)+len(mmu),
         analysis_figures_per_county=len(USED),analysis_comparisons=len(A)*len(USED),analysis_mismatches=mmu,reference_only_mismatches=mm,statewide_checks=st,statewide_sources=SRC)
FA=json.load(open(V+'passA_fitted_equation.json')); FB=json.load(open(V+'passB_fitted_equation.json'))
fe=[dict(item=k,passA=FA[k],passB=FB[k],ok=abs(FA[k]-FB[k])<1e-9) for k in ('n','const','mult','const_se','mult_se','r2')]
fe+=[dict(item=f'{c} {k}',passA=FA['by_county'][c][k],passB=FB['by_county'][c][k],ok=abs(FA['by_county'][c][k]-FB['by_county'][c][k])<1e-9) for c in FA['by_county'] for k in ('drop','dG')]
rep['fitted_equation_checks']=dict(n=len(fe),mismatches=[x for x in fe if not x['ok']],tolerance=1e-9)
rep['CLEAN']=not mmu and all(x['ok'] for x in st) and all(x['ok'] for x in fe)
json.dump(rep,open(V+'compare_report.json','w'),indent=1)
print(json.dumps({k:rep[k] for k in ('fitted_equation_checks','comparisons','matched','mismatches_total','analysis_comparisons','analysis_mismatches','reference_only_mismatches','CLEAN')}))
[print(x) for x in st if not x['ok']]
sys.exit(0 if rep['CLEAN'] else 1)
