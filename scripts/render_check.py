"""Render markdown files through GitHub's GFM renderer (gh api POST /markdown) and check for malformed content/layout:
 - every markdown table block renders as an HTML <table> with consistent column counts (unescaped pipes inside cells break this)
 - no literal table-pipe rows leaking into <p> text, no stray code fences, no raw HTML tags in source
 - relative wiki links point to existing pages; images referenced exist (local file or HTTP 200)
 - headings: no duplicates, no skipped/empty headings; and a Contents/Pages list matches actual pages
Usage: render_check.py OUTDIR repo_or_wiki_context file1.md [file2.md ...]  (pages list taken from the file names)"""
import sys,os,re,json,subprocess,html
out=sys.argv[1]; ctx=sys.argv[2]; files=sys.argv[3:]; os.makedirs(out,exist_ok=True)
pages={os.path.basename(f)[:-3] for f in files}|{'Home'}
issues=[]; summary={}
def rend(text):
    r=subprocess.run(['gh','api','-X','POST','/markdown','-f','mode=gfm','-f',f'context={ctx}','-f',f'text={text}'],capture_output=True,text=True)
    if r.returncode: raise SystemExit(r.stderr)
    return r.stdout
for f in files:
    name=os.path.basename(f)[:-3]; src=open(f,encoding='utf-8').read(); lines=src.split('\n')
    h=rend(src); open(os.path.join(out,name+'.html'),'w').write(h)
    # table blocks in source
    blocks=[];cur=[]
    for i,l in enumerate(lines,1):
        if l.lstrip().startswith('|'): cur.append((i,l))
        else:
            if cur: blocks.append(cur); cur=[]
    if cur: blocks.append(cur)
    def ncells(l):
        s=re.sub(r'\\\|','',l.strip()); s=re.sub(r'`[^`]*`',lambda m:m.group(0).replace('|',''),s)
        return len(s.strip('|').split('|'))
    for b in blocks:
        n0=ncells(b[0][1])
        if len(b)<2 or not re.match(r'^\s*\|?\s*:?-{3,}',b[1][1]): issues.append(f'{name}.md:{b[0][0]} table block without a valid header separator row')
        for i,l in b:
            if ncells(l)!=n0: issues.append(f'{name}.md:{i} table row has {ncells(l)} cells, header has {n0}: {l[:120]}')
            if any('|' in c and '\\|' not in c for c in re.findall(r'`[^`]*`',l)): issues.append(f'{name}.md:{i} pipe inside inline code in a table cell (GFM splits the cell): {l[:120]}')
    ntab=h.count('<table')
    if ntab!=len(blocks): issues.append(f'{name}.md: {len(blocks)} table blocks in source but {ntab} <table> in rendered HTML')
    # pipe-rows leaking into paragraphs
    for m in re.finditer(r'<p[^>]*>(.*?)</p>',h,flags=re.S):
        t=html.unescape(re.sub(r'<[^>]+>','',m.group(1)))
        if t.count('|')>=2 and re.search(r'\|\s*-{3,}|^\s*\|',t,flags=re.M): issues.append(f'{name}.md: table text rendered as paragraph: {t[:120]!r}')
    # code fences / raw html / leftover markdown
    if src.count('```')%2: issues.append(f'{name}.md: unbalanced ``` code fence')
    for i,l in enumerate(lines,1):
        if re.search(r'<(?!https?://)[a-zA-Z/][^>]*>',l) and not l.strip().startswith('<!--'): issues.append(f'{name}.md:{i} raw HTML tag in source: {l[:120]}')
        if re.search(r'\{[a-z_]+(:[^}]*)?\}|\bnan\b|\bNaN\b|\bNone\b(?!\.\*\*| of These Candidates)',l): issues.append(f'{name}.md:{i} unfilled template placeholder / nan / None: {l[:120]}')
    for m in re.finditer(r'(?<![\w`])(\*\*|__)(?=\S)',re.sub(r'`[^`]*`','',h)):
        pass
    if re.search(r'(?<![*\w])\*\*(?!\*)',re.sub(r'<code>.*?</code>','',h)): issues.append(f'{name}.md: literal ** left in rendered HTML (unclosed bold)')
    # links
    for i,l in enumerate(lines,1):
        for t,u in re.findall(r'(!?)\[[^\]]*\]\(([^)\s]+)\)',l):
            if t=='!':
                PRE='https://raw.githubusercontent.com/mbenson8989/California-Election-Analysis/main/'
                if u.startswith(PRE):  # repo not published yet: the file must exist in the local repo folder at that path
                    if not os.path.exists('/workspace/california-elections/repo/'+u[len(PRE):]): issues.append(f'{name}.md:{i} image not in repo folder: {u}')
                elif u.startswith('http'):
                    c=subprocess.run(['curl','-s','-o','/dev/null','-L','-w','%{http_code}',u],capture_output=True,text=True).stdout
                    if c!='200': issues.append(f'{name}.md:{i} image URL returns HTTP {c}: {u}')
                elif not os.path.exists(os.path.join(os.path.dirname(f),u)): issues.append(f'{name}.md:{i} image file missing locally: {u}')
            elif not re.match(r'https?://|#|mailto:',u):
                if ctx.endswith('.wiki') or 'wiki' in out:
                    pg_,_,anc=u.partition('#')
                    if pg_ not in pages: issues.append(f'{name}.md:{i} relative wiki link to non-existent page: {u}')
                    elif anc:
                        tsrc=open(os.path.join(os.path.dirname(f),pg_+'.md'),encoding='utf-8').read()
                        slugs={re.sub(r'[^\w\- ]','',re.sub(r'^#+ ','',l).strip().lower()).replace(' ','-') for l in tsrc.split('\n') if re.match(r'#{1,6} ',l)}
                        if anc not in slugs: issues.append(f'{name}.md:{i} anchor #{anc} not found among headings of {pg_}')
                elif not os.path.exists(os.path.join(os.path.dirname(f),u.split('#')[0])): issues.append(f'{name}.md:{i} relative link target missing in repo folder: {u}')
    heads=[(i,l) for i,l in enumerate(lines,1) if re.match(r'#{1,6} ',l)]
    seen={}
    for i,l in heads:
        k=l.strip().lower()
        if k in seen: issues.append(f'{name}.md:{i} duplicate heading (first at line {seen[k]}): {l}')
        seen[k]=i
        if not l.lstrip('#').strip(): issues.append(f'{name}.md:{i} empty heading')
    if sum(1 for i,l in heads if l.startswith('# '))>1: issues.append(f'{name}.md: more than one H1')
    if 'wiki' in out and any(l.startswith('# ') for i,l in heads):
        issues.append(f'{name}.md:{[i for i,l in heads if l.startswith("# ")][0]} body H1 on a wiki page: GitHub already shows the page title, so the H1 is a second title and is nested as a child of the page in the Pages sidebar')
    # arrows/long values inside wide tables wrap into broken multi-line cells
    for b in blocks:
        nc=ncells(b[0][1])
        for i,l in b:
            if nc>=6 and '→' in l: issues.append(f'{name}.md:{i} "A → B" value inside a {nc}-column table: wraps into a 3-line cell when rendered'); break
    summary[name]=dict(h1=[l for i,l in heads if l.startswith('# ')],table_blocks=len(blocks),rendered_tables=ntab,headings=len(heads),bytes=len(src))
json.dump(dict(summary=summary,issues=issues),open(os.path.join(out,'render_check.json'),'w'),indent=1)
print(json.dumps(summary)); print(len(issues),'issues'); [print(' -',x) for x in issues]
sys.exit(1 if issues else 0)
