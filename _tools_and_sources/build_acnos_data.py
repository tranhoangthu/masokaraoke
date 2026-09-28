import pypdf
import re
import os
import json
import time

vni_map = {
    'aù': 'á', 'aø': 'à', 'aû': 'ả', 'aõ': 'ã', 'aï': 'ạ',
    'aé': 'ắ', 'aè': 'ằ', 'aú': 'ẳ', 'aü': 'ẵ', 'aë': 'ặ',
    'aá': 'ấ', 'aà': 'ầ', 'aå': 'ẩ', 'aã': 'ẫ', 'aä': 'ậ',
    'eù': 'é', 'eø': 'è', 'eû': 'ẻ', 'eõ': 'ẽ', 'eï': 'ẹ',
    'eá': 'ế', 'eà': 'ề', 'eå': 'ể', 'eã': 'ễ', 'eä': 'ệ',
    'où': 'ó', 'oø': 'ò', 'oû': 'ỏ', 'oõ': 'õ', 'oï': 'ọ',
    'oá': 'ố', 'oà': 'ồ', 'oå': 'ổ', 'oã': 'ỗ', 'oä': 'ộ',
    'ôù': 'ớ', 'ôø': 'ờ', 'ôû': 'ở', 'ôõ': 'ỡ', 'ôï': 'ợ',
    'uù': 'ú', 'uø': 'ù', 'uû': 'ủ', 'uõ': 'ũ', 'uï': 'ụ',
    'öù': 'ứ', 'öø': 'ừ', 'öû': 'ử', 'öõ': 'ữ', 'öï': 'ự',
    'yù': 'ý', 'yø': 'ỳ', 'yû': 'ỷ', 'yõ': 'ỹ', 'î': 'ỵ',
    'AÙ': 'Á', 'AØ': 'À', 'AÛ': 'Ả', 'AÕ': 'Ã', 'AÏ': 'Ạ',
    'AÉ': 'Ắ', 'AÈ': 'Ằ', 'AÚ': 'Ẳ', 'AÜ': 'Ẵ', 'AË': 'Ặ',
    'AÁ': 'Ấ', 'AÀ': 'Ầ', 'AÅ': 'Ẩ', 'AÃ': 'Ẫ', 'AÄ': 'Ậ',
    'EÙ': 'É', 'EØ': 'È', 'EÛ': 'Ẻ', 'EÕ': 'Ẽ', 'EÏ': 'Ẹ',
    'EÁ': 'Ế', 'EÀ': 'Ề', 'EÅ': 'Ể', 'EÃ': 'Ễ', 'EÄ': 'Ệ',
    'OÙ': 'Ó', 'OØ': 'Ò', 'OÛ': 'Ỏ', 'OÕ': 'Õ', 'OÏ': 'Ọ',
    'OÁ': 'Ố', 'OÀ': 'Ồ', 'OÅ': 'Ổ', 'OÃ': 'Ỗ', 'OÄ': 'Ộ',
    'ÔÙ': 'Ớ', 'ÔØ': 'Ờ', 'ÔÛ': 'Ở', 'ÔÕ': 'Ỡ', 'ÔÏ': 'Ợ',
    'UÙ': 'Ú', 'UØ': 'Ù', 'UÛ': 'Ủ', 'UÕ': 'Ũ', 'UÏ': 'Ụ',
    'ÖÙ': 'Ứ', 'ÖØ': 'Ừ', 'ÖÛ': 'Ử', 'ÖÕ': 'Ữ', 'ÖÏ': 'Ự',
    'YÙ': 'Ý', 'YØ': 'Ỳ', 'YÛ': 'Ỷ', 'YÕ': 'Ỹ', 'Î': 'Ỵ',
    'aâ': 'â', 'AÂ': 'Â',
    'aê': 'ă', 'AÊ': 'Ă',
    'eâ': 'ê', 'EÂ': 'Ê',
    'oâ': 'ô', 'OÂ': 'Ô',
    'ô': 'ơ', 'Ô': 'Ơ',
    'ö': 'ư', 'Ö': 'Ư',
    'ñ': 'đ', 'Ñ': 'Đ'
}

