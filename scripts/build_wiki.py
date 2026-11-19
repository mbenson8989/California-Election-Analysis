"""Build the California wiki pages + _Sidebar.md + repo README from the analysis outputs (analysis.py: pandas/statsmodels on the
pass-A table). EVERY data number is emitted through N(key,fmt), which records (page, key, format, displayed text) in
verification/wiki_number_manifest.json. verify_wiki.py then recomputes every key from the raw files twice (pass A and pass B
tables, registry.py) and requires the displayed text to match both, and requires every number token on every page to be
covered by the manifest or be a date/label it can find in the raw files.
Layout guards carried over from the Nevada build: no body H1 on wiki pages; _Sidebar in reading order; no 'A → B' pairs in
tables with 6+ columns; cell() escapes '|'; blank line between heading and image."""
import pandas as pd, numpy as np, json, os, sys
sys.path.insert(0,os.path.dirname(__file__)); from fmt import F as FMT, M
W='/workspace/california-elections/'; O=W+'repo/'; WK=W+'wiki/'; V=W+'verification/'
o=pd.read_pickle('/tmp/ca_o.pkl'); J=json.load(open(O+'data/CA_results_summary.json')); R=json.load(open(V+'compare_report.json'))
PC=json.load(open(V+'pdf_cell_check_summary.json')); assert PC['PUBLISHABLE'], 'PDF cell check failed: build is on HOLD'
FT=J['fits']; K=J['K']; PO=J['pooled']; TX=J['overballot']; NAR=J['narrow']; T=PO['totals']
sys.path.insert(0,W+'scripts'); import registry
UNP=registry.unprocessed('A')
REPO='https://github.com/mbenson8989/California-Election-Analysis'; BRANCH='main'; RAW=f'https://raw.githubusercontent.com/mbenson8989/California-Election-Analysis/{BRANCH}/'
PDFN='California_58_County_Democratic_Registration_and_Vote_Change.pdf'; XLSXN=PDFN.replace('.pdf','.xlsx'); PDFRAW=f'{REPO}/raw/{BRANCH}/{PDFN}'
CEDAR='https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit'; NEWIKI='https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki'
EQ_CONST=FT['dG_on_dP']['b']; EQ_MULT=-FT['dG_on_dP']['m']/100   # dG = b + m*(dP/100)  ->  dG = b + (-m/100)*drop
EQ_CONST_SE=FT['dG_on_dP']['b_se']; EQ_MULT_SE=FT['dG_on_dP']['m_se']/100; EQ_R2=FT['dG_on_dP']['r2']
# ---------------- value lookup (analysis outputs only) ----------------
def bv(key):
    a,b=key.split('|',1) if key.count('|')==1 else (key.split('|')[0],key.split('|',1)[1])
    if a=='State':
        m={'S22':PO['S22'],'S26':PO['S26'],'P22':PO['P22'],'P26':PO['P26'],'G22':PO['G22'],'G26':PO['G26'],'dG':PO['dG'],'dP':PO['dP'],'dS':PO['dS'],'drop':-PO['dP'],
           'residual_share':PO['dG']-abs(PO['dP']),'implied':PO['implied_extra_pooled'],'implied_sum':PO['implied_extra_sum'],'implied_sum_loss':PO['implied_extra_sum_loss'],
           'implied_sum_nonloss':PO['implied_extra_sum_nonloss'],'gapreg_sum':PO['gap_reg_scaled_sum']}
        if b in m: return m[b]
        if b in T: return T[b]
        dd={'dreg':('regdem_2022','regdem_2026'),'ddem':('dem_2022','dem_2026'),'dbal':('ballots_2022','ballots_2026'),'dregtot':('regtot_2022','regtot_2026'),'drep':('rep_2022','rep_2026')}
        k=b.replace('_pct','')
        if k in dd: x,y=dd[k]; return (T[y]-T[x])*(100/T[x] if b.endswith('_pct') else 1)
        if b.startswith('under_pct'): y='20'+b[-2:]; return 100*(T['ballots_'+y]-T['govtotal_'+y])/T['ballots_'+y]
        if b.startswith('turnout_reg'): y='20'+b[-2:]; return 100*T['ballots_'+y]/T['regtot_'+y]
        if b.startswith('margin_DR'): y='20'+b[-2:]; return T['ballots_'+y]-T['govtotal_'+y]
        raise KeyError(key)
    if a=='fit':
        if b=='cut': return 4/len(o)
        name,st=b.split('|')
        f=FT[name]
        m={'m':f['m'],'b':f['b'],'m_se':f['m_se'],'b_se':f['b_se'],'r2':f['r2'],'resid_se':f['resid_se'],'n':f['n'],'within1':100*f['within1'],'within2':100*f['within2'],'within3':100*f['within3'],
           'med_abs':f['med_abs'],'b_lo':f['b_ci'][0],'b_hi':f['b_ci'][1],'m_lo':f['m_ci'][0],'m_hi':f['m_ci'][1]}
        return m[st]
    if a=='eq':
        m={'const':EQ_CONST,'mult':EQ_MULT,'const_se':EQ_CONST_SE,'mult_se':EQ_MULT_SE,'r2':EQ_R2,'n':len(o),'state_pred':EQ_CONST+EQ_MULT*(-PO['dP']),'state_diff':PO['dG']-(EQ_CONST+EQ_MULT*(-PO['dP']))}
        return m[b]
    if a=='n':
        m={'counties':len(o),'loss':K['n_loss'],'nonloss':len(o)-K['n_loss'],'P_fell':K['n_P_fell'],'S_rose':K['n_S_rose'],'dG_pos':K['n_pos'],'dG_neg':K['n_neg'],
           'narrowed_out':len(NAR['counties']),'narrowed_in':len(o)-len(NAR['counties']),'regdem_rose':int((o.regdem_2026>o.regdem_2022).sum()),'dem_rose':int((o.dem_2026>o.dem_2022).sum()),
           'bal_rose':int((o.ballots_2026>o.ballots_2022).sum()),'implied_neg':int((o.implied_extra_votes<0).sum())}
        return m[b]
    if a=='stat':
        m={'median_dG':K['median_dG'],'median_dS':K['median_dS'],'median_residual':K['median_residual'],'sd_dG':K['sd_dG'],'mean_dG':K['mean_dG'],'median_dP':float(o.dP.median())}
        return m[b]
    if a=='ob':
        y,st=b.split('|'); t=TX[y]
        m={'n_DR_gt_ballots':len(t['DR_gt_ballots']),'n_ballots_gt_reg':len(t['ballots_gt_reg_15day']),'n_ballots_gt_elig':len(t['ballots_gt_eligible']),'n_reg_gt_elig':len(t['regtot_gt_eligible']),
           'n_ballots_gt_reg_elec':len(t['ballots_gt_reg_turnout_report']),'under_median':t['undervote_pct_median'],'under_min':t['undervote_pct_range'][0],'under_max':t['undervote_pct_range'][1]}
        return m[st]
    if a=='raw': return UNP[key]
    if a=='cmp':
        m={'comparisons':R['comparisons'],'matched':R['matched'],'mismatches':R['mismatches_total'],'analysis_comparisons':R['analysis_comparisons'],'figures_per_county':R['figures_per_county'],
           'statewide_checks':len(R['statewide_checks']),'statewide_ok':sum(x['ok'] for x in R['statewide_checks']),'fit_checks':R['fitted_equation_checks']['n'],
           'pdf_cells':PC['cells_checked'],'pdf_matched':PC['cells_matched'],'pdf_mismatches':len(PC['mismatches']),'pdf_pages':PC['pages']}
        return m[b]
    # county
    c,mt=a,b; r=o.loc[c]
    if mt in r.index and mt not in ('loss',): return float(r[mt])
    m={'implied':r.implied_extra_votes,'gapreg':r.gap_reg_scaled,'drop':-r.dP,'eq_pred':EQ_CONST+EQ_MULT*(-r.dP),'eq_diff':r.dG-(EQ_CONST+EQ_MULT*(-r.dP)),
       'dreg':r.regdem_2026-r.regdem_2022,'ddem':r.dem_2026-r.dem_2022,'dbal':r.ballots_2026-r.ballots_2022,'dreg_pct':100*(r.regdem_2026-r.regdem_2022)/r.regdem_2022,
       'ddem_pct':100*(r.dem_2026-r.dem_2022)/r.dem_2022,'dbal_pct':100*(r.ballots_2026-r.ballots_2022)/r.ballots_2022,
       'margin_DR22':r.ballots_2022-r.govtotal_2022,'margin_DR26':r.ballots_2026-r.govtotal_2026,'turnout_reg22':100*r.ballots_2022/r.regtot_2022,'turnout_reg26':100*r.ballots_2026/r.regtot_2026,
       'under_pct22':100*(r.ballots_2022-r.govtotal_2022)/r.ballots_2022,'under_pct26':100*(r.ballots_2026-r.govtotal_2026)/r.ballots_2026,
       'reg_elig22':100*r.regtot_2022/r.eligible_2022,'reg_elig26':100*r.regtot_2026/r.eligible_2026}
    if mt in m: return float(m[mt])
    if mt in ('cooks22','stud22','cooks26','stud26'): return NAR['detail'][c][mt]
    raise KeyError(key)
