from zipfile import ZipFile
z=ZipFile('output/number-go-up/number-go-up.epub')
for p in ['EPUB/text/ch001.xhtml','EPUB/text/ch002.xhtml','EPUB/nav.xhtml','EPUB/text/title_page.xhtml']:
    print('\n====',p)
    s=z.read(p).decode('utf-8',errors='replace')
    for i,line in enumerate(s.splitlines()[:120],1):
        print('{:03d}: {}'.format(i,line))
