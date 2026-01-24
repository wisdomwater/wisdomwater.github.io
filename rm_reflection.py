import os
import re

for file in os.listdir('external/the-interior-castle/chapters'):
    fullpath = os.path.join('external/the-interior-castle/chapters', file)
    
    print(f'Processing {fullpath}...')
    with open(fullpath, 'r', encoding='utf-8') as f:
        content = f.read()
        content = re.sub(r'    \*', "> *", content, flags=re.DOTALL)
    with open(fullpath, 'w', encoding='utf-8') as f:
        f.write(content)
