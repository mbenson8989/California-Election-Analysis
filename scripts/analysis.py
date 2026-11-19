"""California governor 2022 vs 2026, all 58 counties. Runs ONLY on the pass-A table after asserting pass B is identical on every
analysis figure. P = Democratic registered voters / Total Registered, CA SOS 15-day Report of Registration (close of registration:
as of Oct 24, 2022 and Oct 19, 2026). S = Democratic governor votes / total ballots cast (SOV 2022 Total Voters; 2026 County
Reporting Status Ballots Cast, UNOFFICIAL)."""
import pandas as pd, numpy as np, json, statsmodels.api as sm, statsmodels.formula.api as smf
from scipy import stats
W='/workspace/california-elections/'; V=W+'verification/'; O=W+'repo/'
A=pd.read_csv(V+'passA_counties.csv',index_col='county'); B=pd.read_csv(V+'passB_counties.csv',index_col='county')
rep=json.load(open(V+'compare_report.json')); assert rep['CLEAN']
USED=[k for k in B.columns if not k.startswith('reg_elec')]
assert (A[USED]==B.loc[A.index,USED]).all().all(), 'pass A/B disagree on an analysis figure'
o=A.copy(); N=len(o); assert N==58
c=pd.read_csv(W+'raw/census/co-est2025-alldata.csv',encoding='latin-1',dtype={'STATE':str,'COUNTY':str,'SUMLEV':str})
c=c[(c.SUMLEV=='050')&(c.STATE=='06')]; c.index=c.CTYNAME.str.replace(' County','')
o['pop2025']=c.POPESTIMATE2025.reindex(o.index); assert o.pop2025.notna().all()
o=o.sort_values('pop2025',ascending=False)
for y,t in (('2022','22'),('2026','26')):
    o['S'+t]=100*o[f'dem_{y}']/o[f'ballots_{y}']
    o['P'+t]=100*o[f'regdem_{y}']/o[f'regtot_{y}']
    o['G'+t]=o['S'+t]-o['P'+t]
o['dS']=o.S26-o.S22; o['dP']=o.P26-o.P22; o['dG']=o.G26-o.G22
o['loss']=o.regdem_2026<o.regdem_2022
o['residual']=np.where(o.loss,o.dG-o.dP.abs(),np.nan)
o['implied_extra_votes']=o.dem_2026-o.S22/100*o.ballots_2026
o['gap_reg_scaled']=o.dem_2026-o.dem_2022*(o.regdem_2026/o.regdem_2022)
def fit(y,x,w=None):
    X=sm.add_constant(np.asarray(x,float)/100); r=(sm.WLS(np.asarray(y,float),X,weights=w) if w is not None else sm.OLS(np.asarray(y,float),X)).fit()
    res=np.asarray(y)-r.fittedvalues; ci=r.conf_int()
    return dict(n=int(len(y)),m=float(r.params[1]),m_se=float(r.bse[1]),m_ci=[float(ci[1,0]),float(ci[1,1])],b=float(r.params[0]),b_se=float(r.bse[0]),b_ci=[float(ci[0,0]),float(ci[0,1])],
        r2=float(r.rsquared),resid_se=float(np.sqrt(np.sum(res**2)/(len(y)-2))),within1=float(np.mean(np.abs(res)<=1)),within2=float(np.mean(np.abs(res)<=2)),within3=float(np.mean(np.abs(res)<=3)),med_abs=float(np.median(np.abs(res)))),r
F={}
F['2022'],r22=fit(o.G22,o.P22); F['2026'],r26=fit(o.G26,o.P26)
F['2022_wtd'],_=fit(o.G22,o.P22,o.ballots_2022); F['2026_wtd'],_=fit(o.G26,o.P26,o.ballots_2026)
F['pooled'],_=fit(np.r_[o.G22,o.G26],np.r_[o.P22,o.P26])
o['fit22']=np.asarray(r22.fittedvalues); o['res22']=o.G22-o.fit22; o['fit26']=np.asarray(r26.fittedvalues); o['res26']=o.G26-o.fit26
L=pd.DataFrame(dict(G=np.r_[o.G22,o.G26],P=np.r_[o.P22,o.P26]/100,yr=np.r_[np.zeros(N),np.ones(N)]))
ri=smf.ols('G~P*yr',L).fit(); F['year_interaction']=dict(d_intercept=float(ri.params['yr']),p_d_intercept=float(ri.pvalues['yr']),d_slope=float(ri.params['P:yr']),p_d_slope=float(ri.pvalues['P:yr']))
F['dG_on_dP'],_=fit(o.dG,o.dP)
NAR={}
for t,rr in (('22',r22),('26',r26)):
    inf=rr.get_influence(); NAR[t]=pd.DataFrame(dict(cooks=inf.cooks_distance[0],stud=inf.resid_studentized_external,lev=inf.hat_matrix_diag),index=o.index)
