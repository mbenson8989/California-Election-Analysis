"""58-county PDF (+ xlsx) in the layout of Nebraska_93_County_Democratic_Registration_and_Vote_Change.pdf: openpyxl workbook with live formulas,
rendered to PDF by LibreOffice. Every displayed cell is re-checked against the raw files by check_pdf_cells.py."""
import pandas as pd, subprocess, os, shutil
W='/workspace/california-elections/'; OUT=W+'repo/'; FN='California_58_County_Democratic_Registration_and_Vote_Change'
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.utils import get_column_letter as L
# Same verified county table the analysis uses (pass A; compare_passes.py asserts pass B identical on every figure used here)
rep=__import__('json').load(open(W+'verification/compare_report.json')); assert rep['CLEAN']
d=pd.read_csv(W+'verification/passA_counties.csv').rename(columns={'regdem_2022':'reg_dem_2022','regdem_2026':'reg_dem_2026','dem_2022':'D_2022','dem_2026':'D_2026','regtot_2022':'reg_tot_2022','regtot_2026':'reg_tot_2026'})
d['R26']=d.reg_dem_2026/d.reg_tot_2026; d=d.sort_values(['R26','county'],ascending=[False,True]).reset_index(drop=True); assert len(d)==58
wb=Workbook(); ws=wb.active; ws.title='Registration and Votes'; w2=wb.create_sheet('Dem Vote Share')
HF=PatternFill('solid',fgColor='1F2A44'); HFont=Font(bold=True,color='FFFFFF',name='Calibri',size=10)
REG=PatternFill('solid',fgColor='DDEBF7'); VOT=PatternFill('solid',fgColor='FCE4D6'); TOT=PatternFill('solid',fgColor='E7E6E6')
thin=Side(style='thin',color='BFBFBF'); B=Border(top=thin,bottom=thin,left=thin,right=thin)
INT='#,##0;-#,##0;0'; SINT='+#,##0;-#,##0;0'; PCT='0.0%'; SPCT='+0.0%;-0.0%;0.0%'; PTS='+0.00;-0.00;0.00'
regrose=set(d.county[d.reg_dem_2026>d.reg_dem_2022]); vfell=set(d.county[d.D_2026<d.D_2022])
lst=lambda S:', '.join(c for c in d.county if c in S) or 'none'
NOTE1=('Sorted by 2026 Democratic share of registration (Democratic registered voters ÷ Total Registered, CA SOS 15-day Report of Registration as of October 19, 2026), highest first. '
       f'{d.county[0]} leads by share; {d.sort_values("reg_dem_2026",ascending=False).county.iloc[0]} leads by raw Democratic registration.')
NOTE2=('*2026 figures are UNOFFICIAL and not certified by the California Secretary of State (SOS semi-final unofficial results, electionresults.sos.ca.gov, statewide as of November 19, 2026, 1:59 p.m. PT; retrieved November 19, 2026; SOS certifies December 11, 2026). '
       '2022 votes and ballots: SOS 2022 Statement of Vote (certified). Registration: SOS 15-day Reports of Registration as of October 24, 2022 and October 19, 2026 (close of registration). '
       'Total ballots = total ballots cast in the county (all contests), not governor votes. Votes are votes for the Democratic governor candidate, not a count of registered Democrats who voted.')
def hdr(sh,row,cols):
    for j,c in enumerate(cols,1):
        x=sh.cell(row,j,c); x.fill=HF; x.font=HFont; x.alignment=Alignment(wrap_text=True,horizontal='center',vertical='center'); x.border=B
    sh.row_dimensions[row].height=42
def title(sh,t,ncol):
    sh['A1']=t; sh['A1'].font=Font(bold=True,size=13,name='Calibri')
    for r,txt in [(2,NOTE1),(3,NOTE2)]:
        sh.cell(r,1,txt).font=Font(italic=True,size=9); sh.cell(r,1).alignment=Alignment(wrap_text=True,vertical='top')
        sh.merge_cells(start_row=r,start_column=1,end_row=r,end_column=ncol); sh.row_dimensions[r].height=30
# ---- Tab 1
c1=['County','Dem Reg Share 2026 %','Dem Reg 2022 (Oct 24)','Dem Reg 2026 (Oct 19)','Reg Change #','Reg Change %','Dem Gov Votes 2022','Dem Gov Votes 2026*','Vote Change #','Vote Change % (on 2022 base)','Total Ballots 2022','Total Ballots 2026*','Ballot Change #','Ballot Change %']
title(ws,'California 58 Counties — Democratic Registration, Democratic Governor Votes and Total Ballots, 2022 vs 2026*',len(c1))
ws['A4']='Legend:'; ws['A4'].font=Font(bold=True,size=9)
ws['B4']='Democratic registration rose from 2022 (row shaded blue)' if regrose else 'Democratic registration rose: none'; ws['B4'].fill=REG
ws['F4']=(f'Democratic governor votes fell ({lst(vfell)})' if vfell else 'Democratic governor votes fell: no county'); ws['F4'].fill=VOT
ws.merge_cells('B4:E4'); ws.merge_cells('F4:J4')
for k in ('B4','F4'): ws[k].font=Font(size=9)
H=5; hdr(ws,H,c1); r0=H+1
for i,r in enumerate(d.itertuples()):
    R=r0+i
    vals=[r.county,f"='Dem Vote Share'!G{R}",r.reg_dem_2022,r.reg_dem_2026,f'=D{R}-C{R}',f'=E{R}/C{R}',r.D_2022,r.D_2026,f'=H{R}-G{R}',f'=I{R}/G{R}',r.ballots_2022,r.ballots_2026,f'=L{R}-K{R}',f'=M{R}/K{R}']
    for j,v in enumerate(vals,1):
        x=ws.cell(R,j,v); x.border=B; x.font=Font(size=10)
        x.number_format={2:PCT,6:SPCT,10:SPCT,14:SPCT,5:SINT,9:SINT,13:SINT}.get(j,INT if j>1 else 'General')
        if r.county in regrose: x.fill=REG
        if r.county in vfell: x.fill=VOT
