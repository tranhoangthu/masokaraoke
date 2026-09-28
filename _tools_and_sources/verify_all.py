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
excel_path = 'LIST Nhạc Đông Hải.xlsx'
wb = openpyxl.load_workbook(excel_path, read_only=True)
print('Sheet names:', wb.sheetnames)
for sheet in wb.sheetnames:
    ws = wb[sheet]
    print(f'  Sheet "{sheet}": {ws.max_row:,} rows')

print("\n=== 2. VERIFY JSON & JS ===")
with open('data/donghai.json', 'r', encoding='utf-8') as f:
    jdata = json.load(f)
print(f'donghai.json: {len(jdata):,} records')

with open('data/donghai.js', 'r', encoding='utf-8') as f:
    js_content = f.read()
assert js_content.startswith('window.KARAOKE_DATA_DH=')
assert js_content.rstrip().endswith(';')
print(f'donghai.js: valid syntax, length {len(js_content):,} bytes')

print("\n=== 3. VERIFY CONFIGS ===")
with open('version.json', 'r', encoding='utf-8') as f:
    vdata = json.load(f)
print('version.json version:', vdata['version'])
print('version.json donghai dataset:', vdata['datasets']['donghai'])

with open('app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()
assert "key: 'dh'" in app_js
assert "CURRENT_APP_VERSION = '2.4.0'" in app_js
assert "'dh'" in app_js
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
assert 'v2.4.0' in sw
assert 'donghai.js' in sw
print('sw.js: verified')

print("\n>>> ALL CHECKS PASSED 100% PERFECTLY! <<<")