cut=4/N
flag=sorted(set(NAR['22'].index[(NAR['22'].cooks>cut)|(NAR['22'].stud.abs()>2.5)])|set(NAR['26'].index[(NAR['26'].cooks>cut)|(NAR['26'].stud.abs()>2.5)]),key=lambda x:-o.loc[x,'pop2025'])
k=o.drop(flag); F['2022_narrowed'],_=fit(k.G22,k.P22); F['2026_narrowed'],_=fit(k.G26,k.P26)
NARROW=dict(rule=f"Cook's distance > 4/n ({cut:.3f}) or |externally studentized residual| > 2.5, in either year's fit",counties=flag,
  detail={c_:dict(cooks22=float(NAR['22'].loc[c_,'cooks']),stud22=float(NAR['22'].loc[c_,'stud']),cooks26=float(NAR['26'].loc[c_,'cooks']),stud26=float(NAR['26'].loc[c_,'stud']),
          P22=float(o.loc[c_,'P22']),G22=float(o.loc[c_,'G22']),P26=float(o.loc[c_,'P26']),G26=float(o.loc[c_,'G26']),res22=float(o.loc[c_,'res22']),res26=float(o.loc[c_,'res26'])) for c_ in flag})
FLOOR=o.sort_values('P22').head(5); CEIL=o.sort_values('dG',ascending=False).head(5)
lr=stats.linregress(np.log10(o.pop2025),o.dG); lrS=stats.linregress(np.log10(o.pop2025),o.dS); lrP=stats.linregress(np.log10(o.pop2025),o.dP)
K=dict(floor_rule='five lowest 2022 Democratic registration shares P2022 (most Republican registration baseline)',floor=FLOOR.index.tolist(),ceiling_rule='five largest ΔG',ceiling=CEIL.index.tolist(),
  floor_by_dG=o.dG.idxmin(),ceiling_by_dG=o.dG.idxmax(),lowest5_dG=o.sort_values('dG').head(5).index.tolist(),lowest5_S22=o.sort_values('S22').head(5).index.tolist(),
  mean_dG=float(o.dG.mean()),median_dG=float(o.dG.median()),sd_dG=float(o.dG.std()),sd_dS=float(o.dS.std()),median_dS=float(o.dS.median()),n_pos=int((o.dG>0).sum()),n_neg=int((o.dG<0).sum()),
  n_loss=int(o.loss.sum()),loss_counties=o.index[o.loss].tolist(),nonloss_counties=o.index[~o.loss].tolist(),n_P_fell=int((o.dP<0).sum()),n_S_rose=int((o.dS>0).sum()),
  size_slope=dict(slope=float(lr.slope),r=float(lr.rvalue),p=float(lr.pvalue)),size_dS=dict(r=float(lrS.rvalue),p=float(lrS.pvalue)),size_dP=dict(r=float(lrP.rvalue),p=float(lrP.pvalue)),
  median_residual=float(np.nanmedian(o.residual)) if o.loss.any() else None)
