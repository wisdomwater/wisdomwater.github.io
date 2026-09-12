import zipfile,os,re
epub='output/number-go-up/number-go-up.epub'
if not os.path.exists(epub):
    print('EPUB not found')
    raise SystemExit(1)
with zipfile.ZipFile(epub) as z:
    for n in z.namelist():
        if n.endswith('.xhtml') or n.endswith('.html'):
            txt = z.read(n).decode('utf-8', errors='replace')
            for i,line in enumerate(txt.splitlines(),1):
                if 'number-go-up' in line:
                    print(n, f':{i}:', line.strip())