vni_keys = sorted(vni_map.keys(), key=len, reverse=True)
vni_pattern = re.compile('|'.join(re.escape(k) for k in vni_keys))

def vni_to_unicode(text):
    if not text: return ""
    return vni_pattern.sub(lambda m: vni_map[m.group(0)], text)

def extract_acnos_page(page, default_vol=58, default_lang=0, default_genre=0):
    items = []
    def visitor(text, cm, tm, font_dict, font_size):
        t = text.strip()
        if t:
            items.append({
                'text': t,
                'x': tm[4],
                'y': tm[5],
                'size': font_size
            })
    page.extract_text(visitor_text=visitor)
    
    # Filter header and footer
    content_items = [it for it in items if 32 <= it['y'] <= 775]
    if not content_items:
        return []
        
    # Group items by Y coordinate with tolerance
    rows = []
    for it in sorted(content_items, key=lambda x: -x['y']):
        placed = False
        for row in rows:
            if abs(row['y'] - it['y']) <= 7:
                row['items'].append(it)
                placed = True
                break
        if not placed:
            rows.append({'y': it['y'], 'items': [it]})
            
    # Each song typically spans 2 lines:
    # Line 1: [x < 65] 5-digit code | [65 <= x < 310] Title | [310 <= x < 490] Author | [x >= 490] 6-digit code
    # Line 2: [65 <= x < 310] Intro lyric snippet
    songs = []
    current_song = None
    
    for row in rows:
        r_items = sorted(row['items'], key=lambda x: x['x'])
        
        # Check if this row has a 5-digit or 6-digit song code at x < 65 or x > 480
        left_code_item = next((it for it in r_items if it['x'] < 65 and re.match(r'^\d{5,6}$', it['text'])), None)
        title_item = next((it for it in r_items if 65 <= it['x'] < 315), None)
        author_item = next((it for it in r_items if 310 <= it['x'] < 495), None)
        right_code_item = next((it for it in r_items if it['x'] >= 485 and re.match(r'^\d{5,6}$', it['text'])), None)
        
        if left_code_item or (title_item and (author_item or right_code_item)):
            # This is a main song row!
            if current_song:
                songs.append(current_song)
                
            maso_str = left_code_item['text'] if left_code_item else (right_code_item['text'] if right_code_item else '0')
            try:
                maso = int(maso_str)
            except:
                maso = 0
                
            maso6_str = right_code_item['text'] if right_code_item else ''
            title_str = vni_to_unicode(title_item['text']) if title_item else ''
            author_str = vni_to_unicode(author_item['text']) if author_item else ''
            
            # Clean title
            title_str = re.sub(r'\s+', ' ', title_str).strip()
            author_str = re.sub(r'\s+', ' ', author_str).strip()
            
            # Determine genre
            genre = default_genre
            if '(Remix)' in title_str or 'Remix' in title_str:
                genre = 1
            elif '(VC)' in title_str or 'Vọng Cổ' in title_str or '(Tân Cổ)' in title_str:
                genre = 3
                
            current_song = {
                'maso': maso,
                'title': title_str,
                'intro': '',
                'author': author_str,
                'lan': default_lang,
                'g': genre,
                'v': default_vol,
                'maso6': maso6_str
            }
        elif current_song and title_item:
            # This is the intro snippet line!
            intro_text = vni_to_unicode(title_item['text'])
            intro_text = re.sub(r'\s+', ' ', intro_text).strip()
            current_song['intro'] = intro_text
            # If author was split or continued
            if author_item and not current_song['author']:
                current_song['author'] = vni_to_unicode(author_item['text']).strip()
            elif author_item and current_song['author']:
                current_song['author'] += ' ' + vni_to_unicode(author_item['text']).strip()
                
    if current_song:
        songs.append(current_song)
        
    return songs

