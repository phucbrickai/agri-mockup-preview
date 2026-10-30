import os,re,shutil,json,html
SRC='/workspace/agri-ux'; OUT='/workspace/agri-mockup-preview'
shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT+'/mockups')
shutil.copy(SRC+'/tokens.css',OUT+'/tokens.css')
shutil.copytree(SRC+'/assets/products',OUT+'/assets/products')
for f in ['simple.css','ext.css','agq1.css','contact-v1.png','contact-v2.png']: shutil.copy(f'{SRC}/mockups/{f}',f'{OUT}/mockups/{f}')
FLOWS=[('Buyer','H1 B3 B5 B8 B9 B10 B11 B14'),('Payment variants','B9 B9q B9m B9f B9w B10'),('Pre-order','B5 B15 B9m B10'),
('Seller','S1 S3 S3e S7 H3 S2 S8 T1 T2'),('B2B buyer / RFQ','H2 X2 X2b C2 X3 TX1 TX2'),('Cooperative (HTX)','H4 C3 C2 C5 E1 E2'),
('Agentic copilot','AG-C1 AG-C2 AG-C3 AG-C4 AG-C5'),('Admin & gov','A1 A0 A2 A3 A4 GV1 GV2'),('States & settings','G1 G2 G3 B3e B8e')]
MAIN={'Buyer','Seller','B2B buyer / RFQ','Cooperative (HTX)','Agentic copilot','Admin & gov','States & settings'}
summary={}
for ver,label in [('v1-classic','v1 Classic'),('v2-agentic','v2 Agentic')]:
  sd=f'{SRC}/mockups/{ver}'; od=f'{OUT}/mockups/{ver}'; os.makedirs(od+'/shots')
  ids=[f[:-5] for f in os.listdir(sd) if f.endswith('.html')]
  order=[];fl=[]
  for n,s in FLOWS:
    seq=[i for i in s.split() if i in ids]
    if len(seq)>1: fl.append((n,seq))
    if n in MAIN: order+= [i for i in seq if i not in order]
  order+=sorted(i for i in ids if i not in order)
  nxt={}  # flow next for wiring
  for n,seq in fl:
    for a,b in zip(seq,seq[1:]): nxt.setdefault(a,b)
  for a,b in {'B14':'H1','B8e':'B3','AG-C5':'X3','T2':'H3','TX2':'H2','E2':'H4','GV2':'A1','B3e':'B3','G3':'H1'}.items():
    if a in ids: nxt.setdefault(a,b)
  shutil.copy(sd+'/style.css',od); shutil.copy(sd+'/qr-l11.png',od)
  for i in ids: shutil.copy(f'{sd}/shots/{i}.png',f'{od}/shots/{i}.png')
  titles={}
  for k,i in enumerate(order):
    h=open(f'{sd}/{i}.html',encoding='utf-8').read()
    t=re.search(r'<title>(.*?)</title>',h).group(1); titles[i]=html.unescape(t.split(' · ')[1] if ' · ' in t else t)
    p=order[k-1]; q=order[(k+1)%len(order)]; f=nxt.get(i,'')
    myflows=[n for n,seq in fl if i in seq]
    bar=(f'<div id="pvbar" style="position:fixed;left:0;right:0;bottom:0;z-index:9999;display:flex;gap:6px;align-items:center;justify-content:center;flex-wrap:wrap;padding:6px;background:#1F1C19;color:#fff;font:13px Inter,sans-serif">'
      f'<a style="color:#fff" href="../../index.html">⌂ Index</a> · <a style="color:#fff" href="index.html">{label}</a> · '
      f'<a style="color:#fff" rel="prev" href="{p}.html">◀ {p}</a> <b>{k+1}/{len(order)} {i}</b> <a style="color:#fff" rel="next" href="{q}.html">{q} ▶</a>'
      +(f' · <a style="color:#FFB37A" href="{f}.html">Flow next: {f} →</a>' if f else '')+f'<span style="opacity:.6">{", ".join(myflows)}</span></div>')
    js=('<script>(function(){var N=%s;document.querySelectorAll("button,a[href=\'#\']").forEach(function(e){if(e.closest("#pvbar"))return;var t=e.textContent||"";var g=/Thêm vào giỏ|Mua ngay/.test(t)?"B8.html":N;if(!g)return;'
        'if(e.tagName=="A"){e.setAttribute("href",g)}else{e.style.cursor="pointer";e.setAttribute("data-href",g);e.addEventListener("click",function(){location.href=g})}})})()</script>')%json.dumps(f+'.html' if f else '')
    # explicit add-to-cart on B5 if no cart link
    h=h.replace('</body>',bar+'<div style="height:44px"></div>'+js+'</body>')
    open(f'{od}/{i}.html','w',encoding='utf-8').write(h)
  # version index
  cards=''.join(f'<a class="c" href="{i}.html"><img loading="lazy" src="shots/{i}.png"><span><b>{k+1}. {i}</b> {html.escape(titles[i])}</span></a>' for k,i in enumerate(order))
  fls=''.join(f'<li><b>{n}:</b> '+' → '.join(f'<a href="{i}.html">{i}</a>' for i in seq)+'</li>' for n,seq in fl)
  CSS='body{font-family:Inter,sans-serif;margin:24px;background:#FAF8F5;color:#1F1C19}a{color:#D95E0F}.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:16px}.c{display:flex;flex-direction:column;gap:4px;text-decoration:none;color:inherit;font-size:13px}.c img{width:100%;border:1px solid #E6E1DA;border-radius:12px;aspect-ratio:375/812;object-fit:cover;object-position:top}'
  open(f'{od}/index.html','w').write(f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>{label} · {len(order)} screens</title><style>{CSS}</style></head><body><p><a href="../../index.html">← All versions</a></p><h1>{label} · {len(order)} screens</h1><h2>Flows</h2><ul>{fls}</ul><p>Overview: <a href="../contact-{ver[:2]}.png">contact sheet</a></p><h2>All screens</h2><div class="g">{cards}</div></body></html>')
  summary[ver]=(label,len(order),order[0],fl)
idx=''.join(f'<li><a href="mockups/{v}/index.html"><b>{l}</b></a> — {n} screens · <a href="mockups/{v}/{s}.html">start at {s}</a> · <a href="mockups/contact-{v[:2]}.png">overview</a><br><a href="mockups/{v}/index.html"><img src="mockups/contact-{v[:2]}.png" style="max-width:480px;border:1px solid #ddd;margin:8px 0"></a></li>' for v,(l,n,s,_) in summary.items())
open(OUT+'/index.html','w').write(f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>Nông Sản Việt · simplified mockups preview</title></head><body style="font-family:Inter,sans-serif;margin:24px"><h1>Nông Sản Việt · simplified mockups (Una, approved)</h1><p>Static clickable preview. Each screen has a bottom bar: Index · prev/next · next step in flow. Unwired buttons follow the flow.</p><ul>{idx}</ul></body></html>')
for v,(l,n,s,fl) in summary.items(): print(v,n,[x[0] for x in fl])