MAN=[]; PAGE=['']
def N(key,f,star=False):
    t=FMT(bv(key),f); MAN.append(dict(page=PAGE[0],key=key,fmt=f,text=t)); return t+('\\*' if star else '')
def cell(x): return str(x).replace('|','\\|')
def table(head,rows):
    assert all(len(r)==len(head) for r in rows)
    out=['| '+' | '.join(cell(h) for h in head)+' |','|'+'---|'*len(head)]+['| '+' | '.join(cell(v) for v in r)+' |' for r in rows]
    if len(head)>=6: assert not any('→' in str(v) for r in rows for v in r)
    return '\n'.join(out)
def write(name,lines):
    open(WK+name+'.md','w').write('\n'.join(lines))
CO=list(o.index)  # population order
CEIL=K['ceiling']; FLOOR=K['floor']; BOTH=[c for c in CEIL if c in FLOOR]; c0=K['ceiling_by_dG']; LOSS=[c for c in CO if o.loc[c,'loss']]; NONLOSS=[c for c in CO if not o.loc[c,'loss']]
BIG5=CO[:5]; LOWDG=o.dG.idxmin()
STATUS=("> **\\*2026 figures are UNOFFICIAL.** The California Secretary of State (SOS) results site, electionresults.sos.ca.gov, labels the November 3, 2026 general election results \"Unofficial\" "
 "(semi-final unofficial results with county updates; statewide figures as of November 19, 2026, 1:59 p.m. Pacific; pulled November 19, 2026). Counties are still in the canvass: the SOS Unprocessed Ballots Report "
 "(as of 11/18/2026 5:33 p.m.) estimated {rem} ballots statewide still to process, plus {cure} ballots left to cure. Counties must report final official results by December 4, 2026, and the SOS certifies on December 11, 2026, so these pages need a re-run after certification. "
 "2022 figures are the certified Statement of Vote (certificate dated the 16th day of December, 2022). "
 "**P** = Democratic share of registered voters in the SOS 15-day Report of Registration (close of registration: as of October 24, 2022 and as of October 19, 2026). "
 "Governor race only. Votes are votes for the Democratic candidate, not a count of registered Democrats who voted. These pages measure a pattern; they make no claim about intent, fraud or cause.")