RT=r0+len(d); last=RT-1
tv=['Statewide total',f"='Dem Vote Share'!G{RT}"]+[f'=SUM({L(j)}{r0}:{L(j)}{last})' if j in (3,4,7,8,11,12) else None for j in range(3,15)]
for j,v in enumerate(tv,1):
    if j in (5,9,13): v=f'={L(j-1)}{RT}-{L(j-2)}{RT}'
    if j in (6,10,14): v=f'={L(j-1)}{RT}/{L(j-4) if False else L(j-3)}{RT}'
    x=ws.cell(RT,j,v); x.font=Font(bold=True,size=10); x.fill=TOT; x.border=B
    x.number_format={2:PCT,6:SPCT,10:SPCT,14:SPCT,5:SINT,9:SINT,13:SINT}.get(j,INT if j>1 else 'General')
ws.freeze_panes=ws.cell(r0,2)
for j,wd in enumerate([16,11,12,12,10,10,12,12,11,12,12,12,11,10],1): ws.column_dimensions[L(j)].width=wd
# ---- Tab 2
c2=['County','Dem Share of Ballots 2022 %','Dem Share of Ballots 2026* %','Change (pts)','Dem Share of Registration 2022 %','Total Registered 2022 (Oct 24)','Dem Share of Registration 2026 %','Total Registered 2026 (Oct 19)']
title(w2,'Democratic Governor Votes as a Share of Total Ballots, and Democratic Share of Registration, 2022 vs 2026*',len(c2))
w2['A4']='Share of ballots = Democratic governor votes ÷ total ballots cast. Share of registration = Democratic registered voters ÷ Total Registered. Change (pts) = 2026 share minus 2022 share, in percentage points.'
w2['A4'].font=Font(italic=True,size=9); w2.merge_cells('A4:H4'); w2['A4'].alignment=Alignment(wrap_text=True); w2.row_dimensions[4].height=26
hdr(w2,H,c2)
RV="'Registration and Votes'!"
for i,r in enumerate(d.itertuples()):
    R=r0+i
    vals=[f'={RV}A{R}',f'={RV}G{R}/{RV}K{R}',f'={RV}H{R}/{RV}L{R}',f'=(C{R}-B{R})*100',f'={RV}C{R}/F{R}',r.reg_tot_2022,f'={RV}D{R}/H{R}',r.reg_tot_2026]
    for j,v in enumerate(vals,1):
        x=w2.cell(R,j,v); x.border=B; x.font=Font(size=10)
        x.number_format={2:PCT,3:PCT,4:PTS,5:PCT,7:PCT}.get(j,INT if j>1 else 'General')
        if r.county in regrose: x.fill=REG
        if r.county in vfell: x.fill=VOT
tv=['Statewide total',f'={RV}G{RT}/{RV}K{RT}',f'={RV}H{RT}/{RV}L{RT}',f'=(C{RT}-B{RT})*100',f'={RV}C{RT}/F{RT}',f'=SUM(F{r0}:F{last})',f'={RV}D{RT}/H{RT}',f'=SUM(H{r0}:H{last})']
for j,v in enumerate(tv,1):
    x=w2.cell(RT,j,v); x.font=Font(bold=True,size=10); x.fill=TOT; x.border=B
    x.number_format={2:PCT,3:PCT,4:PTS,5:PCT,7:PCT}.get(j,INT if j>1 else 'General')
w2.freeze_panes=w2.cell(r0,2)
for j,wd in enumerate([16,13,13,10,14,14,14,14],1): w2.column_dimensions[L(j)].width=wd
for sh in (ws,w2):
    sh.page_setup.orientation='landscape'; sh.page_setup.paperSize=sh.PAPERSIZE_LETTER
    sh.page_setup.fitToWidth=1; sh.page_setup.fitToHeight=0; sh.sheet_properties.pageSetUpPr.fitToPage=True
    sh.print_title_rows=f'{H}:{H}'; sh.print_options.horizontalCentered=True
    for m in ('left','right'): setattr(sh.page_margins,m,0.4)
    sh.page_margins.top=sh.page_margins.bottom=0.5
    sh.oddFooter.center.text='Page &P of &N'; sh.oddFooter.left.text='*2026 figures unofficial, not SOS-certified'
for sh in (ws,w2): sh.oddFooter.left.text='*2026 figures UNOFFICIAL, not SOS-certified'
wb.save(OUT+FN+'.xlsx')
tmp='/tmp/ca_pdf_build'; shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp)
subprocess.run(['soffice','--headless','--convert-to','pdf','--outdir',tmp,OUT+FN+'.xlsx'],check=True,capture_output=True)
shutil.copy(tmp+'/'+FN+'.pdf',OUT+FN+'.pdf'); print('built',OUT+FN+'.pdf',len(d),'counties; reg rose:',sorted(regrose),'votes fell:',sorted(vfell))
