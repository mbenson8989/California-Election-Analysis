"""Independent recomputation of EVERY number the wiki/README/PDF display, from ONE pass's county table (pure Python + numpy;
no pandas/statsmodels, so it shares no computation code with analysis.py). verify_wiki.py runs it twice: once on the table that
pass_a.py parsed from the raw files and once on the table pass_b.py parsed from different raw artifacts.
compute(rows) -> {key: value}. Keys: '<County>|<metric>', 'State|<metric>', 'fit|<name>|<stat>', 'eq|<stat>', 'n|<name>', 'ob|<year>|<stat>'."""
import numpy as np, math, csv
from scipy import stats as _st
FIELDS=['reg_elec_2022','ballots_2022','dem_2022','rep_2022','other_2022','govtotal_2022','regdem_2022','regrep_2022','regtot_2022','eligible_2022',
        'reg_elec_2026','ballots_2026','dem_2026','rep_2026','other_2026','govtotal_2026','regdem_2026','regrep_2026','regtot_2026','eligible_2026']
def load(path): return {r['county']:{k:int(r[k]) for k in FIELDS} for r in csv.DictReader(open(path))}
def derive(r):
    d=dict(r)
    d['S22']=100*r['dem_2022']/r['ballots_2022']; d['S26']=100*r['dem_2026']/r['ballots_2026']
    d['P22']=100*r['regdem_2022']/r['regtot_2022']; d['P26']=100*r['regdem_2026']/r['regtot_2026']
    d['G22']=d['S22']-d['P22']; d['G26']=d['S26']-d['P26']; d['dS']=d['S26']-d['S22']; d['dP']=d['P26']-d['P22']; d['dG']=d['G26']-d['G22']; d['drop']=-d['dP']
    d['loss']=1 if r['regdem_2026']<r['regdem_2022'] else 0
    if d['loss']: d['residual']=d['dG']-abs(d['dP'])
    d['implied']=r['dem_2026']-d['S22']/100*r['ballots_2026']
    d['gapreg']=r['dem_2026']-r['dem_2022']*(r['regdem_2026']/r['regdem_2022'])
    for a,b,k in (('regdem_2022','regdem_2026','reg'),('dem_2022','dem_2026','dem'),('ballots_2022','ballots_2026','bal'),('regtot_2022','regtot_2026','regtot'),('rep_2022','rep_2026','rep')):
        d['d'+k]=r[b]-r[a]; d['d'+k+'_pct']=100*(r[b]-r[a])/r[a]
    for y,t in (('2022','22'),('2026','26')):
        d['margin_DR'+t]=r['ballots_'+y]-r['dem_'+y]-r['rep_'+y]; d['under_pct'+t]=100*d['margin_DR'+t]/r['ballots_'+y]
        d['turnout_reg'+t]=100*r['ballots_'+y]/r['regtot_'+y]; d['reg_elig'+t]=100*r['regtot_'+y]/r['eligible_'+y]
    return d
def ols(x,y,w=None):
    x=np.asarray(x,float)/100; y=np.asarray(y,float); n=len(y); X=np.c_[np.ones(n),x]
    W=np.ones(n) if w is None else np.asarray(w,float)
    XtW=X.T*W; A=np.linalg.inv(XtW@X); beta=A@(XtW@y); e=y-X@beta
    s2=(W*e*e).sum()/(n-2); cov=s2*A
    ybar=(W*y).sum()/W.sum(); r2=1-(W*e*e).sum()/(W*(y-ybar)**2).sum()
    t=_st.t.ppf(0.975,n-2)
    return dict(n=n,m=beta[1],b=beta[0],m_se=math.sqrt(cov[1,1]),b_se=math.sqrt(cov[0,0]),r2=r2,resid_se=math.sqrt((e*e).sum()/(n-2)),
                within1=100*np.mean(np.abs(e)<=1),within2=100*np.mean(np.abs(e)<=2),within3=100*np.mean(np.abs(e)<=3),med_abs=float(np.median(np.abs(e))),
                b_lo=beta[0]-t*math.sqrt(cov[0,0]),b_hi=beta[0]+t*math.sqrt(cov[0,0]),m_lo=beta[1]-t*math.sqrt(cov[1,1]),m_hi=beta[1]+t*math.sqrt(cov[1,1])),e,X