def process_all_acnos():
    pdf_configs = [
        ('PDF/acnos/58-tan-nhac.pdf', 58, 0, 0),
        ('PDF/acnos/58 tan nhac bs.pdf', 58, 0, 0),
        ('PDF/acnos/58 remix.pdf', 58, 0, 1),
        ('PDF/acnos/58 remix bs.pdf', 58, 0, 1),
        ('PDF/acnos/58 co nhac.pdf', 58, 0, 3),
        ('PDF/acnos/58 ca sy.pdf', 58, 0, 0),
        ('PDF/acnos/58 tieng anh.pdf', 58, 1, 0),
        ('PDF/acnos/Danh-mục-bổ-sung-V60.pdf', 60, 0, 0),
        ('PDF/acnos/Danh-mục-bài-hát-vol-62-Tiếng-anh.pdf', 62, 1, 0),
    ]
    
    all_songs = {}
    t0 = time.time()
    
    for fp, vol, lang, genre in pdf_configs:
        if not os.path.exists(fp):
            print(f"Skipping {fp}, not found")
            continue
        print(f"Processing {fp} (Vol {vol})...")
        reader = pypdf.PdfReader(fp)
        num_p = len(reader.pages)
        count_fp = 0
        for p_idx in range(num_p):
            page_songs = extract_acnos_page(reader.pages[p_idx], default_vol=vol, default_lang=lang, default_genre=genre)
            for s in page_songs:
                m = s['maso']
                if m <= 0: continue
                # Merge or keep newer vol
                if m not in all_songs or s['v'] > all_songs[m]['v']:
                    all_songs[m] = s
                    count_fp += 1
                else:
                    # Update intro/author if missing
                    if not all_songs[m]['intro'] and s['intro']:
                        all_songs[m]['intro'] = s['intro']
                    if not all_songs[m]['author'] and s['author']:
                        all_songs[m]['author'] = s['author']
        print(f"  -> Extracted {count_fp} songs from {fp} ({num_p} pages)")
        
    print(f"\nTotal unique Acnos songs: {len(all_songs):,} in {time.time()-t0:.2f}s")
    
    # Sort by maso
    sorted_songs = sorted(all_songs.values(), key=lambda x: x['maso'])
    
    # Build standard table rows: [id, maso, title, intro, author, lan, g, v]
    # And we can also store maso6 in intro or author if needed, or in a separate field!
    # Wait, if we format title or intro or keep 6-digit code accessible:
    # E.g. [id, maso, title, intro, author, lan, g, v]
    # Where if maso6 exists and differs from maso, we can note it in intro:
    # intro = f"{intro} [Mã HDMI: {s['maso6']}]" if s['maso6'] else intro!
    acnos_rows = []
    for i, s in enumerate(sorted_songs):
        maso6_tag = f" [Mã HDMI: {s['maso6']}]" if (s['maso6'] and s['maso6'] != str(s['maso'])) else ""
        intro = (s['intro'] + maso6_tag).strip()
        row = [i + 1, s['maso'], s['title'], intro, s['author'], s['lan'], s['g'], s['v']]
        acnos_rows.append(row)
        
    # Write to data/acnos.json and data/acnos.js
    os.makedirs('data', exist_ok=True)
    with open('data/acnos.json', 'w', encoding='utf-8') as f:
        json.dump(acnos_rows, f, ensure_ascii=False, separators=(',', ':'))
    with open('data/acnos.js', 'w', encoding='utf-8') as f:
        f.write("window.KARAOKE_DATA_ACNOS = ")
        json.dump(acnos_rows, f, ensure_ascii=False, separators=(',', ':'))
        f.write(";")
        
    print(f"Saved data/acnos.json and data/acnos.js ({len(acnos_rows):,} songs)!")
    return acnos_rows

if __name__ == '__main__':
    process_all_acnos()
