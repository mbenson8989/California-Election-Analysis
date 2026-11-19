"""PASS A (structured parsers). California governor 2022 vs 2026, all 58 counties.
 2022 governor votes : CA SOS 2022 Statement of Vote (certified Dec 16, 2022), 19-governor.xlsx (openpyxl)
 2022 ballots cast   : CA SOS 2022 SOV 'Voter Participation Statistics by County' PDF, Total Voters column (pdfplumber words)
 2026 votes + ballots: CA SOS results-site data API JSON (api.sos.ca.gov/returns/governor/county/<slug>; maps/status/gubernatorial-general)
 Registration        : CA SOS 15-day Report of Registration (close of registration) county.xlsx, 2022 and 2026 (openpyxl)
Outputs verification/passA_counties.csv and passA_statewide.json"""
import json, csv, glob, os, re, openpyxl, pdfplumber, numpy as np
W='/workspace/california-elections/'; R=W+'raw/'; V=W+'verification/'
SL=[l.strip() for l in open(R+'2026/county_slugs.txt') if l.strip()]
CO=[' '.join(w.capitalize() for w in s.split('-')) for s in SL]; CO=[c.replace('San Luis Obispo','San Luis Obispo') for c in CO]; assert len(CO)==58
num=lambda s:int(str(s).replace(',','').strip())
rows={c:{'county':c} for c in CO}; SW={}
# ---------- 2022 governor votes (SOV xlsx) ----------
ws=openpyxl.load_workbook(R+'2022/19-governor.xlsx',data_only=True).active; X=list(ws.iter_rows(values_only=True))
assert X[1][1]=='DEM' and X[1][2]=='REP' and len([v for v in X[1] if v])==2, X[1]
for r in X[2:]:
    if r[0] in CO: rows[r[0]]['dem_2022']=int(r[1]); rows[r[0]]['rep_2022']=int(r[2]); rows[r[0]]['other_2022']=0
    if r[0]=='State Totals': SW['2022_gov_state_totals']=dict(dem=int(r[1]),rep=int(r[2]))
# ---------- 2022 ballots cast (SOV voter participation PDF, pdfplumber words grouped by line) ----------
with pdfplumber.open(R+'2022/03-voter-participation-stats-by-county.pdf') as p:
    for pg in p.pages:
        lines=[]   # cluster words into text lines: same line if top within 3 pt
        for w in sorted(pg.extract_words(),key=lambda w:w['top']):
            if lines and abs(w['top']-lines[-1][0])<=3: lines[-1][1].append(w)
            else: lines.append((w['top'],[w]))
        for _,lw in lines:
            ws_=sorted(lw,key=lambda w:w['x0']); toks=[w['text'] for w in ws_]
            nums=[t for t in toks if re.fullmatch(r'[\d,]+(\*\*)?',t)]; name=' '.join(t for t in toks if not re.fullmatch(r'[\d,.%*]+',t)).replace('*','').strip()
            if name in CO or name=='State Total':
                v=[num(t.replace('*','')) for t in nums]   # precincts, eligible, registered, precinct voters, VBM voters, total voters
                assert len(v)==6 and v[3]+v[4]==v[5],(name,v)
                if name=='State Total': SW['2022_participation_state_total']=dict(eligible=v[1],registered=v[2],total_voters=v[5])
                else: rows[name]['ballots_2022']=v[5]; rows[name]['reg_elec_2022']=v[2]
# ---------- 2026 (results-site API JSON) ----------
D=R+'2026/sos_api/'
st=json.load(open(D+'returns_maps_status_gubernatorial-general.json'))
for s,c in zip(SL,CO):
    e=st[s.replace('-','')] if s.replace('-','') in st else st[s]
    assert e['countyName']==c,(e['countyName'],c)
    rows[c]['ballots_2026']=num(e['voterTurnout']); rows[c]['reg_elec_2026']=num(e['totalRegisteredVoters']); rows[c]['report_2026']=e['timestamp']+' type '+e['reportType']
    g=json.load(open(D+f'returns_governor_county_{s}.json'))
    cty=[x for x in g if x['raceTitle']==f'Governor - {c} County Results']; assert len(cty)==1,c
    d=[x for x in cty[0]['candidates'] if x['Party']=='Dem']; r_=[x for x in cty[0]['candidates'] if x['Party']=='Rep']; assert len(d)==1 and len(r_)==1 and len(cty[0]['candidates'])==2
    rows[c]['dem_2026']=num(d[0]['Votes']); rows[c]['rep_2026']=num(r_[0]['Votes']); rows[c]['other_2026']=0
    swr=[x for x in g if x['raceTitle']=='Governor - Statewide Results'][0]
    SW.setdefault('2026_gov_statewide_records',{})[s]=dict(ReportingTime=swr['ReportingTime'],**{x['Party']:num(x['Votes']) for x in swr['candidates']})
SW['2026_status_keys']=sorted(st.keys()); SW['2026_status_statewide']={k:st['statewide'][k] for k in ('voterTurnout','totalRegisteredVoters','reportType','timestamp')}
sws=[v for v in SW['2026_gov_statewide_records'].values()]; assert all(v==sws[0] for v in sws),'statewide record changed while the 58 county files were fetched'
SW['2026_gov']=sws[0]
for r in rows.values():
    for y in ('2022','2026'): r[f'govtotal_{y}']=r[f'dem_{y}']+r[f'rep_{y}']+r[f'other_{y}']
