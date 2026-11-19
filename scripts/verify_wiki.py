"""Every number on every wiki page (and the repo README) must trace to BOTH independent raw-file recomputations.
1. Re-parse the raw SOS files from scratch with both independent parsers (pass_a.py, pass_b.py), re-run the A/B comparison and the PDF cell check.
2. registry.compute() recomputes every displayable quantity from each pass's table separately (no pandas/statsmodels, no analysis outputs).
3. For each number the page builder emitted (verification/wiki_number_manifest.json: page, key, format, displayed text), format the pass-A and
   pass-B recomputations the same way; the displayed text must equal both.
4. Scan every page for every number token. Each must be (a) one of the manifest numbers on that page, or (b) a date/time/label whose exact
   text is found in the raw source files, or (c) a fixed method label (years 2022/2026, '15-day', list numbering, the ×/÷ 100 of a percent,
   the 95% of a confidence interval). Anything else is UNTRACED.
Writes verification/wiki_number_check.csv (one row per number) and wiki_number_check_summary.json; exit 1 = HOLD."""
import subprocess, json, csv, re, sys, os, glob, collections
W='/workspace/california-elections/'; V=W+'verification/'; S=W+'scripts/'
sys.path.insert(0,S); import registry, fmt
for s in ('pass_a.py','pass_b.py'): subprocess.run(['python3',S+s],check=True,capture_output=True)
cp=subprocess.run(['python3',S+'compare_passes.py'],capture_output=True)
pc=subprocess.run(['python3',S+'check_pdf_cells.py'],capture_output=True)
A=registry.load(V+'passA_counties.csv'); B=registry.load(V+'passB_counties.csv'); pop=registry.census_pop(W+'raw/census/co-est2025-alldata.csv')
RA=registry.compute(A,pop); RB=registry.compute(B,pop); RA.update(registry.unprocessed('A')); RB.update(registry.unprocessed('B'))
# verification counts: recounted here from the fresh tables / fresh reports
C=json.load(open(V+'compare_report.json')); P=json.load(open(V+'pdf_cell_check_summary.json'))
nf=len(registry.FIELDS); eq=sum(A[c][k]==B[c][k] for c in A for k in registry.FIELDS)
for R_ in (RA,RB):
    R_.update({'cmp|comparisons':len(A)*nf,'cmp|matched':eq,'cmp|mismatches':len(A)*nf-eq,'cmp|analysis_comparisons':len(A)*(nf-2),'cmp|figures_per_county':nf,
               'cmp|statewide_checks':len(C['statewide_checks']),'cmp|statewide_ok':sum(x['ok'] for x in C['statewide_checks']),'cmp|fit_checks':C['fitted_equation_checks']['n'],
               'cmp|pdf_cells':P['cells_checked'],'cmp|pdf_matched':P['cells_matched'],'cmp|pdf_mismatches':len(P['mismatches']),'cmp|pdf_pages':P['pages']})
MAN=json.load(open(V+'wiki_number_manifest.json'))
rows=[]
for m in MAN:
    a=fmt.F(RA[m['key']],m['fmt']) if m['key'] in RA else 'MISSING'; b=fmt.F(RB[m['key']],m['fmt']) if m['key'] in RB else 'MISSING'
    rows.append(dict(page=m['page'],kind='data',token=m['text'],key=m['key'],format=m['fmt'],recomputed_passA=a,recomputed_passB=b,match=(m['text']==a==b),note='verification count' if m['key'].startswith('cmp|') else ''))
# raw corpus for dates/labels
def corpus():
    T=[]
    for f in glob.glob(W+'raw/**/*',recursive=True):
        if f.endswith('.pdf'): T.append(subprocess.run(['pdftotext','-layout',f,'-'],capture_output=True,text=True).stdout)
        elif f.endswith(('.txt','.json','.html')): T.append(open(f,errors='ignore').read())
    return re.sub(r'\s+',' ','\n'.join(T))
