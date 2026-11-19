"""Independent cell-by-cell check of the 58-county PDF against the RAW SOS files.
1. Re-parses the raw files twice, from scratch, by re-running the two independent parsers (pass_a.py: xlsx/pdfplumber/API JSON;
   pass_b.py: pdftotext/regex/rendered pages). Neither reads the PDF, the xlsx, or any analysis output.
2. Recomputes every displayed cell from each pass's counts with exact rational arithmetic (fractions), rounded half-up to the
   number of decimals the PDF shows (the PDF is rendered by LibreOffice, which rounds half away from zero).
3. Reads the values actually printed in the PDF (pdftotext -layout) and compares text to text.
4. Every other number token in the PDF text (dates, page numbers, years in headers) must be accounted for; anything else is untraced.
Writes verification/pdf_cell_check.csv (county, sheet, column, pdf, passA recompute, passB recompute, match) and pdf_cell_check_summary.json.
Exit 1 (build NOT publishable) on any mismatch or untraced token."""
import subprocess, csv, json, re, sys
from fractions import Fraction as Fr
from decimal import Decimal, ROUND_HALF_UP
W='/workspace/california-elections/'; V=W+'verification/'; PDF=W+'repo/California_58_County_Democratic_Registration_and_Vote_Change.pdf'
for s in ('pass_a.py','pass_b.py'): subprocess.run(['python3',W+'scripts/'+s],check=True,capture_output=True)
def load(p): return {r['county']:{k:int(v) for k,v in r.items() if k!='county'} for r in csv.DictReader(open(p))}
PA,PB=load(V+'passA_counties.csv'),load(V+'passB_counties.csv')
def tot(P): return {k:sum(P[c][k] for c in P) for k in next(iter(P.values()))}
PA['Statewide total']=tot({c:v for c,v in PA.items()}); PB['Statewide total']=tot({c:v for c,v in PB.items() if c!='Statewide total'})
def rnd(fr,d): return Decimal(fr.numerator)/Decimal(fr.denominator) if False else (Decimal(fr.numerator)/Decimal(fr.denominator)).quantize(Decimal(1).scaleb(-d),rounding=ROUND_HALF_UP)
def fint(n,sign=False): return ('+' if sign and n>0 else '')+f'{n:,}' if n>=0 else '-'+f'{-n:,}'
def fpct(fr,d=1,sign=False):
    # sign follows the UNROUNDED value, exactly as the spreadsheet format '+0.0%;-0.0%;0.0%' does (e.g. +5/109,843 shows '+0.0%')
    q=rnd(abs(fr)*100,d); s=f'{q:.{d}f}%'
    if fr<0: return '-'+s
    return ('+' if sign and fr>0 else '')+s
def fpts(fr,d=2):
    q=rnd(abs(fr),d); s=f'{q:.{d}f}'
    return '-'+s if fr<0 else ('+'+s if fr>0 else s)
def cells1(r):   # sheet 'Registration and Votes': 13 displayed cells after the county name
    return [('Dem Reg Share 2026 %',fpct(Fr(r['regdem_2026'],r['regtot_2026']))),('Dem Reg 2022',fint(r['regdem_2022'])),('Dem Reg 2026',fint(r['regdem_2026'])),
            ('Reg Change #',fint(r['regdem_2026']-r['regdem_2022'],True)),('Reg Change %',fpct(Fr(r['regdem_2026']-r['regdem_2022'],r['regdem_2022']),1,True)),
            ('Dem Gov Votes 2022',fint(r['dem_2022'])),('Dem Gov Votes 2026*',fint(r['dem_2026'])),('Vote Change #',fint(r['dem_2026']-r['dem_2022'],True)),
            ('Vote Change %',fpct(Fr(r['dem_2026']-r['dem_2022'],r['dem_2022']),1,True)),('Total Ballots 2022',fint(r['ballots_2022'])),('Total Ballots 2026*',fint(r['ballots_2026'])),
            ('Ballot Change #',fint(r['ballots_2026']-r['ballots_2022'],True)),('Ballot Change %',fpct(Fr(r['ballots_2026']-r['ballots_2022'],r['ballots_2022']),1,True))]
def cells2(r):   # sheet 'Dem Vote Share': 7 displayed cells
    s22=Fr(r['dem_2022'],r['ballots_2022']); s26=Fr(r['dem_2026'],r['ballots_2026'])
    return [('Dem Share of Ballots 2022 %',fpct(s22)),('Dem Share of Ballots 2026* %',fpct(s26)),('Change (pts)',fpts((s26-s22)*100)),
            ('Dem Share of Registration 2022 %',fpct(Fr(r['regdem_2022'],r['regtot_2022']))),('Total Registered 2022',fint(r['regtot_2022'])),
            ('Dem Share of Registration 2026 %',fpct(Fr(r['regdem_2026'],r['regtot_2026']))),('Total Registered 2026',fint(r['regtot_2026']))]
