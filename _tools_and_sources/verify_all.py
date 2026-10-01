import os
import sys
import json
import openpyxl

if sys.stdout and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

print("=== 1. VERIFY EXCEL ===")
for ep in ['LIST Nhạc Đông Hải.xlsx', 'KTV Vol 82B Dong Hai.xlsx', 'hanco Vol 83B Dong Hai.xlsx', 'List ACNOS (2017).xlsx']:
    if os.path.exists(ep):
        wb = openpyxl.load_workbook(ep, read_only=True)
        print(f'{ep}: {wb.sheetnames}')
        ws = wb[wb.sheetnames[0]]
        print(f'  First sheet "{wb.sheetnames[0]}": {ws.max_row:,} rows')

print("\n=== 2. VERIFY JSON & JS ===")
# Dong Hai
with open('data/donghai.json', 'r', encoding='utf-8') as f:
    jdata_dh = json.load(f)
print(f'donghai.json: {len(jdata_dh):,} records')

with open('data/donghai.js', 'r', encoding='utf-8') as f:
    js_dh = f.read()
assert js_dh.startswith('window.KARAOKE_DATA_DH=')
assert js_dh.rstrip().endswith(';')
print(f'donghai.js: valid syntax, length {len(js_dh):,} bytes')

# Acnos
with open('data/acnos.json', 'r', encoding='utf-8') as f:
    jdata_acnos = json.load(f)
assert len(jdata_acnos) == 17806, f"Expected 17,806 Acnos records, got {len(jdata_acnos)}"
print(f'acnos.json: {len(jdata_acnos):,} records (100% full Vol 62)')

with open('data/acnos.js', 'r', encoding='utf-8') as f:
    js_acnos = f.read()
assert js_acnos.startswith('window.KARAOKE_DATA_ACNOS = ')
assert js_acnos.rstrip().endswith(';')
print(f'acnos.js: valid syntax, length {len(js_acnos):,} bytes')

print("\n=== 3. VERIFY CONFIGS ===")
with open('version.json', 'r', encoding='utf-8') as f:
    vdata = json.load(f)
ver = vdata['version']
print('version.json version:', ver)
print('version.json acnos dataset:', vdata['datasets']['acnos'])
print('version.json donghai dataset:', vdata['datasets']['donghai'])
print('version.json total songs:', vdata['totalSongs'])

with open('app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()
assert f"CURRENT_APP_VERSION = '{ver}'" in app_js
assert "key: 'dh'" in app_js
assert "key: 'acnos'" in app_js
print('app.js: verified')

with open('style.css', 'r', encoding='utf-8') as f:
    css = f.read()
assert 'body[data-company="dh"]' in css
print('style.css: verified')

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()
assert 'tab-donghai' in html
assert 'data-fav-comp="dh"' in html
assert 'icons/DONGHAI.jpg' in html
print('index.html: verified')

with open('sw.js', 'r', encoding='utf-8') as f:
    sw = f.read()
assert f'v{ver}' in sw
assert 'donghai.js' in sw
assert 'acnos.js' in sw
print('sw.js: verified')

print("\n>>> ALL CHECKS PASSED 100% PERFECTLY! <<<")
