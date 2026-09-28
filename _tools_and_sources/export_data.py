import sqlite3
import zipfile
import glob
import json
import os
import sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

# Ensure output directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('data/lyrics', exist_ok=True)
os.makedirs('icons', exist_ok=True)

apk_path = glob.glob('*.apk')[0]
print(f"Using APK: {apk_path}")

# 1. Export Database tables
conn = sqlite3.connect('temp_kokv1.db')
cur = conn.cursor()

tables = {
    'a': 'arirang',
    'm': 'musiccore',
    'c': 'california',
    'v': 'vietktv'
}

stats = {}

for tbl, fname in tables.items():
    cur.execute(f"SELECT id, maso, title, intro, author, lan, g, v FROM {tbl} ORDER BY maso ASC")
    rows = cur.fetchall()
    stats[fname] = len(rows)
    print(f"Exporting {tbl} ({fname}): {len(rows)} songs...")
    
    # Save as JSON
    json_path = f'data/{fname}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, separators=(',', ':'))
        
    # Save as JS for zero-CORS offline execution (file:///)
    var_name = f"KARAOKE_DATA_{tbl.upper()}"
    js_path = f'data/{fname}.js'
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(f"window.{var_name} = ")
        json.dump(rows, f, ensure_ascii=False, separators=(',', ':'))
        f.write(";")

conn.close()

# 2. Extract and decode all lyrics from APK
print("\nExtracting lyrics from APK assets...")
def rot13_custom(text):
    res = []
    for ch in text:
        code = ord(ch)
        if 97 <= code <= 109:    # a-m
            res.append(chr(code + 13))
        elif 110 <= code <= 122: # n-z
            res.append(chr(code - 13))
        elif 65 <= code <= 77:   # A-M
            res.append(chr(code + 13))
        elif 78 <= code <= 90:   # N-Z
            res.append(chr(code - 13))
        elif ch == '|':
            res.append('\n')
        else:
            res.append(ch)
    return ''.join(res)

all_lyrics = {}
with zipfile.ZipFile(apk_path, 'r') as z:
    asset_files = [n for n in z.namelist() if n.startswith('assets/') and n[7:].isdigit()]
    for n in asset_files:
        song_id = int(n[7:])
        raw = z.read(n).decode('utf-8', 'ignore')
        if raw.startswith('\ufeff'):
            raw = raw[1:]
        all_lyrics[song_id] = rot13_custom(raw)

    # Also extract best icons
    icon_data = z.read('res/6o.png')
    with open('icons/icon-192.png', 'wb') as f:
        f.write(icon_data)
        
    # Create 512x512 icon from 192x192
    im = Image.open('icons/icon-192.png')
    im512 = im.resize((512, 512), Image.Resampling.LANCZOS)
    im512.save('icons/icon-512.png')
    im32 = im.resize((32, 32), Image.Resampling.LANCZOS)
    im32.save('icons/favicon-32.png')

print(f"Total lyrics extracted: {len(all_lyrics)}")

# Split lyrics into chunks of 1000 songs each (e.g. 0-999, 1000-1999, etc.)
chunk_size = 1000
max_id = max(all_lyrics.keys()) if all_lyrics else 0
num_chunks = (max_id // chunk_size) + 1
print(f"Splitting lyrics into {num_chunks} chunks (size {chunk_size})...")

for chunk_idx in range(num_chunks):
    start_id = chunk_idx * chunk_size
    end_id = start_id + chunk_size
    chunk_data = {k: v for k, v in all_lyrics.items() if start_id <= k < end_id}
    
    # Save chunk JSON
    with open(f'data/lyrics/lyrics_{chunk_idx}.json', 'w', encoding='utf-8') as f:
        json.dump(chunk_data, f, ensure_ascii=False, separators=(',', ':'))
        
    # Save chunk JS
    with open(f'data/lyrics/lyrics_{chunk_idx}.js', 'w', encoding='utf-8') as f:
        f.write(f"window.KARAOKE_LYRICS_{chunk_idx} = ")
        json.dump(chunk_data, f, ensure_ascii=False, separators=(',', ':'))
        f.write(";")

print("\n--- Summary ---")
for k, v in stats.items():
    print(f"  {k}: {v} songs")
print(f"  Total lyrics: {len(all_lyrics)}")
print("Data export complete!")