def BANNER(): return STATUS.format(rem=N('raw|unproc_remaining','i'),cure=N('raw|unproc_cure','i'))
PAGES=[('Home','Home'),('Reverse-Math','Bottom-Up Reverse Math'),('Locked-California-Formula','Locked California Formula'),('Floor-and-Ceiling','Floor and Ceiling Counties'),('Graphs','Graphs'),('California-County-PDF-Information','California County PDF Information')]
REL=lambda skip:'---\n**Related:** '+' · '.join(f'[{t}]({p})' for p,t in PAGES if p!=skip)+f' · [Cedar County Audit (Nebraska)]({CEDAR})\n'
def nb(c): return f"{c} ({N(c+'|dG','g2',True)})"
# ======================= HOME =======================
PAGE[0]='Home'
H=[BANNER(),'',
f"Method developed by Morissa Benson (CD3 Vice Chair, Nebraska GOP). It began with her [Cedar County Audit]({CEDAR}) on the [Nebraska Election Analysis wiki]({NEWIKI}). That audit is where the ΔG method and the reverse step come from. "
f"This wiki applies the same arithmetic to all {N('n|counties','i')} California counties. California has party registration, so it uses the registration baseline, as the Nevada, North Carolina, Kansas and Pennsylvania analyses do. "
f"Data: California Secretary of State Statement of Vote, Reports of Registration and election-night results ([sos.ca.gov](https://www.sos.ca.gov/elections/prior-elections/statewide-election-results/general-election-nov-8-2022/statement-vote), [Report of Registration](https://www.sos.ca.gov/elections/report-registration/15day-general-2026), [electionresults.sos.ca.gov](https://electionresults.sos.ca.gov/)). Population (sort order only) comes from the U.S. Census Bureau. Compiled November 19, 2026. Code and data: [California-Election-Analysis]({REPO}).",'',
'## Pages','',
f'1. [Cedar County Audit]({CEDAR}) (Nebraska wiki): where the method started',
f'2. [Bottom-Up Reverse Math](Reverse-Math): {c0} (the ceiling county), the five largest counties, then all counties, solved backward for implied extra votes',
'3. [Locked California Formula](Locked-California-Formula): the California fitted equation, a blank template, a worked example and the California-only constants',
'4. [Floor and Ceiling Counties](Floor-and-Ceiling): the floor and ceiling counties, the counties narrowed out of the fit, and the over-ballot check',
'5. [Graphs](Graphs): slope chart, ΔG by population, the ΔS and ΔP components, forward fit, residuals and the over-ballot check',
f'6. [California County PDF Information](California-County-PDF-Information): the county PDF (download), what each column means, and its cell-by-cell check','',
'## Statewide at a glance','',
table(['Measure','2022','2026\\*','Change'],[
 ['Democratic registered voters (15-day report)',N('State|regdem_2022','i'),N('State|regdem_2026','i'),N('State|dreg','s')],
 ['Total registered voters (15-day report)',N('State|regtot_2022','i'),N('State|regtot_2026','i'),N('State|dregtot','s')],
 ['**P**: Democratic share of registration',N('State|P22','p2'),N('State|P26','p2'),N('State|dP','g2')+' pts'],
 ['Democratic governor votes',N('State|dem_2022','i'),N('State|dem_2026','i'),N('State|ddem','s')],
 ['Republican governor votes',N('State|rep_2022','i'),N('State|rep_2026','i'),N('State|drep','s')],
 ['Total ballots cast',N('State|ballots_2022','i'),N('State|ballots_2026','i'),N('State|dbal','s')],
 ['**S**: Democratic share of ballots cast',N('State|S22','p2'),N('State|S26','p2'),N('State|dS','g2')+' pts'],
 ['**G** = S − P',N('State|G22','g2'),N('State|G26','g2'),'ΔG '+N('State|dG','g2')]]),'',
"Candidates (top-two general election): 2022 Gavin Newsom (DEM, incumbent) and Brian Dahle (REP). 2026\\* Xavier Becerra (DEM) and Steve Hilton (REP). Write-in votes are not in the SOS county tables used here.",'',
'## County results in brief','',
f"- **Democratic registration share P fell in {N('n|P_fell','i')} of {N('n|counties','i')} counties** (statewide {N('State|P22','p2')} to {N('State|P26','p2')}). The Democratic registration *count* fell in {N('n|loss','i')} counties and rose statewide by {N('State|dreg','s')}; total registration rose {N('State|dregtot','s')}.",
f"- **The Democratic share of ballots (S) rose in {N('n|S_rose','i')} of {N('n|counties','i')} counties.** County ΔS ranges from {N(o.dS.idxmin()+'|dS','g2',True)} ({o.dS.idxmin()}) to {N(o.dS.idxmax()+'|dS','g2',True)} ({o.dS.idxmax()}), median {N('stat|median_dS','g2',True)}.",
f"- **ΔG is positive in {N('n|dG_pos','i')} counties and negative in {N('n|dG_neg','i')}** ({', '.join(o.index[o.dG<0])}). County median {N('stat|median_dG','g2',True)}; range {N(o.dG.idxmin()+'|dG','g2',True)} ({o.dG.idxmin()}) to {N(o.dG.idxmax()+'|dG','g2',True)} ({o.dG.idxmax()}). Statewide ΔG = {N('State|dG','g2',True)}: S rose {N('State|dS','g2',True)} points and P fell {N('State|drop','f2')} points.",
f"- **Ceiling counties** (five largest ΔG): "+', '.join(nb(c) for c in CEIL)+". **Floor counties** (most Republican baseline, five lowest 2022 P): "+', '.join(f"{c} ({N(c+'|P22','p2')})" for c in FLOOR)+(f". {' and '.join(BOTH)} {'are' if len(BOTH)>1 else 'is'} in both groups" if BOTH else ". No county is in both groups")+". See [Floor and Ceiling Counties](Floor-and-Ceiling).",
f"- **Residual step:** the {N('n|loss','i')} counties whose Democratic registration count fell run it. Residuals range from {N(o.residual.idxmin()+'|residual','g2',True)} ({o.residual.idxmin()}) to {N(o.residual.idxmax()+'|residual','g2',True)} ({o.residual.idxmax()}), median {N('stat|median_residual','g2',True)}. The other {N('n|nonloss','i')} counties (including Los Angeles, San Diego and Orange) gained or kept Democratic registrants and are non-loss counties.",
f"- **Solved backward (hypothesis):** implied extra votes sum to {N('State|implied_sum','s',True)} across the {N('n|counties','i')} counties ({N('State|implied','s',True)} on pooled statewide numbers); Los Angeles accounts for {N('Los Angeles|implied','s',True)}. See [Bottom-Up Reverse Math](Reverse-Math).",
f"- **California fitted equation (Locked page):** ΔG = {N('eq|const','g2')} + {N('eq|mult','f2')} × (Democratic registration-share drop, points), R² {N('eq|r2','f2')}. See [Locked California Formula](Locked-California-Formula#california-fitted-equation-final).",
f"- **Over-ballot check:** in both years, no county has more ballots cast than registered voters on the 15-day report, none has more ballots than eligible residents, none has more registered voters than eligible residents, and none has Democratic + Republican governor votes above ballots cast. The tightest margin is Alpine ({N('Alpine|margin_DR22','i')} ballots without a governor vote in 2022, {N('Alpine|margin_DR26','i')} in 2026\\*). **No over-ballot flags.**",'',
'## Verification: two independent passes over the raw SOS files','',
"- **Pass A** read structured files with structured parsers: the 2022 Statement of Vote governor table (`19-governor.xlsx`), the SOV Voter Participation Statistics by County PDF (word geometry with pdfplumber), the 2026 results site's own data API JSON (governor by county; County Reporting Status), and the 15-day Report of Registration `county.xlsx` for each year.",
"- **Pass B** used separate code on different artifacts, text and regex only: the SOV governor **PDF**, the participation PDF as plain text, the **rendered** 2026 results pages a reader sees (each county's governor page and the County Reporting Status table), and the Report of Registration **PDFs**.",
f"- **Result:** {N('cmp|comparisons','i')} figure comparisons ({N('n|counties','i')} counties × {N('cmp|figures_per_county','i')} figures). **{N('cmp|matched','i')} matched, {N('cmp|mismatches','i')} mismatched.** Every statewide sum matched the SOS's own published statewide total ({N('cmp|statewide_ok','i')} of {N('cmp|statewide_checks','i')}), and the fitted equation and every county's inputs to it agreed in both passes ({N('cmp|fit_checks','i')} checks).",
f"- **Every number on these pages** was recomputed from the raw files through both passes and matched as displayed (see `verification/wiki_number_check.csv`). **Every cell of the county PDF** ({N('cmp|pdf_cells','i')} cells) was recomputed from the raw files and matched the printed value ({N('cmp|pdf_matched','i')} of {N('cmp|pdf_cells','i')}).",'',
'## Read this before using the numbers','',
"- **2026 is UNOFFICIAL and incomplete.** Ballots were still being processed when these figures were pulled. Every 2026 figure carries an asterisk and will change before certification.",
"- **Registration date.** P uses the 15-day Report of Registration, the SOS's close-of-registration snapshot for each general election. California has same-day (conditional) voter registration, so people who registered after the 15-day report could still vote; the 15-day count is a baseline, not the final roll.",
"- **Ballots cast** is the county's total ballots cast in the election (SOV \"Total Voters\" in 2022; \"Ballots Cast\" on the County Reporting Status page in 2026\\*), not governor votes. Ballots without a governor vote stay in the denominator of S.",
"- **No other state's constant is used.** All fitted values on these pages come from California's own counties.",
'',REL('Home')]
write('Home',H)
# ======================= REVERSE MATH =======================
PAGE[0]='Reverse-Math'; r0=o.loc[c0]
def ctab(cs):
    return table(['County','P 2022','S 2022','G 2022','P 2026\\*','S 2026\\*','G 2026\\*','ΔG\\*'],[[c,N(c+'|P22','f2'),N(c+'|S22','f2'),N(c+'|G22','g2'),N(c+'|P26','f2'),N(c+'|S26','f2'),N(c+'|G26','g2'),N(c+'|dG','g2')] for c in cs])
