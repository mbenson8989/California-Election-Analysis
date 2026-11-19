"""Display formats shared by build_wiki.py (writer) and verify_wiki.py (checker). Formatting only; no computation.
i: 1,234   s: +1,234 / −1,234   f1/f2/f3/f4: 1.23   g1/g2/g4: +1.23 / −1.23   p1/p2: 12.34%   gp2: +12.34% / −12.34%   pct0: 12% (share 0-100)"""
M='−'
def F(v,f):
    if f=='pct0': return f'{v:.0f}%'
    if f.startswith('gp'):
        d=int(f[2]); s=f'{abs(v):.{d}f}%'; return ('+' if v>0 else M if v<0 else '')+s
    if f=='i': return f'{int(round(v)):,}'
    if f=='s':
        n=int(round(v)); return ('+' if n>0 else M if n<0 else '')+f'{abs(n):,}'
    if f[0]=='f': return f'{v:,.{int(f[1])}f}'.replace('-',M)
    if f[0]=='g':
        d=int(f[1]); s=f'{abs(v):,.{d}f}'; z=float(s.replace(',',''))==0
        return s if z else ('+' if v>0 else M)+s
    if f[0]=='p': return f'{v:.{int(f[1])}f}%'.replace('-',M)
    if f.startswith('gp'):
        d=int(f[2]); s=f'{abs(v):.{d}f}%'; return ('+' if v>0 else M if v<0 else '')+s
    if f=='pct0': return f'{v:.0f}%'
    raise ValueError(f)