# ---------- registration: 15-day Report of Registration county.xlsx ----------
def ror(f):
    ws=openpyxl.load_workbook(f,data_only=True).active; h=None; out={}
    for r in ws.iter_rows(values_only=True):
        if r[0]=='County': h=[re.sub(r'\s+',' ',str(x)).strip() for x in r]; continue
        if h and r[0] in CO+['State Total'] and isinstance(r[1],(int,float)):
            out[r[0]]=dict(elig=int(r[h.index('Eligible')]),tot=int(r[h.index('Total Registered')]),dem=int(r[h.index('Democratic')]),rep=int(r[h.index('Republican')]),
                           parties=int(sum(r[h.index(k)] for k in h[3:])))
    return out
for y in ('2022','2026'):
    T=ror(R+f'registration/ROR_15day_general_{y}_county.xlsx'); assert len(T)==59,len(T)
    for c in CO:
        assert T[c]['parties']==T[c]['tot'],(y,c,'party columns do not add to Total Registered')
        rows[c][f'regdem_{y}']=T[c]['dem']; rows[c][f'regrep_{y}']=T[c]['rep']; rows[c][f'regtot_{y}']=T[c]['tot']; rows[c][f'eligible_{y}']=T[c]['elig']
    SW[f'ror_{y}_state_total']=T['State Total']
F=['county','reg_elec_2022','ballots_2022','dem_2022','rep_2022','other_2022','govtotal_2022','regdem_2022','regrep_2022','regtot_2022','eligible_2022',
   'reg_elec_2026','ballots_2026','dem_2026','rep_2026','other_2026','govtotal_2026','regdem_2026','regrep_2026','regtot_2026','eligible_2026']
for c in CO: assert all(k in rows[c] for k in F),(c,[k for k in F if k not in rows[c]])
with open(V+'passA_counties.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=F,extrasaction='ignore'); w.writeheader(); [w.writerow(rows[c]) for c in CO]
json.dump({c:rows[c]['report_2026'] for c in CO},open(V+'passA_2026_county_report_times.json','w'),indent=1)
S=lambda k:sum(rows[c][k] for c in CO)
chk={'2022_dem':S('dem_2022')==SW['2022_gov_state_totals']['dem'],'2022_rep':S('rep_2022')==SW['2022_gov_state_totals']['rep'],
     '2022_ballots':S('ballots_2022')==SW['2022_participation_state_total']['total_voters'],'2022_reg_elec':S('reg_elec_2022')==SW['2022_participation_state_total']['registered'],
     '2026_dem':S('dem_2026')==SW['2026_gov']['Dem'],'2026_ballots':S('ballots_2026')==num(SW['2026_status_statewide']['voterTurnout']),'2026_reg_elec':S('reg_elec_2026')==num(SW['2026_status_statewide']['totalRegisteredVoters']),'2026_rep':S('rep_2026')==SW['2026_gov']['Rep']}
for y in ('2022','2026'):
    for k,kk in (('regdem','dem'),('regrep','rep'),('regtot','tot'),('eligible','elig')): chk[f'ror{y}_{k}']=S(f'{k}_{y}')==SW[f'ror_{y}_state_total'][kk]
SW['sums']={k:S(k) for k in F[1:]}
json.dump(dict(statewide=SW,county_sum_equals_file_total=chk),open(V+'passA_statewide.json','w'),indent=1)
print(json.dumps(chk)); print(len(rows),'counties x',len(F)-1,'figures'); assert all(chk.values())
# ---------- statewide fitted equation (Locked page): dG = const + mult * drop, drop = P2022 - P2026 (points), OLS over 58 counties (numpy lstsq) ----------
P22=np.array([100*rows[c]['regdem_2022']/rows[c]['regtot_2022'] for c in CO]); P26=np.array([100*rows[c]['regdem_2026']/rows[c]['regtot_2026'] for c in CO])
S22=np.array([100*rows[c]['dem_2022']/rows[c]['ballots_2022'] for c in CO]); S26=np.array([100*rows[c]['dem_2026']/rows[c]['ballots_2026'] for c in CO])
dG=(S26-P26)-(S22-P22); drop=P22-P26; X=np.c_[np.ones(len(CO)),drop]
beta,_,_,_=np.linalg.lstsq(X,dG,rcond=None); res=dG-X@beta; s2=res@res/(len(CO)-2); cov=s2*np.linalg.inv(X.T@X)
fitA=dict(n=len(CO),const=float(beta[0]),mult=float(beta[1]),const_se=float(np.sqrt(cov[0,0])),mult_se=float(np.sqrt(cov[1,1])),r2=float(1-res@res/np.sum((dG-dG.mean())**2)),
          by_county={c:dict(drop=float(d),dG=float(g)) for c,d,g in zip(CO,drop,dG)})
json.dump(fitA,open(V+'passA_fitted_equation.json','w'),indent=1); print('fitted equation A',{k:fitA[k] for k in ('const','mult','const_se','mult_se','r2')})