RM=[BANNER(),'',
"The reverse math runs bottom-up: start with the ceiling county, then the largest counties, then every county, and only then solve backward for the votes the pattern implies. Each step uses the same three numbers per county and year: Democratic governor votes, total ballots cast, and the Democratic share of registration P.",'',
f'## Step one: {c0} (the ceiling county)','',
table(['Item','2022','2026\\*'],[
 ['Democratic registered voters',N(c0+'|regdem_2022','i'),N(c0+'|regdem_2026','i')],['Total registered voters',N(c0+'|regtot_2022','i'),N(c0+'|regtot_2026','i')],
 ['P',N(c0+'|P22','f2'),N(c0+'|P26','f2')],['Democratic governor votes',N(c0+'|dem_2022','i'),N(c0+'|dem_2026','i')],['Total ballots cast',N(c0+'|ballots_2022','i'),N(c0+'|ballots_2026','i')],
 ['S',N(c0+'|S22','f2'),N(c0+'|S26','f2')],['G = S − P',N(c0+'|G22','g2'),N(c0+'|G26','g2')]]),'',
f"ΔG = {N(c0+'|G26','g2')} − ({N(c0+'|G22','g2')}) = **{N(c0+'|dG','g2',True)}**. S rose {N(c0+'|dS','g2')} points while P moved {N(c0+'|dP','g2')} points. "+
(f"{c0}'s Democratic registration count fell ({N(c0+'|regdem_2022','i')} to {N(c0+'|regdem_2026','i')}), so it runs the residual step: residual = ΔG − |ΔP| = {N(c0+'|residual','g2',True)}." if r0.loss else f"{c0}'s Democratic registration count did not fall ({N(c0+'|regdem_2022','i')} to {N(c0+'|regdem_2026','i')}), so it is a non-loss county and skips the residual step."),'',
'## Step two: the five largest counties','',
ctab(BIG5),'',
f"Los Angeles alone cast {N('Los Angeles|ballots_2026','i',True)} of the state's {N('State|ballots_2026','i',True)} ballots in 2026\\*. All five are non-loss counties: Democratic registration rose in each." if all(not o.loc[c,'loss'] for c in BIG5) else '','',
'## Step three: all counties','',
f"Across all {N('n|counties','i')} counties, ΔG is positive in {N('n|dG_pos','i')} and negative in {N('n|dG_neg','i')}. The county median is {N('stat|median_dG','g2',True)}. Statewide, G went from {N('State|G22','g2')} to {N('State|G26','g2',True)}, a ΔG of {N('State|dG','g2',True)}. The full table is at the bottom of this page.",'',
f'## Residual step: the {N("n|loss","i")} counties that lost Democratic registrants','',
f"Run the reverse step only where the Democratic registration count fell. Residual = ΔG − |P 2026 − P 2022|: the vote-share movement left after subtracting the expected loss from the registration-share decline.",'',
table(['County','Dem reg. 2022','Dem reg. 2026','ΔP','ΔG\\*','Residual\\*'],[[c,N(c+'|regdem_2022','i'),N(c+'|regdem_2026','i'),N(c+'|dP','g2'),N(c+'|dG','g2'),N(c+'|residual','g2')] for c in sorted(LOSS,key=lambda c:-o.loc[c,'residual'])]),'',
f"Median residual {N('stat|median_residual','g2',True)}. Non-loss counties ({N('n|nonloss','i')}): "+', '.join(NONLOSS)+".",'',
f"Statewide the Democratic registration count rose ({N('State|regdem_2022','i')} to {N('State|regdem_2026','i')}), so by the county rule California as a whole is a non-loss case. On shares alone, ΔG − |ΔP| statewide = {N('State|residual_share','g2',True)}.",'',
'## Solving backward: implied extra votes (hypothesis)','',
"Implied extra votes = Democratic votes 2026 − (S 2022 ÷ 100) × ballots 2026: the Democratic votes above what the 2022 share of ballots would give on the 2026 ballot count. The registration-scaled gap (the Nebraska wiki's \"gap in votes\" line) = Democratic votes 2026 − Democratic votes 2022 × (Dem registration 2026 ÷ Dem registration 2022).",'',
table(['Group','Implied extra votes\\*'],[['All counties (sum)',N('State|implied_sum','s')],['Pooled statewide numbers',N('State|implied','s')],[f'Loss counties ({N("n|loss","i")})',N('State|implied_sum_loss','s')],[f'Non-loss counties ({N("n|nonloss","i")})',N('State|implied_sum_nonloss','s')]]),'',
f"Registration-scaled gap, summed over counties: {N('State|gapreg_sum','s',True)}. Counties with negative implied extra votes: "+(', '.join(f"{c} ({N(c+'|implied','s',True)})" for c in o.index[o.implied_extra_votes<0]) or 'none')+".",'',
'## What the arithmetic cannot tell you','',
"- It cannot tell a persuaded voter from a new voter, a registration change from a turnout change, or a counting problem from a campaign.",
"- 2026 ballots were still being counted. Late ballots in California lean differently from early ones, so S, ΔG and every implied-vote figure will move before certification.",
"- Same-day registration means some 2026 voters are not in the 15-day registration baseline at all.",'',
'## Full county table (largest to smallest population)','',
table(['County','P 2022','S 2022','G 2022','P 2026\\*','S 2026\\*','G 2026\\*','ΔG\\*','Residual\\*','Implied extra votes\\*'],
 [[c,N(c+'|P22','f2'),N(c+'|S22','f2'),N(c+'|G22','g2'),N(c+'|P26','f2'),N(c+'|S26','f2'),N(c+'|G26','g2'),N(c+'|dG','g2'),(N(c+'|residual','g2') if o.loc[c,'loss'] else 'non-loss'),N(c+'|implied','s')] for c in CO]),'',
REL('Reverse-Math')]
write('Reverse-Math',RM)
# ======================= LOCKED FORMULA =======================
PAGE[0]='Locked-California-Formula'
LA='Los Angeles'
def fitrow(lbl,name,star):
    return [lbl,N(f'fit|{name}|n','i'),f"{N(f'fit|{name}|m','g2')} ({N(f'fit|{name}|m_se','f2')})",f"{N(f'fit|{name}|b','g2')} ({N(f'fit|{name}|b_se','f2')})",N(f'fit|{name}|r2','f3'),N(f'fit|{name}|resid_se','f2'),
            f"{N(f'fit|{name}|within1','pct0')} / {N(f'fit|{name}|within2','pct0')} / {N(f'fit|{name}|within3','pct0')}",N(f'fit|{name}|med_abs','f2')]
