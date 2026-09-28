import os
import sys
import struct
import json
import re
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Ensure utf-8 output in terminal
if sys.stdout and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Comprehensive decoding patterns for Dong Hai / Megamid font
PATTERNS = [
    # 3-byte uppercase
    (b'\xd6\xf4\xf9', 'Ướ'), (b'\xd6\xf4\xf8', 'Ườ'), (b'\xd6\xf4\xef', 'Ượ'), (b'\xd6\xf4', 'Ươ'),
    (b'\xd4\xdb', 'Ở'), (b'\xd4\xf9', 'Ớ'), (b'\xd4\xf8', 'Ờ'), (b'\xd4\xef', 'Ợ'), (b'\xd4\xd9', 'Ớ'),
    (b'\xd6\xd9', 'Ứ'), (b'\xd6\xd8', 'Ừ'),

    # 3-byte lowercase ươ
    (b'\xf6\xf4\xf8', 'ườ'), (b'\xf6\xf4\xf9', 'ướ'), (b'\xf6\xf4\xfb', 'ưở'),
    (b'\xf6\xf4\xf5', 'ưỡ'), (b'\xf6\xf4\xef', 'ượ'), (b'\xf6\xf4', 'ươ'),

    # Uppercase 2-byte: Ô
    (b'O\xc2', 'Ô'), (b'O\xc1', 'Ố'), (b'O\xc0', 'Ồ'), (b'O\xc5', 'Ổ'), (b'O\xc3', 'Ỗ'), (b'O\xc4', 'Ộ'),
    (b'O\xd9', 'Ó'), (b'O\xd8', 'Ò'), (b'O\xdb', 'Ỏ'), (b'O\xd5', 'Õ'), (b'O\xef', 'Ọ'),

    # Uppercase 2-byte: Ê
    (b'E\xc2', 'Ê'), (b'E\xc1', 'Ế'), (b'E\xc0', 'Ề'), (b'E\xc5', 'Ể'), (b'E\xc3', 'Ễ'), (b'E\xc4', 'Ệ'),
    (b'E\xd9', 'É'), (b'E\xd8', 'È'), (b'E\xdb', 'Ẻ'), (b'E\xd5', 'Ẽ'), (b'E\xef', 'Ẹ'),

    # Uppercase 2-byte: U
    (b'U\xd9', 'Ú'), (b'U\xd8', 'Ù'), (b'U\xdb', 'Ủ'), (b'U\xd5', 'Ũ'), (b'U\xef', 'Ụ'),
    (b'U\xf6', 'Ư'),

    # Uppercase 2-byte: I, Y
    (b'I\xd9', 'Í'), (b'Y\xd9', 'Ý'), (b'Y\xd8', 'Ỳ'), (b'Y\xdb', 'Ỷ'), (b'Y\xd5', 'Ỹ'), (b'Y\xef', 'Ỵ'),

    # Uppercase 2-byte: A
    (b'A\xd8', 'À'), (b'A\xd9', 'Á'), (b'A\xdb', 'Ả'), (b'A\xd5', 'Ã'), (b'A\xef', 'Ạ'),
    (b'A\xc2', 'Â'), (b'A\xc0', 'Ầ'), (b'A\xc1', 'Ấ'), (b'A\xc3', 'Ẫ'), (b'A\xc4', 'Ậ'), (b'A\xc5', 'Ẩ'),
    (b'A\xca', 'Ă'), (b'A\xc8', 'Ằ'), (b'A\xc9', 'Ắ'),

    # Lowercase 2-byte: ư
    (b'\xf6\xf8', 'ừ'), (b'\xf6\xf9', 'ứ'), (b'\xf6\xfb', 'ử'),
    (b'\xf6\xf5', 'ữ'), (b'\xf6\xef', 'ự'), (b'\xf6', 'ư'),

    # Lowercase 2-byte: ơ
    (b'\xf4\xf8', 'ờ'), (b'\xf4\xf9', 'ớ'), (b'\xf4\xfb', 'ở'),
    (b'\xf4\xf5', 'ỡ'), (b'\xf4\xef', 'ợ'), (b'\xf4', 'ơ'),

    # Lowercase 2-byte: a
    (b'a\xe0', 'ầ'), (b'a\xe1', 'ấ'), (b'a\xe2', 'â'), (b'a\xe3', 'ẫ'), (b'a\xe4', 'ậ'), (b'a\xe5', 'ẩ'),
    (b'a\xe8', 'ằ'), (b'a\xe9', 'ắ'), (b'a\xea', 'ă'), (b'a\xeb', 'ặ'), (b'a\xfa', 'ẳ'), (b'a\xfc', 'ẵ'),
    (b'a\xf8', 'à'), (b'a\xf9', 'á'), (b'a\xfb', 'ả'), (b'a\xf5', 'ã'), (b'a\xef', 'ạ'),

    # Lowercase 2-byte: e
    (b'e\xe0', 'ề'), (b'e\xe1', 'ế'), (b'e\xe2', 'ê'), (b'e\xe3', 'ễ'), (b'e\xe4', 'ệ'), (b'e\xe5', 'ể'),
    (b'e\xf8', 'è'), (b'e\xf9', 'é'), (b'e\xfb', 'ẻ'), (b'e\xf5', 'ẽ'), (b'e\xef', 'ẹ'),

    # Lowercase 2-byte: o
    (b'o\xe0', 'ồ'), (b'o\xe1', 'ố'), (b'o\xe2', 'ô'), (b'o\xe3', 'ỗ'), (b'o\xe4', 'ộ'), (b'o\xe5', 'ổ'),
    (b'o\xf8', 'ò'), (b'o\xf9', 'ó'), (b'o\xfb', 'ỏ'), (b'o\xf5', 'õ'), (b'o\xef', 'ọ'),

    # Lowercase 2-byte: u
    (b'u\xf8', 'ù'), (b'u\xf9', 'ú'), (b'u\xfb', 'ủ'), (b'u\xf5', 'ũ'), (b'u\xef', 'ụ'),

    # Lowercase 2-byte: y
    (b'y\xf8', 'ỳ'), (b'y\xf9', 'ý'), (b'y\xfb', 'ỷ'), (b'y\xf5', 'ỹ'), (b'y\xef', 'ỵ'),

    # Lowercase 2-byte: i
    (b'i\xf8', 'ì'), (b'i\xf9', 'í'), (b'i\xfb', 'ỉ'), (b'i\xf5', 'ĩ'), (b'i\xef', 'ị'),

    # Single bytes
    (b'\xd1', 'Đ'), (b'\xd4', 'Ơ'), (b'\xd6', 'Ô'), (b'\xcd', 'Í'), (b'\x85', '…'),
    (b'\xec', 'ì'), (b'\xed', 'í'), (b'\xe6', 'ỉ'), (b'\xf3', 'ĩ'), (b'\xf2', 'ị'), (b'\xee', 'ị'),
]
PATTERNS.sort(key=lambda x: -len(x[0]))

