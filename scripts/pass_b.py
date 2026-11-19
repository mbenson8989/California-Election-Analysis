"""PASS B: independent code on DIFFERENT artifacts from pass A where the SOS publishes one. Text/regex only (no openpyxl/pdfplumber/json of the results API).
 2022 governor votes : the Statement of Vote governor PDF (19-governor.pdf), `pdftotext -layout` + regex (pass A read the .xlsx)
 2022 ballots cast   : SOV Voter Participation Statistics by County PDF, `pdftotext -layout` + regex (pass A: pdfplumber word geometry;
                       the SOS publishes this table only as a PDF)
 2026 votes + ballots: RENDERED results pages captured from electionresults.sos.ca.gov as visible text: each county's Governor page
                       and the County Reporting Status table (pass A read the site's data API JSON)
 Registration        : `pdftotext -layout` of the 15-day Report of Registration county.pdf (pass A read county.xlsx)
Outputs verification/passB_counties.csv, passB_sources.json, passB_fitted_equation.json"""
import subprocess, re, csv, json, os
W='/workspace/california-elections/'; R=W+'raw/'; V=W+'verification/'
SL=[l.strip() for l in open(R+'2026/county_slugs.txt') if l.strip()]
CO=['Alameda','Alpine','Amador','Butte','Calaveras','Colusa','Contra Costa','Del Norte','El Dorado','Fresno','Glenn','Humboldt','Imperial','Inyo','Kern','Kings','Lake','Lassen','Los Angeles','Madera','Marin','Mariposa','Mendocino','Merced','Modoc','Mono','Monterey','Napa','Nevada','Orange','Placer','Plumas','Riverside','Sacramento','San Benito','San Bernardino','San Diego','San Francisco','San Joaquin','San Luis Obispo','San Mateo','Santa Barbara','Santa Clara','Santa Cruz','Shasta','Sierra','Siskiyou','Solano','Sonoma','Stanislaus','Sutter','Tehama','Trinity','Tulare','Tuolumne','Ventura','Yolo','Yuba']
assert len(CO)==58 and len(SL)==58
NAME=r'(San Luis Obispo|[A-Z][a-z]+(?: [A-Z][a-z]+)?)'
N=re.compile(r'^\d{1,3}(?:,\d{3})*$')
def txt(pdf): return subprocess.run(['pdftotext','-layout',pdf,'-'],capture_output=True,text=True).stdout
def ints(s): return [int(t.replace(',','')) for t in s.replace('**','').split() if N.match(t.replace('**',''))]
B={c:{'county':c} for c in CO}; notes={}
# ---------- 2022 governor votes: SOV PDF ----------
L=txt(R+'2022/19-governor.pdf').split('\n')
assert any(re.search(r'\bDEM\s+REP\b',l) for l in L[:15])
for l in L:
    m=re.match(r'^'+NAME+r'\s+([\d,]+)\s+([\d,]+)\s*$',l.strip()) or re.match(r'^(State Totals)\s+([\d,]+)\s+([\d,]+)\s*$',l.strip())
    if m and (m.group(1) in CO or m.group(1)=='State Totals'):
        d,r=int(m.group(2).replace(',','')),int(m.group(3).replace(',',''))
        if m.group(1)=='State Totals': notes['2022_sov_governor_state_totals']=[d,r]
        else: assert 'dem_2022' not in B[m.group(1)]; B[m.group(1)].update(dem_2022=d,rep_2022=r,other_2022=0)
# ---------- 2022 ballots: SOV voter participation PDF ----------
for l in txt(R+'2022/03-voter-participation-stats-by-county.pdf').split('\n'):
    m=re.match(r'^'+NAME+r'\*?\s+(\d.*)$',l.strip())
    if m and m.group(1) in CO:
        v=ints(m.group(2)); assert len(v)==6 and v[3]+v[4]==v[5],(m.group(1),v)   # precincts, eligible, registered, precinct voters, VBM voters, total voters
        B[m.group(1)]['reg_elec_2022']=v[2]; B[m.group(1)]['ballots_2022']=v[5]
    if l.startswith('State Total'): notes['2022_participation_state_total_line']=ints(l)
# ---------- 2026: rendered county governor pages ----------
for s,c in zip(SL,CO):
    t=open(R+f'2026/rendered/gov_county_{s}.txt').read()
    assert f'Governor - {c} County Results' in t,(c,'wrong page')
    cand=re.findall(r'\t([^\t\n]+)\n\n\(Party Preference: (\w+)\)\n\t([\d,]+)\t\n([\d.]+)%\n\t([\d,]+)\t',t)
    assert len(cand)==2 and {x[1] for x in cand}=={'DEM','REP'},(c,cand)
    for nm,p,cv,_,sv in cand: B[c]['dem_2026' if p=='DEM' else 'rep_2026']=int(cv.replace(',',''))
    B[c]['other_2026']=0
    notes.setdefault('2026_rendered_county_as_of',{})[c]=re.search(r'reporting as of ([^\n]+?)\s*\n',t).group(1)
    notes.setdefault('2026_rendered_state_votes_on_county_pages',{})[c]={p:int(sv.replace(',','')) for nm,p,cv,_,sv in cand}