RAWTXT=corpus()
MONTH=r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
DATE=re.compile(MONTH+r' \d{1,2}, \d{4}(?:, \d{1,2}:\d{2} [ap]\.m\.)?|\d{1,2}th day of '+MONTH+r', \d{4}|\d{2}/\d{2}/\d{4} \d{1,2}:\d{2} [ap]\.m\.|\(Oct \d{1,2}\)')
LABEL=re.compile(r'15-day|Vintage 2025|[×÷] 100\b|95% interval')
TOK=re.compile(r'(?<![\w.\-/])[+−-]?\d[\d,]*(?:\.\d+)?%?')
pages={os.path.basename(f)[:-3]:open(f).read() for f in glob.glob(W+'wiki/*.md')}; pages['README']=open(W+'repo/README.md').read()
issues=[]
for pg,src in pages.items():
    t=re.sub(r'\]\([^)]*\)',']',src); t=re.sub(r'(?<!`)`[^`\n]+`(?!`)','',t); t=re.sub(r'https?://\S+','',t); t=re.sub(r'(?m)^\s*\d+\. ','',t)
    for d in DATE.finditer(t):
        txt=d.group(0); probe=txt.strip('()').replace('Oct ','October ')
        found=(probe in RAWTXT) or (txt.startswith('(Oct') and re.search(r'October '+probe.split()[1]+r', 20\d\d',RAWTXT) is not None)
        if not found and re.match(r'\d{2}/\d{2}/\d{4}',txt): found=txt in RAWTXT
        if not found and ' day of ' in txt: found=txt.replace('th day of','th day of') in RAWTXT
        if not found and re.match(MONTH+r' \d{1,2}, \d{4}$',txt):  # e.g. 'November 19, 2026' appears inside a longer raw timestamp
            found=txt in RAWTXT
        rows.append(dict(page=pg,kind='date/label',token=txt,key='raw-file text',format='',recomputed_passA=txt if found else 'NOT IN RAW FILES',recomputed_passB='',match=found,note='exact text searched in raw/'))
    t2=LABEL.sub(' ',DATE.sub(' ',t))
    toks=[x.group(0).rstrip(',') for x in TOK.finditer(t2)]
    toks=[x for x in toks if x not in ('2022','2026')]
    want=collections.Counter(m['text'] for m in MAN if m['page']==pg); have=collections.Counter(toks)
    for k,v in (have-want).items(): issues.append(dict(page=pg,token=k,count=v,problem='number on page not traced to any recomputed value'))
    for k,v in (want-have).items(): issues.append(dict(page=pg,token=k,count=v,problem='manifest number not found on page'))
mism=[r for r in rows if not r['match']]
with open(V+'wiki_number_check.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
# structural checks (as Nevada): banner/UNOFFICIAL on every page, Cedar link exact, fitted-equation section, sidebar order
CEDAR='https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit'
st=dict(unofficial_on_every_page={p:('UNOFFICIAL' in s) for p,s in pages.items()},cedar_link_on_every_page={p:(CEDAR in s) for p,s in pages.items() if p!='README'} | {'README':CEDAR in pages['README']},
        fitted_equation_section='## California fitted equation (final)' in pages['Locked-California-Formula'],
        sidebar_order=re.findall(r'\]\(([\w-]+)\)',pages['_Sidebar'])==['Home','Reverse-Math','Locked-California-Formula','Floor-and-Ceiling','Graphs','California-County-PDF-Information'],
        home_links_pdf_page='(California-County-PDF-Information)' in pages['Home'],
        pdf_raw_link='https://github.com/mbenson8989/California-Election-Analysis/raw/main/California_58_County_Democratic_Registration_and_Vote_Change.pdf' in pages['California-County-PDF-Information'],
        compare_passes_clean=cp.returncode==0,pdf_cell_check_publishable=pc.returncode==0)
ok_struct=all(v if isinstance(v,bool) else all(v.values()) for v in st.values())
SUM=dict(numbers_checked=len(rows),data_numbers=sum(r['kind']=='data' for r in rows),date_labels=sum(r['kind']!='data' for r in rows),matched=len(rows)-len(mism),mismatches=mism,untraced_or_missing=issues,
         per_page={p:dict(numbers=sum(r['page']==p for r in rows),mismatches=sum(r['page']==p and not r['match'] for r in rows)) for p in pages},structure=st)
SUM['STATUS']='PASS' if not mism and not issues and ok_struct else 'HOLD'
json.dump(SUM,open(V+'wiki_number_check_summary.json','w'),indent=1)
print(json.dumps({k:SUM[k] for k in ('numbers_checked','data_numbers','date_labels','matched','STATUS')}),json.dumps(st))
for m in mism[:60]: print('MISMATCH',m)
for i in issues[:80]: print('ISSUE',i)
sys.exit(0 if SUM['STATUS']=='PASS' else 1)
