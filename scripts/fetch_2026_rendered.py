"""Pass-B input for 2026: the RENDERED CA SOS results pages (what a reader sees), captured as HTML + visible text.
Opens electionresults.sos.ca.gov in Chrome (site sits behind Imperva/Incapsula, which rejects curl) and saves the
Governor county table, the County Reporting Status page (ballots cast / registration per county), the voter-turnout
map page and the Unprocessed Ballots Status page to raw/2026/rendered/. Also logs every XHR/fetch the pages make."""
import os,datetime,json
from playwright.sync_api import sync_playwright
O='/workspace/california-elections/raw/2026/rendered/'; os.makedirs(O,exist_ok=True); log=[]; xhr=[]
PAGES=[('home','https://electionresults.sos.ca.gov/'),('governor','https://electionresults.sos.ca.gov/returns/governor'),
       ('county_status','https://electionresults.sos.ca.gov/returns/status'),('voter_turnout_map','https://electionresults.sos.ca.gov/returns/maps/voter-turnout'),
       ('unprocessed_ballots','https://electionresults.sos.ca.gov/unprocessed-ballots-status')]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=False,args=['--no-sandbox','--disable-blink-features=AutomationControlled'],ignore_default_args=['--enable-automation'])
    pg=b.new_page(viewport={'width':1500,'height':1200})
    pg.on('request',lambda r: xhr.append(dict(url=r.url,type=r.resource_type)) if r.resource_type in ('xhr','fetch') else None)
    for name,u in PAGES:
        pg.goto(u,wait_until='load',timeout=90000); pg.wait_for_timeout(9000)
        open(O+name+'.html','w').write(pg.content()); t=pg.inner_text('body'); open(O+name+'.txt','w').write(t)
        log.append(dict(name=name,url=pg.url,captured=datetime.datetime.now().astimezone().isoformat(),chars=len(t)))
    # Governor county pages (rendered table a reader sees), 58 counties
    for sl in [l.strip() for l in open('/workspace/california-elections/raw/2026/county_slugs.txt') if l.strip()]:
        u='https://electionresults.sos.ca.gov/returns/governor/county/'+sl
        if os.path.exists(O+'gov_county_'+sl+'.txt') and 'Party Preference' in open(O+'gov_county_'+sl+'.txt').read(): continue  # resume
        for k in range(3):
            pg.goto(u,wait_until='load',timeout=90000); pg.wait_for_timeout(4000); t=pg.inner_text('body')
            if 'Party Preference' in t: break
        open(O+'gov_county_'+sl+'.txt','w').write(t)
        log.append(dict(name='gov_county_'+sl,url=pg.url,captured=datetime.datetime.now().astimezone().isoformat(),chars=len(t)))
    b.close()
lp=O+'capture_log.json'; old=json.load(open(lp)) if os.path.exists(lp) else {}
json.dump(dict(runs=old.get('runs',[dict(pages=old.get('pages',[]),xhr=old.get('xhr',[]))] if old else [])+[dict(pages=log,xhr=xhr)]),open(lp,'w'),indent=1); print(len(log),'pages captured')
