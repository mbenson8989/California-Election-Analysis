"""Pass-A input for 2026: CA SOS results-site data API (the JSON the results site itself loads), saved byte-for-byte.
 api.sos.ca.gov/returns/governor/county/<slug>  (58 counties; each also carries the statewide record)
 api.sos.ca.gov/returns/maps/status/gubernatorial-general  (County Reporting Status: registered voters + ballots cast per county)
Usage: fetch_2026_api.py OUTDIR"""
import sys,os,json,hashlib,datetime,urllib.request
O=sys.argv[1]; os.makedirs(O,exist_ok=True); log=[]
S=[l.strip() for l in open('/workspace/california-elections/raw/2026/county_slugs.txt') if l.strip()]; assert len(S)==58
U=['https://api.sos.ca.gov/returns/maps/status/gubernatorial-general']+[f'https://api.sos.ca.gov/returns/governor/county/{s}' for s in S]
for u in U:
    b=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=60).read()
    fn=u.split('api.sos.ca.gov/')[1].replace('/','_')+'.json'; open(os.path.join(O,fn),'wb').write(b)
    log.append(dict(url=u,file=fn,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),fetched=datetime.datetime.now().astimezone().isoformat()))
json.dump(log,open(os.path.join(O,'fetch_log.json'),'w'),indent=1); print(len(log),'files')