T=o.sum(numeric_only=True)
PO=dict(S22=100*T.dem_2022/T.ballots_2022,S26=100*T.dem_2026/T.ballots_2026,P22=100*T.regdem_2022/T.regtot_2022,P26=100*T.regdem_2026/T.regtot_2026)
PO.update(G22=PO['S22']-PO['P22'],G26=PO['S26']-PO['P26']); PO['dG']=PO['G26']-PO['G22']; PO['dP']=PO['P26']-PO['P22']; PO['dS']=PO['S26']-PO['S22']
PO['implied_extra_pooled']=(PO['S26']-PO['S22'])/100*T.ballots_2026; PO['implied_extra_sum']=float(o.implied_extra_votes.sum())
PO['implied_extra_sum_loss']=float(o.implied_extra_votes[o.loss].sum()); PO['implied_extra_sum_nonloss']=float(o.implied_extra_votes[~o.loss].sum())
PO['residual_pooled']=PO['dG']-abs(PO['dP']) if PO['dP']<0 else None
PO['gap_reg_scaled_sum']=float(o.gap_reg_scaled.sum())
PO['totals']={k_:int(T[k_]) for k_ in USED+['reg_elec_2022','reg_elec_2026']}
s=max(-PO['dP'],0)/100; Nb=T.ballots_2026; p=PO['S26']/100
PO['offset']={f'cushion_{cu}':dict(switched=float((s+cu/100)*Nb),added=float((s+cu/100)*Nb/(1-p+s+cu/100))) for cu in (0,1,2)} if s>0 else 'P did not fall statewide; no offset need'
TX={}
for y in ('2022','2026'):
    m1=o[f'ballots_{y}']-o[f'dem_{y}']-o[f'rep_{y}']
    TX[y]=dict(DR_gt_ballots=o.index[m1<0].tolist(),
               ballots_gt_reg_15day=o.index[o[f'ballots_{y}']>o[f'regtot_{y}']].tolist(),
               ballots_gt_reg_turnout_report=o.index[o[f'ballots_{y}']>o[f'reg_elec_{y}']].tolist(),
               ballots_gt_eligible=o.index[o[f'ballots_{y}']>o[f'eligible_{y}']].tolist(),
               regtot_gt_eligible=o.index[o[f'regtot_{y}']>o[f'eligible_{y}']].tolist(),
               min_margin_ballots_minus_DR=dict(county=m1.idxmin(),votes=int(m1.min())),
               undervote_pct_median=float((100*m1/o[f'ballots_{y}']).median()),undervote_pct_range=[float((100*m1/o[f'ballots_{y}']).min()),float((100*m1/o[f'ballots_{y}']).max())],
               undervote_pct_statewide=float(100*(T[f'ballots_{y}']-T[f'govtotal_{y}'])/T[f'ballots_{y}']),
               max_turnout_of_reg_15day=dict(county=(o[f'ballots_{y}']/o[f'regtot_{y}']).idxmax(),pct=float(100*(o[f'ballots_{y}']/o[f'regtot_{y}']).max())),
               max_reg_of_eligible=dict(county=(o[f'regtot_{y}']/o[f'eligible_{y}']).idxmax(),pct=float(100*(o[f'regtot_{y}']/o[f'eligible_{y}']).max())))
o['flag']=''
for c_ in FLOOR.index: o.loc[c_,'flag']='floor'
for c_ in CEIL.index: o.loc[c_,'flag']=(o.loc[c_,'flag']+'; ' if o.loc[c_,'flag'] else '')+'ceiling'
for c_ in flag: o.loc[c_,'flag']=(o.loc[c_,'flag']+'; ' if o.loc[c_,'flag'] else '')+'narrowed-out'
o.to_pickle('/tmp/ca_o.pkl')
cols=['pop2025','flag','ballots_2022','dem_2022','rep_2022','govtotal_2022','regdem_2022','regrep_2022','regtot_2022','eligible_2022','reg_elec_2022','S22','P22','G22',
      'ballots_2026','dem_2026','rep_2026','govtotal_2026','regdem_2026','regrep_2026','regtot_2026','eligible_2026','reg_elec_2026','S26','P26','G26','dS','dP','dG','loss','residual','implied_extra_votes','gap_reg_scaled','fit22','res22','fit26','res26']
out=o[cols].copy()
out.insert(1,'status_2026','2026 UNOFFICIAL: CA SOS electionresults.sos.ca.gov semi-final unofficial results, statewide as of Nov 19, 2026 1:59 p.m. PT; counties report final results by Dec 4, SOS certifies Dec 11, 2026')
out.insert(2,'P_definition','P = Democratic registered voters / Total Registered, CA SOS 15-day Report of Registration (Oct 24, 2022; Oct 19, 2026)')
out.round(6).to_csv(O+'data/CA_Governor_2022_2026_DeltaG_by_County.csv')
J=dict(fits=F,narrow=NARROW,K=K,pooled=PO,overballot=TX)
json.dump(J,open(O+'data/CA_results_summary.json','w'),indent=1,default=lambda x: x.item() if hasattr(x,'item') else str(x))
print(json.dumps(J,indent=0,default=lambda x: x.item() if hasattr(x,'item') else str(x))[:7000])
print(o[['P22','S22','G22','P26','S26','G26','dS','dP','dG','loss','residual','implied_extra_votes']].round(2).to_string())