LK=[BANNER(),'',
'## California fitted equation (final)','',
'```',
f"California equation:  ΔG = {N('eq|const','g2')} + {N('eq|mult','f2')} × (Dem registration-share drop, points)",
f"Four decimals:        ΔG = {N('eq|const','g4')} + {N('eq|mult','f4')} × (Dem registration-share drop, points)",
'```','',
table(['Item','Rounded','Four decimals'],[
 ['Constant (intercept)',N('eq|const','g2'),N('eq|const','g4')],['Multiplier (slope)',N('eq|mult','f2'),N('eq|mult','f4')],
 ['Intercept standard error',N('eq|const_se','f2'),N('eq|const_se','f4')],['Slope standard error',N('eq|mult_se','f2'),N('eq|mult_se','f4')],['R²',N('eq|r2','f2'),N('eq|r2','f4')]]),'',
f"Fitted by ordinary least squares across all {N('eq|n','i')} counties (n = {N('eq|n','i')}), each county weighted equally: 2022 to 2026\\* governor race, registration from the SOS 15-day Reports of Registration, S denominator = total ballots cast, locked gap formula. Registration-share drop = P 2022 − P 2026, in points. 2026 figures are UNOFFICIAL. Computed separately in Pass A (numpy least squares) and Pass B (closed-form, pure Python); the two agree to within one part in a billion.",'',
f"**What it means:** across California's counties, each one-point drop in Democratic registration share goes with about {N('eq|mult','f2')} points of ΔG, starting from about {N('eq|const','g2')} when the share does not fall. The fit explains little of the county-to-county differences in ΔG (R² {N('eq|r2','f2')}); the slope's standard error is {N('eq|mult_se','f2')}.",'',
f"**Worked example: {LA}.** P fell from {N(LA+'|P22','f2')} to {N(LA+'|P26','f2')}, a drop of {N(LA+'|drop','f4')} points. Predicted ΔG = {N('eq|const','g4')} + {N('eq|mult','f4')} × {N(LA+'|drop','f4')} = {N(LA+'|eq_pred','g2')}. Actual ΔG = {N(LA+'|dG','g2',True)}. Difference from the fitted line (actual − predicted) = {N(LA+'|eq_diff','g2',True)}. Statewide (pooled totals): drop {N('State|drop','f4')}, predicted {N('eq|state_pred','g2')}, actual {N('State|dG','g2',True)}.",'',
'## The equation','',
"- **S** (Democratic vote share) = Democratic governor votes ÷ total ballots cast × 100. Ballots cast is the county's total ballots cast (2022: SOV Voter Participation Statistics, Total Voters; 2026\\*: SOS County Reporting Status, Ballots Cast).",
"- **P** (Democratic registration share) = Democratic registered voters ÷ Total Registered × 100, from the SOS 15-day Report of Registration (Registration by County) for each general election.",
"- **G** = S − P",
"- **ΔG** = G(2026) − G(2022) = (S2026 − S2022) − (P2026 − P2022)",
"- **Reverse step (residual).** Run it only where the Democratic registration count fell. Residual = ΔG − |P2026 − P2022|.",
"- **Solved backward: implied extra votes** = D2026 − (S2022 ÷ 100) × ballots2026",
"- **Registration-scaled gap** = D2026 − D2022 × (DemReg2026 ÷ DemReg2022)",'',
'### Why these files','',
"- **Registration date.** The 15-day Report of Registration is the SOS's close-of-registration snapshot for each general election (as of October 24, 2022 and as of October 19, 2026). It is the same point in both election cycles, and it is the registration figure the SOS itself uses for turnout on its results pages.",
"- **Ballots, not governor votes.** S divides by total ballots cast in the county, so ballots with no governor vote stay in the denominator.",
"- **2022 is certified; 2026 is not.** The 2022 Statement of Vote is the certified canvass. The 2026 figures are the SOS's semi-final unofficial results with county updates, pulled November 19, 2026.",'',
'## Blank template','',
table(['Line','Item','2022','2026'],[
 ['L1','Democratic governor votes','______','______'],['L2','Total ballots cast','______','______'],['L3','S = L1 ÷ L2 × 100','______','______'],
 ['L4','Democratic registered voters (15-day Report of Registration)','______','______'],['L5','Total Registered (same report)','______','______'],['L6','P = L4 ÷ L5 × 100','______','______'],
 ['L7','G = L3 − L6','______','______'],['L8','ΔG = G 2026 − G 2022','','______'],['L9','Registration-share change = P 2026 − P 2022','','______'],
 ['L10','Did the Democratic registration count fall? (L4: 2026 below 2022)','','Yes / No'],['L11','If yes: residual = L8 − \\|L9\\|','','______'],
 ['L12','Implied extra votes = L1 (2026) − L3 (2022) ÷ 100 × L2 (2026)','','______'],['L13','Registration-scaled gap = L1 (2026) − L1 (2022) × (L4 2026 ÷ L4 2022)','','______'],
 ['L14','Fitted G = m × (L6 ÷ 100) + b, CA constants for that year','______','______'],['L15','Distance from the CA line = L7 − L14','______','______'],
 ['L16','Fitted-equation prediction = constant + multiplier × (− L9)','','______']]),'',
f'## Worked example: {c0} (ceiling county)','',
table(['Line','Item','2022','2026\\*'],[
 ['L1','Democratic governor votes',N(c0+'|dem_2022','i'),N(c0+'|dem_2026','i')],['L2','Total ballots cast',N(c0+'|ballots_2022','i'),N(c0+'|ballots_2026','i')],['L3','S',N(c0+'|S22','f2'),N(c0+'|S26','f2')],
 ['L4','Democratic registered voters',N(c0+'|regdem_2022','i'),N(c0+'|regdem_2026','i')],['L5','Total Registered',N(c0+'|regtot_2022','i'),N(c0+'|regtot_2026','i')],['L6','P',N(c0+'|P22','f2'),N(c0+'|P26','f2')],
 ['L7','G',N(c0+'|G22','g2'),N(c0+'|G26','g2')],['L8','ΔG','',N(c0+'|dG','g2')],['L9','Registration-share change','',N(c0+'|dP','g2')],
 ['L10','Democratic registration count fell?','','Yes' if r0.loss else 'No'],['L11','Residual','',N(c0+'|residual','g2') if r0.loss else 'not run (non-loss county)'],
 ['L12','Implied extra votes','',N(c0+'|implied','s')],['L13','Registration-scaled gap','',N(c0+'|gapreg','s')],
 ['L14','Fitted G',N(c0+'|fit22','g2'),N(c0+'|fit26','g2')],['L15','Distance from the CA line',N(c0+'|res22','g2'),N(c0+'|res26','g2')],['L16','Fitted-equation prediction','',N(c0+'|eq_pred','g2')]]),'',
'## CA-only constants (forward fit)','',
f"The forward surplus equation is fit by least squares across all {N('n|counties','i')} California counties, each weighted equally: **G = m × (P ÷ 100) + b**. It uses California data only. No other state's constant is reused.",'',
table(['Fit','n','m (SE)','b (SE)','R²','Residual SE','Within one / two / three pts','Median abs. residual'],[
 fitrow('2022, all counties','2022',False),fitrow('2026\\*, all counties','2026',True),fitrow('2022, narrowed','2022_narrowed',False),fitrow('2026\\*, narrowed','2026_narrowed',True),
 fitrow('2022, ballot-weighted','2022_wtd',False),fitrow('2026\\*, ballot-weighted','2026_wtd',True),fitrow('2022 + 2026\\* pooled','pooled',True)]),'',
f"**The locked CA constants are the all-county fits: 2022 m = {N('fit|2022|m','g2')}, b = {N('fit|2022|b','g2')}; 2026\\* m = {N('fit|2026|m','g2')}, b = {N('fit|2026|b','g2')}.** Narrowed fits leave out {', '.join(NAR['counties'])} (see [Floor and Ceiling Counties](Floor-and-Ceiling#counties-narrowed-out-of-the-fit)).",'',
f"- **What m means.** G already contains −P, so an m of minus one hundred would mean S does not move with P at all, and an m of zero would mean S moves point for point with P. It is not an \"injection multiplier.\"",
f"- **Intercepts.** 2022 b 95% interval {N('fit|2022|b_lo','g2')} to {N('fit|2022|b_hi','g2')}; 2026\\* {N('fit|2026|b_lo','g2')} to {N('fit|2026|b_hi','g2')}.",'',
'## Rules for using this formula','',
"1. **Use registration from the same report in both years.** California's are the SOS 15-day Reports of Registration.",
f"2. **If a county lost Democratic registrants, run the residual step.** In California that is {N('n|loss','i')} counties; the other {N('n|nonloss','i')} are non-loss counties.",
f"3. **The starting point is different in every state.** California's constants come from California's own {N('n|counties','i')} counties. Los Angeles alone cast {N('Los Angeles|ballots_2026','i',True)} of {N('State|ballots_2026','i',True)} ballots, but the equal-weight fit counts it once, like Alpine.",
f"4. **Always pull out the ceiling and floor counties.** The ceiling county is {c0} ({N(c0+'|dG','g2',True)}), and the lowest ΔG is {LOWDG} ({N(LOWDG+'|dG','g2',True)}). The floor (most Republican baseline) is {', '.join(FLOOR)}. See [Floor and Ceiling Counties](Floor-and-Ceiling).",'',
REL('Locked-California-Formula')]
write('Locked-California-Formula',LK)
# ======================= FLOOR AND CEILING =======================
PAGE[0]='Floor-and-Ceiling'
FC=[BANNER(),'',
'## How to read floor and ceiling counties','',
"The **ceiling** counties are the five with the largest ΔG: where the Democratic share of ballots outran the Democratic share of registration by the most between 2022 and 2026\\*. The **floor** counties are the five with the most Republican registration baseline (lowest 2022 P). Looking at both shows whether the biggest movements came from places with few Democrats to begin with.",'',
'## Terminology','',
"- **Ceiling counties**: the five largest ΔG.",
"- **Floor counties**: the five lowest 2022 Democratic registration shares (P 2022).",
"- **Loss counties**: the Democratic registration count fell between the two 15-day reports. Only these run the residual step.",
"- **Non-loss counties**: the Democratic registration count rose or held.",
"- **Narrowed-out counties**: counties whose Cook's distance is above four divided by n, or whose externally studentized residual is beyond two and a half in absolute value, in either year's G-on-P fit.",'',
'## Ceiling and floor detail','',
table(['County','Group','P 2022','P 2026\\*','S 2022','S 2026\\*','ΔG\\*','Loss county'],
 [[c,'ceiling'+(' + floor' if c in FLOOR else ''),N(c+'|P22','f2'),N(c+'|P26','f2'),N(c+'|S22','f2'),N(c+'|S26','f2'),N(c+'|dG','g2'),'yes' if o.loc[c,'loss'] else 'no'] for c in CEIL]+
 [[c,'floor',N(c+'|P22','f2'),N(c+'|P26','f2'),N(c+'|S22','f2'),N(c+'|S26','f2'),N(c+'|dG','g2'),'yes' if o.loc[c,'loss'] else 'no'] for c in FLOOR if c not in CEIL]),'',
f"The five lowest ΔG are {', '.join(f'{c} ({N(c+chr(124)+'dG','g2',True)})' for c in K['lowest5_dG'])}: the Bay Area counties with the highest Democratic baselines.",'',
'## Counties narrowed out of the fit','',
f"Rule: Cook's distance above four divided by n ({N('fit|cut','f3')}) or |externally studentized residual| above two and a half, in either year's fit. {N('n|narrowed_out','i')} counties are narrowed out; the narrowed fits use {N('n|narrowed_in','i')}.",'',
table(['County',"Cook's D 2022","Studentized 2022","Cook's D 2026\\*","Studentized 2026\\*",'P 2022','G 2022','G 2026\\*'],
 [[c,N(c+'|cooks22','f3'),N(c+'|stud22','g2'),N(c+'|cooks26','f3'),N(c+'|stud26','g2'),N(c+'|P22','f2'),N(c+'|G22','g2'),N(c+'|G26','g2')] for c in NAR['counties']]),'',
'## Over-ballot check','',
"Three tests per county and year: ballots cast against registered voters on the 15-day report, ballots cast and registered voters against eligible residents (the SOS's own eligible count on the same report), and Democratic + Republican governor votes against ballots cast.",'',
table(['Test','2022','2026\\*'],[
 ['Counties with ballots cast above 15-day registration',N('ob|2022|n_ballots_gt_reg','i'),N('ob|2026|n_ballots_gt_reg','i')],
 ['Counties with ballots cast above eligible residents',N('ob|2022|n_ballots_gt_elig','i'),N('ob|2026|n_ballots_gt_elig','i')],
 ['Counties with registered voters above eligible residents',N('ob|2022|n_reg_gt_elig','i'),N('ob|2026|n_reg_gt_elig','i')],
 ['Counties with Dem + Rep governor votes above ballots cast',N('ob|2022|n_DR_gt_ballots','i'),N('ob|2026|n_DR_gt_ballots','i')],
 ['Ballots with no governor vote, county median (% of ballots)',N('ob|2022|under_median','p2'),N('ob|2026|under_median','p2')],
 ['Ballots with no governor vote, statewide (% of ballots)',N('State|under_pct22','p2'),N('State|under_pct26','p2')],
 ['Highest turnout of 15-day registration',f"{TX['2022']['max_turnout_of_reg_15day']['county']} {N(TX['2022']['max_turnout_of_reg_15day']['county']+'|turnout_reg22','p2')}",f"{TX['2026']['max_turnout_of_reg_15day']['county']} {N(TX['2026']['max_turnout_of_reg_15day']['county']+'|turnout_reg26','p2')}"],
 ['Highest registration of eligible',f"{TX['2022']['max_reg_of_eligible']['county']} {N(TX['2022']['max_reg_of_eligible']['county']+'|reg_elig22','p2')}",f"{TX['2026']['max_reg_of_eligible']['county']} {N(TX['2026']['max_reg_of_eligible']['county']+'|reg_elig26','p2')}"]]),'',
f"**No over-ballot flags in either year.** The tightest margin is Alpine, with {N('Alpine|margin_DR22','i')} ballots without a governor vote in 2022 and {N('Alpine|margin_DR26','i')} in 2026\\*. Because of same-day registration, a county could legitimately cast more ballots than its 15-day registration count; none did.",'',
'## Data sources','',
"- 2022 governor votes: SOS Statement of Vote, Governor ([xlsx](https://elections.cdn.sos.ca.gov/sov/2022-general/sov/19-governor.xlsx), [PDF](https://elections.cdn.sos.ca.gov/sov/2022-general/sov/19-governor.pdf)). Certified.",
"- 2022 ballots cast: SOS SOV [Voter Participation Statistics by County](https://elections.cdn.sos.ca.gov/sov/2022-general/sov/03-voter-participation-stats-by-county.pdf), Total Voters. Certified.",
"- Registration: SOS 15-day Report of Registration, Registration by County ([2022 xlsx](https://elections.cdn.sos.ca.gov/ror/15day-general-2022/county.xlsx), [2022 PDF](https://elections.cdn.sos.ca.gov/ror/15day-general-2022/county.pdf), [2026 xlsx](https://elections.cdn.sos.ca.gov/ror/15day-gen-2026/county.xlsx), [2026 PDF](https://elections.cdn.sos.ca.gov/ror/15day-gen-2026/county.pdf)).",
"- 2026\\* governor votes and ballots cast: [electionresults.sos.ca.gov](https://electionresults.sos.ca.gov/returns/governor) (county governor pages and [County Reporting Status](https://electionresults.sos.ca.gov/returns/status)) and the site's data API (`api.sos.ca.gov/returns/governor/county/alameda` (one file per county), `api.sos.ca.gov/returns/maps/status/gubernatorial-general`). UNOFFICIAL.",
"- Population (sort order only): U.S. Census Bureau county population estimates, Vintage 2025.",'',
REL('Floor-and-Ceiling')]
write('Floor-and-Ceiling',FC)
# ======================= GRAPHS =======================
PAGE[0]='Graphs'
ch=[('Slope chart: G, 2022 to 2026','CA_Slope_G2022_to_G2026.png','County G in 2022 and 2026','Each line is one county. Red lines are the ceiling counties, blue lines the floor counties.'),
 ('ΔG by county, population order','CA_DeltaG_by_Population.png','Bar chart of ΔG by county','Largest county on the left. Red = ceiling, blue = floor.'),
 ('What ΔG is made of: ΔS vs ΔP','CA_DeltaG_Components_dS_vs_dP_by_Population.png','ΔS and minus ΔP by county','Blue = change in the Democratic share of ballots; orange = minus the change in the Democratic registration share; black tick = ΔG.'),
 ('Democratic share of ballots and P, population order','CA_Stacked_Share_and_Registration_by_Population.png','Democratic share of ballots with registration markers','Bars: the Democratic share of ballots, with the 2026 gain stacked on top. Markers: P in each year.'),
 ('Forward fit: CA-only constants','CA_Forward_Fit_G_vs_P_2022_2026.png','G against P with fitted lines','Solid line: all-county fit. Dashed: narrowed fit. Black outline = narrowed-out county.'),
 ('ΔG vs ΔP','CA_DeltaG_vs_DeltaP_Scatter.png','ΔG against the registration-share change','Counties above the dotted line had a rise in S.'),
 ('Residual step and implied extra votes','CA_Residual_and_Implied_Votes_by_Population.png','Residual and implied extra votes by county','Top: residual = ΔG − |ΔP| for loss counties only. Bottom: implied extra votes (symmetric log scale).'),
 ('Over-ballot check','CA_Overballot_Check_by_Population.png','Ballots against governor votes and against registration','Top: ballots minus governor votes, as a share of ballots. Bottom: ballots as a share of 15-day registration. No county crosses either line.')]