def decode_text(b):
    if not b:
        return ""
    if all(x < 128 for x in b):
        return b.decode('ascii', errors='ignore')

    # Check if string contains Latin alphabet letters
    has_latin = any((ord('a') <= x <= ord('z')) or (ord('A') <= x <= ord('Z')) for x in b)
    if not has_latin:
        try:
            return b.decode('gbk')
        except Exception:
            try:
                return b.decode('gb18030')
            except Exception:
                pass

    out = []
    i = 0
    n = len(b)
    while i < n:
        matched = False
        for pat, repl in PATTERNS:
            plen = len(pat)
            if b[i:i+plen] == pat:
                out.append(repl)
                i += plen
                matched = True
                break
        if not matched:
            byte = b[i:i+1]
            try:
                out.append(byte.decode('ascii'))
            except Exception:
                try:
                    out.append(b[i:i+2].decode('gbk'))
                    i += 2
                    continue
                except Exception:
                    out.append('')
            i += 1
    return ''.join(out)

def clean_song_title(raw_decoded):
    """
    Cleans up title formatting, splits line break slashes '/'
    and separates notes or composer info in parentheses.
    """
    s = raw_decoded.strip()
    if not s:
        return "", "", ""
        
    full_title = s
    note = ""
    
    if '/' in s:
        parts = s.split('/', 1)
        part1 = parts[0].strip()
        part2 = parts[1].strip()
        
        m = re.match(r'^\((.*?)\)$', part2)
        if m:
            content = m.group(1).strip()
            # If it's a remix, tan co, live, dj... keep it in the title
            if any(k in content.lower() for k in ['remix', 'tân cổ', 'tc', 'dj', 'live', 'dance', 'disco', 'trữ tình', 'nhạc hoa']):
                full_title = f"{part1} ({content})"
                note = content
            else:
                full_title = part1
                note = content
        else:
            full_title = f"{part1} {part2}"
            note = ""
    else:
        m = re.search(r'\((.*?)\)$', s)
        if m:
            note = m.group(1).strip()

    return full_title, s, note

