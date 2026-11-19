import pandas as pd, numpy as np, json, textwrap
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
O='/workspace/california-elections/repo/'; o=pd.read_pickle('/tmp/ca_o.pkl'); J=json.load(open(O+'data/CA_results_summary.json'))
N=len(o); x=np.arange(N); names=list(o.index); DPI=150
FOOT=("P = Democratic registered voters ÷ Total Registered, CA Secretary of State 15-day Report of Registration (as of October 24, 2022 and October 19, 2026). "
      "S = Dem governor votes ÷ total ballots cast. G = S − P.\nSource: CA Secretary of State: 2022 Statement of Vote (certified); "
      "2026 UNOFFICIAL semi-final results (electionresults.sos.ca.gov, statewide as of November 19, 2026, 1:59 p.m. PT; SOS certifies December 11, 2026). Population: Census Vintage 2025 (sort order only).")
def foot(fig):
    wd=int(fig.get_figwidth()*17); fig.text(0.01,0.005,'\n'.join(textwrap.fill(l,wd) for l in FOOT.split('\n')),fontsize=7,color='#444',va='bottom')
CEIL=J['K']['ceiling']; FLOOR=J['K']['floor']; NAR=J['narrow']['counties']
WIDE=(20,8.5)
def col(c,default='#9aa5b1'): return '#c0392b' if c in CEIL else ('#1f4e9a' if c in FLOOR else default)
# 1 slope
fig,ax=plt.subplots(figsize=(11,22)); LAB=[]
for c,r in o.iterrows():
    cl=col(c); lw=2 if cl!='#9aa5b1' else 0.9
    ax.plot([0,1],[r.G22,r.G26],color=cl,lw=lw,alpha=0.9 if lw>1 else 0.6,marker='o',ms=3)
    LAB.append((r.G26,f"{c} (ΔG {r.dG:+.2f})",cl))
LAB.sort(); last=-999
for y,t,cl in LAB:
    yy=max(y,last+0.42); last=yy; ax.annotate(t,(1,y),xytext=(1.05,yy),fontsize=8,va='center',color=cl,arrowprops=dict(arrowstyle='-',color=cl,lw=0.5))