def influence(x,y):
    f,e,X=ols(x,y); n=len(y); H=X@np.linalg.inv(X.T@X)@X.T; h=np.diag(H); p=2
    s2=(e@e)/(n-p); cooks=e**2/(p*s2)*h/(1-h)**2
    s2i=((n-p)*s2-e**2/(1-h))/(n-p-1); stud=e/np.sqrt(s2i*(1-h))
    return cooks,stud
def compute(rows,pop=None):
    CO=list(rows); D={c:derive(rows[c]) for c in CO}; R={}
    for c in CO:
        for k,v in D[c].items(): R[f'{c}|{k}']=v
    T={k:sum(rows[c][k] for c in CO) for k in FIELDS}; st=derive(T)
    for k,v in st.items(): R[f'State|{k}']=v
    R['State|residual_share']=st['dG']-abs(st['dP'])
    R['State|implied_sum']=sum(D[c]['implied'] for c in CO)
    R['State|implied_sum_loss']=sum(D[c]['implied'] for c in CO if D[c]['loss']); R['State|implied_sum_nonloss']=sum(D[c]['implied'] for c in CO if not D[c]['loss'])
    R['State|gapreg_sum']=sum(D[c]['gapreg'] for c in CO)
    g=lambda k:[D[c][k] for c in CO]
    fits={'2022':(g('P22'),g('G22'),None),'2026':(g('P26'),g('G26'),None),'2022_wtd':(g('P22'),g('G22'),g('ballots_2022')),'2026_wtd':(g('P26'),g('G26'),g('ballots_2026')),
          'pooled':(g('P22')+g('P26'),g('G22')+g('G26'),None)}
    for name,(x,y,w) in fits.items():
        f,e,_=ols(x,y,w)
        for k,v in f.items(): R[f'fit|{name}|{k}']=v
        if name in ('2022','2026'):
            t=name[2:]
            for c,ee in zip(CO,e): R[f'{c}|res{t}']=ee; R[f'{c}|fit{t}']=D[c]['G'+t]-ee
    n=len(CO); flag=set()
    for t in ('22','26'):
        cooks,stud=influence(g('P'+t),g('G'+t))
        for c,ck,sd in zip(CO,cooks,stud):
            R[f'{c}|cooks{t}']=ck; R[f'{c}|stud{t}']=sd
            if ck>4/n or abs(sd)>2.5: flag.add(c)
    R['n|narrowed_out']=len(flag); R['n|narrowed_in']=n-len(flag); R['fit|cut']=4/n
    keep=[c for c in CO if c not in flag]
    for t,y in (('22','2022'),('26','2026')):
        f,_,_=ols([D[c]['P'+t] for c in keep],[D[c]['G'+t] for c in keep])
        for k,v in f.items(): R[f'fit|{y}_narrowed|{k}']=v
    # statewide fitted equation for the Locked page: dG = const + mult * drop (drop in points; no /100)
    x=np.array(g('drop')); y=np.array(g('dG')); X=np.c_[np.ones(n),x]; A=np.linalg.inv(X.T@X); b=A@X.T@y; e=y-X@b; s2=e@e/(n-2)
    R.update({'eq|const':b[0],'eq|mult':b[1],'eq|const_se':math.sqrt(s2*A[0,0]),'eq|mult_se':math.sqrt(s2*A[1,1]),'eq|r2':1-(e@e)/((y-y.mean())@(y-y.mean())),'eq|n':n})
    for c in CO: R[f'{c}|eq_pred']=b[0]+b[1]*D[c]['drop']; R[f'{c}|eq_diff']=D[c]['dG']-R[f'{c}|eq_pred']
    R['eq|state_pred']=b[0]+b[1]*st['drop']; R['eq|state_diff']=st['dG']-R['eq|state_pred']
    # counts and summary statistics
    R['n|counties']=n; R['n|loss']=sum(D[c]['loss'] for c in CO); R['n|nonloss']=n-R['n|loss']
    R['n|P_fell']=sum(D[c]['dP']<0 for c in CO); R['n|S_rose']=sum(D[c]['dS']>0 for c in CO); R['n|dG_pos']=sum(D[c]['dG']>0 for c in CO); R['n|dG_neg']=sum(D[c]['dG']<0 for c in CO)
    R['n|regdem_rose']=sum(D[c]['dreg']>0 for c in CO); R['n|dem_rose']=sum(D[c]['ddem']>0 for c in CO); R['n|bal_rose']=sum(D[c]['dbal']>0 for c in CO)
    R['n|implied_neg']=sum(D[c]['implied']<0 for c in CO)
    for k in ('dG','dS','dP','residual'):
        v=[D[c][k] for c in CO if k in D[c]]; R[f'stat|median_{k}']=float(np.median(v)); R[f'stat|mean_{k}']=float(np.mean(v)); R[f'stat|sd_{k}']=float(np.std(v,ddof=1))
    for y,t in (('2022','22'),('2026','26')):
        R[f'ob|{y}|n_DR_gt_ballots']=sum(D[c]['margin_DR'+t]<0 for c in CO); R[f'ob|{y}|n_ballots_gt_reg']=sum(rows[c]['ballots_'+y]>rows[c]['regtot_'+y] for c in CO)
        R[f'ob|{y}|n_ballots_gt_elig']=sum(rows[c]['ballots_'+y]>rows[c]['eligible_'+y] for c in CO); R[f'ob|{y}|n_reg_gt_elig']=sum(rows[c]['regtot_'+y]>rows[c]['eligible_'+y] for c in CO)
        R[f'ob|{y}|n_ballots_gt_reg_elec']=sum(rows[c]['ballots_'+y]>rows[c]['reg_elec_'+y] for c in CO)
        u=[D[c]['under_pct'+t] for c in CO]; R[f'ob|{y}|under_median']=float(np.median(u)); R[f'ob|{y}|under_min']=min(u); R[f'ob|{y}|under_max']=max(u)
    if pop:
        R['n|pop_total']=sum(pop[c] for c in CO)
        for c in CO: R[f'{c}|pop2025']=pop[c]
    return R