def parse_volume(idx_path, p_start, p_tail, p_singer_start):
    with open(idx_path, 'rb') as f:
        d = f.read()
    
    # 1. Parse singers
    singers = []
    pos = p_singer_start
    while pos < p_start:
        p05 = d.find(b'\x05', pos)
        if p05 == -1 or p05 >= p_start:
            break
        sname = decode_text(d[pos:p05])
        smeta = d[p05:p05+5]
        scnt = smeta[2] if len(smeta) >= 3 else 0
        singers.append({'name': sname, 'count': scnt})
        pos = p05 + 5

    # 2. Parse songs
    records = []
    pos = p_start
    while pos < p_tail:
        p01 = d.find(b'\x01', pos)
        if p01 == -1 or p01 >= p_tail:
            break
        title_bytes = d[pos:p01]
        flag = d[p01+3]
        mlen = 18 if (flag & 0x80) else 12
        meta = d[p01:p01+mlen]
        records.append((title_bytes, meta, flag))
        pos = p01 + mlen
    records.append((b'\xd7\xe6\xb9\xfa\xd7\xe6\xb9\xfa\xb6\xe0\xc3\xc0\xc0\xf6', b'', 2))

    # 3. Parse codes
    table = d[p_tail+14:]
    codes = []
    for i in range(len(table)//4):
        b = table[i*4 : (i+1)*4]
        code = (b[1] << 16) | (b[3] << 8) | b[2]
        codes.append((code, b[1]))

    assert len(records) == len(codes), f"Mismatch in {idx_path}: {len(records)} records vs {len(codes)} codes"
    return singers, records, codes

def infer_genre(title, note):
    combined = f"{title} {note}".lower()
    if 'remix' in combined or 'dj' in combined or 'dance' in combined:
        return 1  # Nhạc Trẻ / Remix
    if 'tân cổ' in combined or 'vọng cổ' in combined or '(tc)' in combined:
        return 3  # Quê Hương - Cổ Nhạc
    if 'trữ tình' in combined or 'bolero' in combined:
        return 2  # Trữ Tình
    if 'thiếu nhi' in combined:
        return 5  # Thiếu Nhi
    return 0  # Khác

def consolidate_volumes():
    # Detect best paths (drive I:/J: or local workspace)
    p82 = 'I:/IDX/MEGIDX' if os.path.exists('I:/IDX/MEGIDX') else 'MEGIDX 82BKTV'
    p83 = 'J:/IDX/MEGIDX' if os.path.exists('J:/IDX/MEGIDX') else 'MEGIDX 83B'

    print(f"Reading Vol 82B from: {p82}")
    s82, r82, c82 = parse_volume(p82, 26624, 378315, 1463)
    print(f"  -> Vol 82B: {len(r82):,} songs, {len(s82):,} singers")

    print(f"Reading Vol 83B from: {p83}")
    s83, r83, c83 = parse_volume(p83, 18925, 257501, 1159)
    print(f"  -> Vol 83B: {len(r83):,} songs, {len(s83):,} singers")

    merged = {}

    # Insert Vol 82B
    for i in range(len(r82)):
        rec = r82[i]
        code, vocal_flag = c82[i]
        flag = rec[2]
        lang_id = flag & 0x7f
        meta = rec[1]

        singer = ''
        if (flag & 0x80) and len(meta) >= 18:
            s_idx = struct.unpack('<H', meta[16:18])[0]
            if s_idx < len(s82):
                singer = s82[s_idx]['name']

        raw_title = decode_text(rec[0])
        title, orig, note = clean_song_title(raw_title)

        offset_hex = ''
        if len(meta) >= 12:
            offset_val = struct.unpack('<I', meta[8:12])[0]
            offset_hex = f'{offset_val:08X}'

        is_v = 1 if (vocal_flag == 1 or lang_id == 1) else 0

        merged[code] = {
            'code': code,
            'title': title,
            'orig_title': orig,
            'singer': singer,
            'note': note,
            'lang_id': lang_id,
            'is_vocal': is_v,
            'vol': 'Vol 82B KTV',
            'vol_num': 82,
            'hex_offset': offset_hex,
            'in_82': True,
            'in_83': False
        }

    # Merge Vol 83B
    for i in range(len(r83)):
        rec = r83[i]
        code, vocal_flag = c83[i]
        flag = rec[2]
        lang_id = flag & 0x7f
        meta = rec[1]

        singer = ''
        if (flag & 0x80) and len(meta) >= 18:
            s_idx = struct.unpack('<H', meta[16:18])[0]
            if s_idx < len(s83):
                singer = s83[s_idx]['name']

        raw_title = decode_text(rec[0])
        title, orig, note = clean_song_title(raw_title)

        offset_hex = ''
        if len(meta) >= 12:
            offset_val = struct.unpack('<I', meta[8:12])[0]
            offset_hex = f'{offset_val:08X}'

        is_v = 1 if (vocal_flag == 1 or lang_id == 1) else 0

        if code in merged:
            item = merged[code]
            item['in_83'] = True
            item['vol'] = 'Vol 82B & 83B'
            item['vol_num'] = 83
            if is_v:
                item['is_vocal'] = 1

            # Check if 83B refined the title or released updated track
            if title.lower() != item['title'].lower():
                old_t = item['title']
                item['title'] = title
                item['orig_title'] = orig
                item['note'] = f'[Cập nhật 83B] Tên cũ 82B: {old_t}'
                if singer:
                    item['singer'] = singer
            elif not item['singer'] and singer:
                item['singer'] = singer
        else:
            merged[code] = {
                'code': code,
                'title': title,
                'orig_title': orig,
                'singer': singer,
                'note': '[Bài mới Vol 83B]',
                'lang_id': lang_id,
                'is_vocal': is_v,
                'vol': 'Vol 83B KTV',
                'vol_num': 83,
                'hex_offset': offset_hex,
                'in_82': False,
                'in_83': True
            }

    # Language string mapping
    for item in merged.values():
        lid = item['lang_id']
        if lid == 0:
            item['lang_str'] = 'Tiếng Việt'
        elif lid == 1:
            item['lang_str'] = 'Nhạc Ca Sĩ (Vocal)'
        elif lid == 2:
            item['lang_str'] = 'Tiếng Hoa'
        elif lid == 3:
            item['lang_str'] = 'Tiếng Anh'
        else:
            item['lang_str'] = f'Khác ({lid})'

        item['pop_file'] = f"{item['hex_offset'].lower()}.pop" if item['hex_offset'] else ''
        item['genre'] = infer_genre(item['title'], item['note'])

    # Sort merged songs by code
    sorted_songs = sorted(merged.values(), key=lambda x: x['code'])
    for idx, s in enumerate(sorted_songs, start=1):
        s['stt'] = idx

    print(f"Total Consolidated Songs: {len(sorted_songs):,} unique songs")
    return s82, s83, sorted_songs

def export_to_excel(s82, s83, songs, output_path):
    print(f"\nCreating Excel Workbook: {output_path}...")
    wb = openpyxl.Workbook()

    # Styling definitions
    font_header = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
    fill_header = PatternFill(start_color='0E7490', end_color='0E7490', fill_type='solid') # Ocean Cyan / Teal
    fill_zebra = PatternFill(start_color='F8FAFC', end_color='F8FAFC', fill_type='solid')
    fill_new_badge = PatternFill(start_color='FEF3C7', end_color='FEF3C7', fill_type='solid')
    font_data = Font(name='Segoe UI', size=10)
    font_code = Font(name='Segoe UI', size=11, bold=True, color='0369A1')
    font_new_code = Font(name='Segoe UI', size=11, bold=True, color='D97706')

    border_thin = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )
    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    align_right = Alignment(horizontal='right', vertical='center')

    headers = [
        ("STT", 8, align_center),
        ("Mã bài hát", 14, align_center),
        ("Tên bài hát", 36, align_left),
        ("Tên gốc (MEGMID)", 36, align_left),
        ("Ca sĩ / Nghệ sĩ", 25, align_left),
        ("Ghi chú / Tác giả", 28, align_left),
        ("Ngôn ngữ / Phân loại", 20, align_center),
        ("Có lời ca sĩ (Vocal)", 18, align_center),
        ("Vol phát hành", 18, align_center),
        ("Offset MEGMID (Hex)", 20, align_center),
        ("File trích xuất (.pop)", 22, align_center),
    ]

    def write_sheet(ws, title, song_list):
        ws.title = title
        ws.views.sheetView[0].showGridLines = True

        # Header
        for col_idx, (h_name, _, align) in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx, value=h_name)
            cell.font = font_header
            cell.fill = fill_header
            cell.alignment = align
            cell.border = border_thin
        ws.row_dimensions[1].height = 28

        # Data rows
        for row_idx, s in enumerate(song_list, start=2):
            is_new = (s['vol'] == 'Vol 83B KTV')
            vocal_label = "Có lời ca sĩ 🎤" if s['is_vocal'] else "Beat / Nhạc nền"
            values = [
                s['stt'],
                s['code'],
                s['title'],
                s['orig_title'],
                s['singer'],
                s['note'],
                s['lang_str'],
                vocal_label,
                s['vol'],
                s['hex_offset'],
                s['pop_file']
            ]
            is_even = (row_idx % 2 == 0)
            ws.row_dimensions[row_idx].height = 20

            for col_idx, val in enumerate(values, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                if col_idx == 2:
                    cell.font = font_new_code if is_new else font_code
                else:
                    cell.font = font_data
                cell.alignment = headers[col_idx-1][2]
                cell.border = border_thin
                if is_new and col_idx in [2, 3, 9]:
                    cell.fill = fill_new_badge
                elif not is_even:
                    cell.fill = fill_zebra

        # Column widths & filters
        for col_idx, (_, width, _) in enumerate(headers, start=1):
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = width

        ws.freeze_panes = 'A2'
        last_col = get_column_letter(len(headers))
        ws.auto_filter.ref = f"A1:{last_col}{len(song_list)+1}"

    # Sheet 1: Tất cả bài hát (10,976)
    ws_main = wb.active
    write_sheet(ws_main, "Tất cả bài hát", songs)
    print("  -> Sheet 'Tất cả bài hát' written")

    # Sheet 2: Bài mới Vol 83B (151 songs)
    songs_83_new = [s for s in songs if s['vol'] == 'Vol 83B KTV']
    ws_83 = wb.create_sheet()
    write_sheet(ws_83, "Bài mới Vol 83B", songs_83_new)
    print(f"  -> Sheet 'Bài mới Vol 83B' written ({len(songs_83_new)} bài)")

    # Sheet 3: Nhạc Ca Sĩ (Vocal)
    songs_vocal = [s for s in songs if s['is_vocal'] == 1]
    ws_voc = wb.create_sheet()
    write_sheet(ws_voc, "Nhạc Ca Sĩ (Vocal)", songs_vocal)
    print(f"  -> Sheet 'Nhạc Ca Sĩ (Vocal)' written ({len(songs_vocal)} bài)")

    # Sheet 4: Nhạc Tiếng Việt
    songs_vi = [s for s in songs if s['lang_id'] == 0]
    ws_vi = wb.create_sheet()
    write_sheet(ws_vi, "Nhạc Tiếng Việt", songs_vi)
    print(f"  -> Sheet 'Nhạc Tiếng Việt' written ({len(songs_vi)} bài)")

    # Sheet 5: Nhạc Nước Ngoài (Hoa, Anh)
    songs_foreign = [s for s in songs if s['lang_id'] in [2, 3]]
    ws_foreign = wb.create_sheet()
    write_sheet(ws_foreign, "Nhạc Nước Ngoài", songs_foreign)
    print(f"  -> Sheet 'Nhạc Nước Ngoài' written ({len(songs_foreign)} bài)")

    # Sheet 6: Danh mục Ca sĩ
    ws_singers = wb.create_sheet(title="Danh mục Ca sĩ")
    ws_singers.views.sheetView[0].showGridLines = True
    s_headers = [
        ("STT", 8, align_center),
        ("Tên Ca sĩ / Ban nhạc", 35, align_left),
        ("Số lượng bài hát trong thư viện", 30, align_center)
    ]
    for col_idx, (h_name, _, align) in enumerate(s_headers, start=1):
        cell = ws_singers.cell(row=1, column=col_idx, value=h_name)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align
        cell.border = border_thin
    ws_singers.row_dimensions[1].height = 28

    # Count songs per singer
    singer_counts = {}
    for s in songs:
        if s['singer']:
            singer_counts[s['singer']] = singer_counts.get(s['singer'], 0) + 1
    sorted_singers = sorted(singer_counts.items(), key=lambda x: -x[1])

    for row_idx, (name, cnt) in enumerate(sorted_singers, start=2):
        is_even = (row_idx % 2 == 0)
        ws_singers.row_dimensions[row_idx].height = 20
        c1 = ws_singers.cell(row=row_idx, column=1, value=row_idx - 1)
        c2 = ws_singers.cell(row=row_idx, column=2, value=name)
        c3 = ws_singers.cell(row=row_idx, column=3, value=cnt)
        for col_idx, cell in enumerate([c1, c2, c3], start=1):
            cell.font = font_data
            cell.border = border_thin
            cell.alignment = s_headers[col_idx-1][2]
            if not is_even:
                cell.fill = fill_zebra

    for col_idx, (_, width, _) in enumerate(s_headers, start=1):
        col_letter = get_column_letter(col_idx)
        ws_singers.column_dimensions[col_letter].width = width
    ws_singers.freeze_panes = 'A2'
    ws_singers.auto_filter.ref = f"A1:C{len(sorted_singers)+1}"
    print(f"  -> Sheet 'Danh mục Ca sĩ' written ({len(sorted_singers)} nghệ sĩ)")

    wb.save(output_path)
    print(f"SUCCESS: Saved Excel to {output_path} ({os.path.getsize(output_path):,} bytes)")

def export_json_and_js(songs, json_path, js_path):
    print(f"\nExporting JSON and JS database for Dong Hai KTV...")
    # Schema matching web app: [id, maso, title, intro, author, lan, g, v, isVocal, isChorus]
    rows = []
    for s in songs:
        # Construct helpful intro
        intro_parts = []
        if s['note']:
            intro_parts.append(s['note'])
        if s['is_vocal']:
            intro_parts.append("Có lời ca sĩ")
        intro_str = " - ".join(intro_parts)

        row = [
            s['stt'],
            s['code'],
            s['title'],
            intro_str,
            s['singer'],
            s['lang_id'],
            s['genre'],
            s['vol_num'],
            s['is_vocal'],
            0
        ]
        rows.append(row)

    # 1. Write JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, separators=(',', ':'))
    print(f"SUCCESS: Saved JSON to {json_path} ({os.path.getsize(json_path):,} bytes, {len(rows):,} records)")

    # 2. Write JS
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write("window.KARAOKE_DATA_DH=")
        json.dump(rows, f, ensure_ascii=False, separators=(',', ':'))
        f.write(";\n")
    print(f"SUCCESS: Saved JS to {js_path} ({os.path.getsize(js_path):,} bytes)")

def main():
    s82, s83, songs = consolidate_volumes()
    
    excel_path = os.path.abspath('LIST Nhạc Đông Hải.xlsx')
    export_to_excel(s82, s83, songs, excel_path)

    json_path = os.path.abspath('data/donghai.json')
    js_path = os.path.abspath('data/donghai.js')
    export_json_and_js(songs, json_path, js_path)

if __name__ == '__main__':
    main()
