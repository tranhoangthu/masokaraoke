import json
import pymupdf
import re
import os

with open('arirang_ocr_lines.json', 'r', encoding='utf-8-sig') as f:
    pages_ocr = json.load(f)

doc = pymupdf.open('PDF/arirang/BAIHATCOVOCALVACHORUS.pdf')

with open('data/arirang.json', 'r', encoding='utf-8') as f:
    arirang_db = json.load(f)

db_codes = set(s[1] for s in arirang_db)
print(f"Total songs in Arirang DB: {len(db_codes)}")

code_regex = re.compile(r'\b(5\d{4}|5\d\s*\d{3}|5\d{2}\s*\d{2}|5\d{3}\s*\d)\b')

vocal_songs = set()
chorus_songs = set()

for p_idx in range(len(doc)):
    page_key = f"page_{p_idx:02d}.png"
    if page_key not in pages_ocr:
        continue
    
    ocr_lines = pages_ocr[page_key]
    codes_on_page = []
    for l in ocr_lines:
        for m in code_regex.finditer(l):
            c = int(re.sub(r'\s+', '', m.group(1)))
            if c in db_codes and c not in codes_on_page:
                codes_on_page.append(c)
                
    # Get image rects on this page
    p = doc[p_idx]
    image_rects = []
    for img_info in p.get_images():
        xref = img_info[0]
        base = doc.extract_image(xref)
        w = base['width']
        rects = p.get_image_rects(xref)
        for r in rects:
            if r.y0 < 800:
                t = 'chorus' if w >= 40 else 'vocal'
                image_rects.append({'type': t, 'y0': r.y0, 'y1': r.y1})
                
    # Deduplicate image rects that are on the same Y position
    unique_rects = []
    for r in sorted(image_rects, key=lambda x: x['y0']):
        if not any(abs(ur['y0'] - r['y0']) < 8 for ur in unique_rects):
            unique_rects.append(r)
            
    print(f"Page {p_idx:02d}: {len(codes_on_page)} codes, {len(unique_rects)} image rows")
    
    if len(unique_rects) == 0:
        # Fallback based on page range
        if p_idx < 32:
            for c in codes_on_page: chorus_songs.add(c)
        else:
            for c in codes_on_page: vocal_songs.add(c)
    elif len(codes_on_page) <= len(unique_rects):
        # Match by row index
        for i, c in enumerate(codes_on_page):
            if i < len(unique_rects):
                if unique_rects[i]['type'] == 'vocal':
                    vocal_songs.add(c)
                else:
                    chorus_songs.add(c)
            else:
                if p_idx < 32: chorus_songs.add(c)
                else: vocal_songs.add(c)
    else:
        # If more codes than rects, match closest Y or use page default
        for i, c in enumerate(codes_on_page):
            if i < len(unique_rects) and unique_rects[i]['type'] == 'vocal':
                vocal_songs.add(c)
            elif p_idx >= 32:
                vocal_songs.add(c)
            else:
                chorus_songs.add(c)

print(f"\nFinal extracted: Vocal songs = {len(vocal_songs)}, Chorus songs = {len(chorus_songs)}")

# Save tags to JSON
tags_map = {
    'vocal': sorted(list(vocal_songs)),
    'chorus': sorted(list(chorus_songs))
}
with open('data/arirang_tags.json', 'w', encoding='utf-8') as f:
    json.dump(tags_map, f, indent=2)

# Update arirang_db records:
# Schema: [id, maso, title, intro, author, lan, g, v, vocal_flag, chorus_flag]
# Or add badge into intro so it works seamlessly with all existing frontends:
# If vocal: add ' [🎤 Có lời ca]'
# If chorus: add ' [💋 Có tiếng bè]'
updated_rows = []
for row in arirang_db:
    m = row[1]
    is_vocal = 1 if m in vocal_songs else 0
    is_chorus = 1 if m in chorus_songs else 0
    tag_str = ""
    if is_vocal and is_chorus:
        tag_str = " [🎤 Có lời ca | 💋 Có bè]"
    elif is_vocal:
        tag_str = " [🎤 Có lời ca]"
    elif is_chorus:
        tag_str = " [💋 Có tiếng bè]"
        
    intro = row[3]
    if tag_str and tag_str not in intro:
        intro = (intro + tag_str).strip()
        
    # [id, maso, title, intro, author, lan, g, v, is_vocal, is_chorus]
    new_row = [row[0], row[1], row[2], intro, row[4], row[5], row[6], row[7], is_vocal, is_chorus]
    updated_rows.append(new_row)

with open('data/arirang.json', 'w', encoding='utf-8') as f:
    json.dump(updated_rows, f, ensure_ascii=False, separators=(',', ':'))

with open('data/arirang.js', 'w', encoding='utf-8') as f:
    f.write("window.KARAOKE_DATA_A = ")
    json.dump(updated_rows, f, ensure_ascii=False, separators=(',', ':'))
    f.write(";\n")
    f.write(f"window.ARIRANG_VOCAL_CODES = new Set({list(vocal_songs)});\n")
    f.write(f"window.ARIRANG_CHORUS_CODES = new Set({list(chorus_songs)});\n")

print("Saved updated data/arirang.json and data/arirang.js!")