def census_pop(path):
    out={}
    for r in csv.DictReader(open(path,encoding='latin-1')):
        if r['SUMLEV']=='050' and r['STATE']=='06': out[r['CTYNAME'].replace(' County','')]=int(r['POPESTIMATE2025'])
    return out

def unprocessed(mode):
    """Statewide row of the SOS Unprocessed Ballots Report. mode 'A': HTML table cells (html.parser); mode 'B': regex on the visible text."""
    R='/workspace/california-elections/raw/2026/rendered/'
    if mode=='A':
        from html.parser import HTMLParser
        class P(HTMLParser):
            def __init__(s): super().__init__(); s.rows=[]; s.cur=None; s.cell=None
            def handle_starttag(s,t,a):
                if t=='tr': s.cur=[]
                if t=='td' and s.cur is not None: s.cell=''
            def handle_endtag(s,t):
                if t=='td' and s.cell is not None: s.cur.append(s.cell.strip()); s.cell=None
                if t=='tr' and s.cur is not None: s.rows.append(s.cur); s.cur=None
            def handle_data(s,d):
                if s.cell is not None: s.cell+=d
        p=P(); p.feed(open(R+'unprocessed_ballots.html').read())
        row=[r for r in p.rows if r and r[0]=='STATEWIDE'][0]; v=[int(x.replace(',','')) if x else None for x in row[1:]]
        return {'raw|unproc_processed':v[0],'raw|unproc_remaining':v[8],'raw|unproc_cure':v[11]}
    import re
    t=open(R+'unprocessed_ballots.txt').read(); l=[x for x in t.split('\n') if x.startswith('STATEWIDE\t')][0].split('\t')
    v=[int(x.replace(',','')) if x.strip() else None for x in l[1:]]
    return {'raw|unproc_processed':v[0],'raw|unproc_remaining':v[8],'raw|unproc_cure':v[11]}