ax.axhline(0,color='#333',lw=0.6); ax.set_xticks([0,1]); ax.set_xticklabels(['2022','2026*']); ax.set_xlim(-0.1,1.5)
ax.set_ylabel('G = S − P (points)'); ax.set_title('California governor: county G, 2022 → 2026* (58 counties)\nRed = 5 ceiling counties (largest ΔG); blue = 5 floor counties (lowest 2022 Dem registration share)\n*2026 UNOFFICIAL')
fig.subplots_adjust(bottom=0.06,top=0.95); foot(fig); fig.savefig(O+'CA_Slope_G2022_to_G2026.png',dpi=DPI); plt.close()
# 2 dG by population
fig,ax=plt.subplots(figsize=WIDE)
ax.bar(x,o.dG,color=[col(c,'#e67e22' if v>0 else '#7f8c8d') for c,v in o.dG.items()]); ax.axhline(0,color='#333',lw=0.7)
for i,(c,v) in enumerate(o.dG.items()): ax.text(i,v+(0.15 if v>0 else -0.15),f'{v:+.1f}',ha='center',va='bottom' if v>0 else 'top',fontsize=6.5)
ax.set_xticks(x); ax.set_xticklabels(names,rotation=70,ha='right',fontsize=8); ax.set_xlim(-1,N); ax.set_ylabel('ΔG = G2026 − G2022 (points)')
ax.set_title(f'California governor: ΔG by county, largest population (left) to smallest. *2026 UNOFFICIAL.\nCeiling (red): {", ".join(CEIL)}. Floor (blue): {", ".join(FLOOR)}.',fontsize=10)
fig.subplots_adjust(bottom=0.27); foot(fig); fig.savefig(O+'CA_DeltaG_by_Population.png',dpi=DPI); plt.close()
# 3 components
fig,ax=plt.subplots(figsize=WIDE); w=0.4
ax.bar(x-w/2,o.dS,w,color='#2c7fb8',label='ΔS: change in Dem share of ballots (2026 − 2022)')
ax.bar(x+w/2,-o.dP,w,color='#d95f0e',label='−ΔP: minus the change in Dem registration share')
ax.plot(x,o.dG,'k_',ms=14,mew=2,label='ΔG = ΔS − ΔP'); ax.axhline(0,color='#333',lw=0.7)
ax.set_xticks(x); ax.set_xticklabels(names,rotation=70,ha='right',fontsize=8); ax.set_xlim(-1,N); ax.set_ylabel('points'); ax.legend(loc='upper right',fontsize=8)
ax.set_title(f'What ΔG is made of in California: ΔS ranges {o.dS.min():+.2f} to {o.dS.max():+.2f} (median {o.dS.median():+.2f}); the registration-share change ΔP ranges {o.dP.min():+.2f} to {o.dP.max():+.2f}. Largest population left. *2026 UNOFFICIAL.',fontsize=10)
fig.subplots_adjust(bottom=0.27); foot(fig); fig.savefig(O+'CA_DeltaG_Components_dS_vs_dP_by_Population.png',dpi=DPI); plt.close()
# 4 stacked share + P
fig,ax=plt.subplots(figsize=WIDE)
base=np.minimum(o.S22,o.S26); ax.bar(x,base,color='#5b8bd0',label='Dem share of ballots kept (lower of 2022/2026)')
ax.bar(x,np.maximum(o.dS,0),bottom=base,color='#e67e22',label='2026 gain in Dem share of ballots')
ax.bar(x,np.maximum(-o.dS,0),bottom=o.S26,color='#bbbbbb',label='2026 drop in Dem share of ballots')
ax.scatter(x,o.P22,marker='v',color='#1f4e9a',zorder=3,label='P 2022 (Dem registration share, 15-day report Oct 24, 2022)'); ax.scatter(x,o.P26,marker='^',color='#c0392b',zorder=3,label='P 2026 (15-day report Oct 19, 2026)')
ax.set_xticks(x); ax.set_xticklabels(names,rotation=70,ha='right',fontsize=8); ax.set_xlim(-1,N); ax.set_ylim(0,95); ax.set_ylabel('%'); ax.legend(loc='upper right',fontsize=8)
ax.set_title('California governor: Democratic share of ballots (bars) and Democratic registration share P (markers), largest population left. *2026 UNOFFICIAL.',fontsize=10)
fig.subplots_adjust(bottom=0.27); foot(fig); fig.savefig(O+'CA_Stacked_Share_and_Registration_by_Population.png',dpi=DPI); plt.close()
# 5 forward fit
fig,axs=plt.subplots(1,2,figsize=(17,8.5),sharey=True)
for ax,t,y in ((axs[0],'22','2022'),(axs[1],'26','2026')):
    f=J['fits'][y]; fn=J['fits'][y+'_narrowed']
    for c,r in o.iterrows():
        ax.scatter(r['P'+t],r['G'+t],color=col(c,'#555'),s=45,edgecolor='k' if c in NAR else 'none',lw=1.5,zorder=3)
        ax.annotate(c,(r['P'+t],r['G'+t]),fontsize=7,xytext=(3,3),textcoords='offset points')
    xx=np.linspace(10,70,10); ax.plot(xx,f['m']*xx/100+f['b'],'k-',label=f"all 58: G = {f['m']:.2f}·(P/100) {f['b']:+.2f}, R² {f['r2']:.2f}")
    ax.plot(xx,fn['m']*xx/100+fn['b'],'k--',label=f"narrowed (n={fn['n']}): m {fn['m']:.2f}, b {fn['b']:+.2f}, R² {fn['r2']:.2f}")
    ax.axhline(0,color='#999',lw=0.5); ax.set_xlabel('P: Dem registration share (%)'); ax.set_title(y+('*' if y=='2026' else '')); ax.legend(fontsize=8,loc='upper left')
axs[0].set_ylabel('G = S − P (points)')
fig.suptitle('California forward fit (CA-only constants): G vs P. Black outline = narrowed-out counties. Red = ceiling, blue = floor. *2026 UNOFFICIAL.'); fig.subplots_adjust(bottom=0.15); foot(fig)
fig.savefig(O+'CA_Forward_Fit_G_vs_P_2022_2026.png',dpi=DPI); plt.close()
# 6 dG vs dP
fig,ax=plt.subplots(figsize=(11,9)); f=J['fits']['dG_on_dP']
for c,r in o.iterrows():
    ax.scatter(r.dP,r.dG,color=col(c,'#555'),s=45); ax.annotate(c,(r.dP,r.dG),fontsize=7,xytext=(3,3),textcoords='offset points')
