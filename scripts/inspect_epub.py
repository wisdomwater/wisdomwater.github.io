import zipfile,sys,os
epub='output/number-go-up/number-go-up.epub'
if not os.path.exists(epub):
    print('EPUB not found:', epub)
    sys.exit(1)
with zipfile.ZipFile(epub) as z:
    names = z.namelist()
    print('TOTAL FILES:', len(names))
    # Show first 20 files
    for i,n in enumerate(names[:50]):
        info = z.getinfo(n)
        comp = 'stored' if info.compress_type==zipfile.ZIP_STORED else 'deflated'
        print(f'{i:03d}: {n} ({comp})')
    # Check mimetype first
    if names[0] != 'mimetype':
        print('\nERROR: first zip entry is not "mimetype" (found: %s)'%names[0])
    else:
        mi = z.getinfo('mimetype')
        if mi.compress_type != zipfile.ZIP_STORED:
            print('\nERROR: mimetype is compressed (should be stored)')
        else:
            print('\nmimetype is first entry and stored — OK')
    # Read container.xml
    if 'META-INF/container.xml' in names:
        cont = z.read('META-INF/container.xml').decode('utf-8')
        print('\n--- META-INF/container.xml ---')
        print(cont)
        # try to extract rootfile
        import re
        m = re.search(r'full-path\s*=\s*"([^"]+)"', cont)
        if m:
            opf = m.group(1)
            print('\nOPF path:', opf)
            if opf in names:
                print('\n--- OPF file head ---')
                s = z.read(opf).decode('utf-8', errors='replace')
                print('\n'.join(s.splitlines()[:200]))
            else:
                print('OPF file listed in container not found in zip')
        else:
            print('Could not find rootfile full-path in container.xml')
    else:
        print('META-INF/container.xml missing')

    # Quick scan: check for duplicate ids in XHTML files
    import re
    ids = {}
    for n in names:
        if n.endswith('.xhtml') or n.endswith('.html') or n.endswith('.htm'):
            try:
                txt = z.read(n).decode('utf-8', errors='replace')
            except Exception as e:
                print('Failed reading', n, e)
                continue
            for mid in re.findall(r'id\s*=\s*"([^"]+)"', txt):
                ids[mid] = ids.get(mid,0)+1
    dup = {k:v for k,v in ids.items() if v>1}
    if dup:
        print('\nDuplicate HTML ids detected (may break EPUB/KDP):')
        for k,v in list(dup.items())[:50]:
            print(k, v)
    else:
        print('\nNo duplicate HTML ids found')
        # Print a sample of all ids found (first 80)
        if ids:
            print('\nSample of collected HTML ids (name:count):')
            i = 0
            for k,v in sorted(ids.items(), key=lambda x: -x[1]):
                print(f' {k}: {v}')
                i += 1
                if i>80:
                    break
        # If specific duplicates found, print locations
        # Also list any files containing the string 'number-go-up' to locate duplicates
        found = []
        for n in names:
            if n.endswith('.xhtml') or n.endswith('.html'):
                txt = z.read(n).decode('utf-8', errors='replace')
                if 'number-go-up' in txt:
                    found.append(n)
        if found:
            print('\nFiles containing the text "number-go-up":')
            for n in found:
                print(' -', n)