t=open(R+'2026/rendered/county_status.txt').read()
for c in CO+['Statewide']:
    m=re.search(r'\n'+re.escape(c)+r'\t[^\t]*\t[\d,]+\t([\d,]+)\t([\d,]+)\t',t); assert m,c
    if c=='Statewide': notes['2026_status_statewide_row']=dict(registered=int(m.group(1).replace(',','')),ballots=int(m.group(2).replace(',','')))
    else: B[c]['reg_elec_2026']=int(m.group(1).replace(',','')); B[c]['ballots_2026']=int(m.group(2).replace(',',''))
for c in CO:
    for y in ('2022','2026'): B[c][f'govtotal_{y}']=B[c][f'dem_{y}']+B[c][f'rep_{y}']+B[c][f'other_{y}']
# ---------- registration: ROR county.pdf text (first block of each county: Eligible, Total Registered, Democratic, Republican, ...) ----------
def ror(pdf):
    T=txt(pdf); out={}; date=re.search(r'Report of Registration as of (\w+ \d+, \d{4})',T).group(1)
    for l in T.split('\n'):
        m=re.match(r'^(State Total|'+NAME[1:-1]+r')\s+(\d.*)$',l.strip())
        if m and (m.group(1) in CO or m.group(1)=='State Total') and m.group(1) not in out:   # first occurrence = page with Eligible/Total/Dem/Rep columns
            v=ints(m.group(2)); assert len(v)==6,(pdf,l); out[m.group(1)]=dict(elig=v[0],tot=v[1],dem=v[2],rep=v[3])
    return date,out
for y in ('2022','2026'):
    hdr=txt(R+f'registration/ROR_15day_general_{y}_county.pdf').split('\n')[:8]
    assert re.search(r'Eligible\s+Registered\s+Democratic\s+Republican',' '.join(hdr)),hdr
    date,out=ror(R+f'registration/ROR_15day_general_{y}_county.pdf'); notes[f'ror_{y}_as_of']=date; notes[f'ror_{y}_state_total']=out['State Total']
    for c in CO: B[c].update({f'regdem_{y}':out[c]['dem'],f'regrep_{y}':out[c]['rep'],f'regtot_{y}':out[c]['tot'],f'eligible_{y}':out[c]['elig']})
F=['county','reg_elec_2022','ballots_2022','dem_2022','rep_2022','other_2022','govtotal_2022','regdem_2022','regrep_2022','regtot_2022','eligible_2022',
   'reg_elec_2026','ballots_2026','dem_2026','rep_2026','other_2026','govtotal_2026','regdem_2026','regrep_2026','regtot_2026','eligible_2026']
with open(V+'passB_counties.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=F); w.writeheader(); [w.writerow({k:B[c][k] for k in F}) for c in CO]
json.dump(notes,open(V+'passB_sources.json','w'),indent=1)
print('pass B ok',len(B),'counties x',len(F)-1)
# ---------- statewide fitted equation, computed independently in pure Python (closed-form simple regression) ----------
n=len(CO)
P22=[100*B[c]['regdem_2022']/B[c]['regtot_2022'] for c in CO]; P26=[100*B[c]['regdem_2026']/B[c]['regtot_2026'] for c in CO]
S22=[100*B[c]['dem_2022']/B[c]['ballots_2022'] for c in CO]; S26=[100*B[c]['dem_2026']/B[c]['ballots_2026'] for c in CO]
y=[(S26[i]-P26[i])-(S22[i]-P22[i]) for i in range(n)]; x=[P22[i]-P26[i] for i in range(n)]
mx=sum(x)/n; my=sum(y)/n; sxx=sum((a-mx)**2 for a in x); sxy=sum((a-mx)*(b-my) for a,b in zip(x,y)); syy=sum((b-my)**2 for b in y)
mult=sxy/sxx; const=my-mult*mx; sse=sum((b-const-mult*a)**2 for a,b in zip(x,y)); s2=sse/(n-2)
fitB=dict(n=n,const=const,mult=mult,const_se=(s2*(1/n+mx*mx/sxx))**0.5,mult_se=(s2/sxx)**0.5,r2=1-sse/syy,by_county={c:dict(drop=x[i],dG=y[i]) for i,c in enumerate(CO)})
json.dump(fitB,open(V+'passB_fitted_equation.json','w'),indent=1); print('fitted equation B',{k:fitB[k] for k in ('const','mult','const_se','mult_se','r2')})