G=[BANNER(),'','Every chart carries the source and the 2026 UNOFFICIAL label in its footer. Bars run left to right from the largest county to the smallest (Census Vintage 2025).','']
for h,f,alt,cap in ch: G+=[f'## {h}','',f'![{alt}]({RAW}{f})','',f'*{cap}*','']
G+=['## Data behind the charts','',
f'- County table: [data/CA_Governor_2022_2026_DeltaG_by_County.csv]({REPO}/blob/{BRANCH}/data/CA_Governor_2022_2026_DeltaG_by_County.csv)',
f'- Fits, narrowed fits, floor and ceiling, over-ballot checks: [data/CA_results_summary.json]({REPO}/blob/{BRANCH}/data/CA_results_summary.json)',
f'- Verification (both passes, figure by figure): [verification/]({REPO}/tree/{BRANCH}/verification)','',REL('Graphs')]
write('Graphs',G)
# ======================= PDF INFO =======================
PAGE[0]='California-County-PDF-Information'
PI=[BANNER(),'',
f'**[Download: {PDFN}]({PDFRAW})** ({N("cmp|pdf_pages","i")} landscape pages) · [Excel version]({REPO}/raw/{BRANCH}/{XLSXN})','',
f"All {N('n|counties','i')} counties, sorted by 2026 Democratic share of registration (highest first, {o.sort_values('P26',ascending=False).index[0]} first): Democratic registration on the 15-day reports for 2022 and 2026, Democratic governor votes for 2022 and 2026\\*, and total ballots cast for 2022 and 2026\\*, each with the change as a number and a percent, plus a statewide totals row. The second table shows the Democratic share of ballots and of registration. Counties where Democratic registration rose are shaded blue; no county's Democratic governor vote fell.",'',
'## Columns','',
table(['Column','Meaning'],[
 ['County','County name'],['Dem Reg Share 2026 %','Democratic registered voters ÷ Total Registered, 15-day Report of Registration as of October 19, 2026 (the sort key)'],
 ['Dem Reg 2022 (Oct 24) / Dem Reg 2026 (Oct 19)','Democratic registered voters on the 15-day Report of Registration for each election'],
 ['Reg Change # / Reg Change %','Dem Reg 2026 minus Dem Reg 2022, and that change as a percent of Dem Reg 2022'],
 ['Dem Gov Votes 2022 / 2026\\*','Votes for the Democratic governor candidate (2022 Statement of Vote; 2026\\* SOS unofficial results)'],
 ['Vote Change # / Vote Change % (on 2022 base)','Dem Gov Votes 2026\\* minus 2022, and that change as a percent of the 2022 votes'],
 ['Total Ballots 2022 / 2026\\*','Total ballots cast in the county (all contests), not governor votes'],
 ['Ballot Change # / Ballot Change %','Total Ballots 2026\\* minus 2022, and that change as a percent of 2022'],
 ['Second table','Dem share of ballots (Dem governor votes ÷ total ballots) for each year, its change in points, Dem share of registration for each year, and Total Registered']]),'',
'## Statewide totals row','',
table(['Column','Value'],[
 ['Dem Reg Share 2026 %',N('State|P26','p1')],['Dem Reg 2022',N('State|regdem_2022','i')],['Dem Reg 2026',N('State|regdem_2026','i')],['Reg Change #',N('State|dreg','s')],['Reg Change %',N('State|dreg_pct','gp1')],
 ['Dem Gov Votes 2022',N('State|dem_2022','i')],['Dem Gov Votes 2026\\*',N('State|dem_2026','i')],['Vote Change #',N('State|ddem','s')],['Vote Change %',N('State|ddem_pct','gp1')],
 ['Total Ballots 2022',N('State|ballots_2022','i')],['Total Ballots 2026\\*',N('State|ballots_2026','i')],['Ballot Change #',N('State|dbal','s')],['Ballot Change %',N('State|dbal_pct','gp1')]]),'',
'## How the PDF was checked','',
f"Every cell was recomputed from the raw SOS files through two independent parsers (pass A and pass B), with exact arithmetic rounded to the decimals the PDF prints, and compared with the text actually printed in the PDF: **{N('cmp|pdf_matched','i')} of {N('cmp|pdf_cells','i')} cells matched, {N('cmp|pdf_mismatches','i')} mismatched.** The sort order, page numbers and row count were checked too. See `verification/pdf_cell_check.csv` and `verification/pdf_cell_check_summary.json` in the [repository]({REPO}).",'',
REL('California-County-PDF-Information')]
write('California-County-PDF-Information',PI)
# ======================= SIDEBAR =======================
PAGE[0]='_Sidebar'
SB=['**California ΔG wiki**','','1. [Home](Home)','2. [Bottom-Up Reverse Math](Reverse-Math)','3. [Locked California Formula](Locked-California-Formula)','4. [Floor and Ceiling Counties](Floor-and-Ceiling)','5. [Graphs](Graphs)','6. [California County PDF Information](California-County-PDF-Information)','',
f'Method origin: [Cedar County Audit (Nebraska)]({CEDAR})','','*2026 figures UNOFFICIAL until the SOS certifies on December 11, 2026.*','']
write('_Sidebar',SB)
# ======================= README =======================
PAGE[0]='README'
pngs=[f for _,f,_,_ in ch]
RD=['# California Election Analysis: 2022 vs 2026 Governor (ΔG method)','',
f"**\\*2026 figures are UNOFFICIAL** (CA SOS semi-final unofficial results, statewide as of November 19, 2026, 1:59 p.m. Pacific). The SOS certifies on December 11, 2026. 2022 figures are the certified Statement of Vote.",'',
f"County-level analysis of the California governor race, 2022 vs 2026, for all {N('n|counties','i')} counties. It uses the ΔG method from Morissa Benson's [Cedar County Audit]({CEDAR}). The full write-up is on the **[wiki]({REPO}/wiki)**.",'',
'- **S** = Democratic governor votes ÷ total ballots cast',
'- **P** = Democratic registered voters ÷ Total Registered, SOS 15-day Report of Registration',
'- **G** = S − P; **ΔG** = G2026 − G2022; residual = ΔG − |ΔP| for counties whose Democratic registration count fell; implied extra votes = D2026 − S2022 × ballots2026',
f"- **California fitted equation:** ΔG = {N('eq|const','g2')} + {N('eq|mult','f2')} × (Dem registration-share drop, points)",
f"- **CA-only constants** (G = m × P ÷ 100 + b, all counties): 2022 m = {N('fit|2022|m','g2')}, b = {N('fit|2022|b','g2')}; 2026\\* m = {N('fit|2026|m','g2')}, b = {N('fit|2026|b','g2')}",'',
'## Contents','',
table(['Path','What'],[
 ['CA_*.png','The charts used on the wiki'],
 [PDFN,'The county PDF (Democratic registration, Democratic governor votes and total ballots, 2022 vs 2026\\*), with its Excel source'],
 ['data/CA_Governor_2022_2026_DeltaG_by_County.csv','All counties, every input and computed figure, sorted by population'],
 ['data/CA_results_summary.json','Fits, narrowed fits, floor and ceiling, over-ballot checks, statewide totals'],
 ['verification/','Pass A and Pass B county tables, the figure-by-figure comparison, the PDF cell check, the wiki number check, the render check'],
 ['raw/','Untouched source files: 2022 Statement of Vote, 15-day Reports of Registration, 2026 results-site API JSON and rendered pages, Census file, fetch logs'],
 ['scripts/','run_all.sh runs the whole build in order'],
 ['wiki/','The wiki pages and _Sidebar.md, as they will be pushed to the wiki']]),'',
'## Verification','',
f"Two independent passes over the raw SOS files: {N('cmp|comparisons','i')} figure comparisons, {N('cmp|matched','i')} matched and {N('cmp|mismatches','i')} mismatched. The county PDF: {N('cmp|pdf_matched','i')} of {N('cmp|pdf_cells','i')} cells matched a recomputation from the raw files. Every number on the wiki pages and in this README was traced to both passes.",'',
'These pages measure a pattern. They make no claim about intent, fraud or cause.','']
open(O+'README.md','w').write('\n'.join(RD))
json.dump(MAN,open(V+'wiki_number_manifest.json','w'),indent=0)
print('built',sorted(os.listdir(WK)),len(MAN),'numbers in manifest')