xx=np.linspace(o.dP.min()-0.3,o.dP.max()+0.3,10); ax.plot(xx,f['m']*xx/100+f['b'],'k-',label=f"ΔG = {f['m']/100:.3f}·ΔP {f['b']:+.2f}  (R² {f['r2']:.2f})")
ax.plot(xx,-xx,color='#999',ls=':',label='ΔG = −ΔP (ΔS = 0)')
ax.axhline(0,color='#999',lw=0.5); ax.legend(fontsize=8)
ax.set_xlabel('ΔP: change in Dem registration share (points)'); ax.set_ylabel('ΔG (points)')
ax.set_title(f'California: ΔG against the registration-share change ΔP. P fell in {int((o.dP<0).sum())} of 58 counties.\nCounties above the dotted line had ΔS > 0. *2026 UNOFFICIAL.')
fig.subplots_adjust(bottom=0.14); foot(fig); fig.savefig(O+'CA_DeltaG_vs_DeltaP_Scatter.png',dpi=DPI); plt.close()
# 7 residual + implied extra votes
fig,axs=plt.subplots(2,1,figsize=(20,11),sharex=True)
axs[0].bar(x,o.residual,color=[col(c,'#2c7fb8') for c in o.index]); axs[0].axhline(0,color='#333',lw=0.7); axs[0].set_ylabel('residual = ΔG − |ΔP| (points)')
for i,v in enumerate(o.residual):
    if v==v: axs[0].text(i,v+(0.08 if v>0 else -0.08),f'{v:+.1f}',ha='center',va='bottom' if v>0 else 'top',fontsize=6.5)
axs[1].bar(x,o.implied_extra_votes,color=[col(c,'#2c7fb8') for c in o.index]); axs[1].axhline(0,color='#333',lw=0.7); axs[1].set_yscale('symlog',linthresh=100); axs[1].set_ylabel('implied extra votes (symlog scale)')
for i,v in enumerate(o.implied_extra_votes): axs[1].text(i,v,f'{v:+,.0f}',ha='center',va='bottom' if v>0 else 'top',fontsize=5.5,rotation=90)
axs[1].set_xticks(x); axs[1].set_xticklabels(names,rotation=70,ha='right',fontsize=8)
fig.suptitle(f"California residual step: only the {int(o.loss.sum())} counties whose Democratic registration count fell run it (no bar = non-loss county). Residual = ΔG − |ΔP|. Implied extra votes = D2026 − S2022 × ballots2026 (hypothesis). *2026 UNOFFICIAL.",fontsize=10)
fig.subplots_adjust(bottom=0.17); foot(fig); fig.savefig(O+'CA_Residual_and_Implied_Votes_by_Population.png',dpi=DPI); plt.close()
# 8 overballot
fig,axs=plt.subplots(2,1,figsize=(20,13))
w=0.4; m22=100*(o.ballots_2022-o.govtotal_2022)/o.ballots_2022; m26=100*(o.ballots_2026-o.govtotal_2026)/o.ballots_2026
axs[0].bar(x-w/2,m22,w,color='#7f8c8d',label='2022'); axs[0].bar(x+w/2,m26,w,color='#2c7fb8',label='2026*'); axs[0].axhline(0,color='r',lw=1,label='over-vote line (Dem + Rep governor votes = ballots)')
axs[0].set_ylabel('(ballots − governor votes) as % of ballots'); axs[0].legend(fontsize=8); axs[0].set_title('Governor votes vs ballots cast')
t22=100*o.ballots_2022/o.regtot_2022; t26=100*o.ballots_2026/o.regtot_2026
axs[1].bar(x-w/2,t22,w,color='#7f8c8d',label='2022: ballots ÷ 15-day registration'); axs[1].bar(x+w/2,t26,w,color='#2c7fb8',label='2026*: ballots ÷ 15-day registration'); axs[1].axhline(100,color='r',lw=1,label='over-ballot line (ballots = registered)')
axs[1].set_ylabel('ballots cast as % of registered voters'); axs[1].set_ylim(0,110); axs[1].legend(fontsize=8,loc='lower right'); axs[1].set_title('Ballots cast vs registered voters')
for a in axs: a.set_xticks(x); a.set_xticklabels(names,rotation=70,ha='right',fontsize=8); a.set_xlim(-1,N)
fig.suptitle('California over-ballot check: every bar on the left is above zero and every bar on the right is below 100% in both years. Largest population left. *2026 UNOFFICIAL.',fontsize=10)
fig.subplots_adjust(bottom=0.14,hspace=0.45); foot(fig); fig.savefig(O+'CA_Overballot_Check_by_Population.png',dpi=DPI); plt.close()
print('ok')