T=subprocess.run(['pdftotext','-layout',PDF,'-'],capture_output=True,text=True,check=True).stdout
NAMES=sorted(PA,key=len,reverse=True); TOK=re.compile(r'^[+-]?[\d,]+(?:\.\d+)?%?$')
rows=[]; seen={1:[],2:[]}; untraced=[]; other_tokens=[]
for ln,l in enumerate(T.split('\n'),1):
    st=l.strip(); name=next((n for n in NAMES if st.startswith(n+' ')),None)
    vals=st[len(name):].split() if name else []
    if name and vals and all(TOK.match(v) for v in vals) and len(vals) in (13,7):
        sheet=1 if len(vals)==13 else 2; seen[sheet].append(name)
        exp_a=(cells1 if sheet==1 else cells2)(PA[name]); exp_b=(cells1 if sheet==1 else cells2)(PB[name])
        for (col,a),(_,b),pv in zip(exp_a,exp_b,vals):
            rows.append(dict(county=name,sheet='Registration and Votes' if sheet==1 else 'Dem Vote Share',column=col,pdf_value=pv,recomputed_passA=a,recomputed_passB=b,match=(pv==a==b)))
        continue
    # every other number in the text must be a known non-data token
    for m in re.finditer(r'(?<![\w.])[+-]?\d[\d,]*(?:\.\d+)?%?',l):
        t=m.group(0); ctx=l[max(0,m.start()-25):m.end()+12]
        ok=(re.search(r'Page \d+ of \d+',ctx) is not None) or t in ('2022','2026','58') or re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December|Oct) \d{1,2}(, \d{4})?',ctx) is not None or re.search(r'\d{1,2}:\d{2} [ap]\.m\.',ctx) is not None or t=='15'
        other_tokens.append(dict(line=ln,token=t,context=ctx.strip(),classified='label/date/page' if ok else 'UNTRACED'))
        if not ok: untraced.append(dict(line=ln,token=t,context=ctx.strip()))
# page numbering and the label '58' must themselves be right
pages=int(subprocess.run(['pdfinfo',PDF],capture_output=True,text=True).stdout.split('Pages:')[1].split()[0])
pg=re.findall(r'Page (\d+) of (\d+)',T); pages_ok=[int(a) for a,b in pg]==list(range(1,pages+1)) and all(int(b)==pages for a,b in pg)
order_expected=sorted([c for c in PA if c!='Statewide total'],key=lambda c:(-Fr(PA[c]['regdem_2026'],PA[c]['regtot_2026']),c))
order_ok={s:[c for c in seen[s] if c!='Statewide total']==order_expected for s in (1,2)}
complete={s:sorted(seen[s])==sorted(PA) for s in (1,2)}
mism=[r for r in rows if not r['match']]
with open(V+'pdf_cell_check.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
S=dict(pdf=PDF.split('/')[-1],pages=pages,page_numbers_ok=pages_ok,rows_found={'Registration and Votes':len(seen[1]),'Dem Vote Share':len(seen[2])},rows_complete=complete,sort_order_ok=order_ok,
       cells_checked=len(rows),cells_matched=len(rows)-len(mism),mismatches=mism,other_number_tokens=len(other_tokens),untraced_tokens=untraced,
       statewide_row={r['column']:r['pdf_value'] for r in rows if r['county']=='Statewide total' and r['sheet']=='Registration and Votes'},
       statewide_row_sheet2={r['column']:r['pdf_value'] for r in rows if r['county']=='Statewide total' and r['sheet']=='Dem Vote Share'},
       method='raw files re-parsed by pass_a.py and pass_b.py (independent parsers); exact fractions, half-up rounding to displayed decimals; PDF text via pdftotext -layout')
S['PUBLISHABLE']=not mism and not untraced and pages_ok and all(order_ok.values()) and all(complete.values()) and len(rows)==59*13+59*7
json.dump(S,open(V+'pdf_cell_check_summary.json','w'),indent=1)
json.dump(other_tokens,open(V+'pdf_other_number_tokens.json','w'),indent=1)
print(json.dumps({k:S[k] for k in ('cells_checked','cells_matched','rows_found','rows_complete','sort_order_ok','page_numbers_ok','other_number_tokens','PUBLISHABLE')}))
for m in mism[:50]: print('MISMATCH',m)
for u in untraced: print('UNTRACED',u)
sys.exit(0 if S['PUBLISHABLE'] else 1)
