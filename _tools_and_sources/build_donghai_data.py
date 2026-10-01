import os
import sys
import struct
import json
import re
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')

# Ensure _tools_and_sources is in path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from export_donghai_excel import PATTERNS, decode_text, clean_song_title, parse_volume, infer_genre

def fix_chinese_mojibake(title, raw_bytes, code):
    if code < 20000 and any(c in title for c in ['°', '®', '±', '²', '³', 'µ', '¶', '·', '¹', 'º', '»', '¼', '½', '¾', '¿', 'Ị']):
        gbk = decode_text(raw_bytes)
        if gbk and not any(c in gbk for c in ['°', '®', '±', '¿']):
            return gbk
    return title

def build_donghai_dataset(excel_82_path, excel_83_path, megidx_82_path, megidx_83_path):
    print("=" * 65)
    print("  XÂY DỰNG BỘ DỮ LIỆU ĐÔNG HẢI KTV (VOL 82B & VOL 83B)")
    print("=" * 65)

    # 1. Parse MEGIDX binaries for rich metadata (singers, hex offsets, raw bytes)
    print(f"\n[1/5] Đọc dữ liệu nhị phân MEGIDX...")
    s82, r82, c82 = parse_volume(megidx_82_path, 26624, 378315, 1463)
    s83, r83, c83 = parse_volume(megidx_83_path, 18925, 257501, 1159)
    print(f"  - MEGIDX 82B: {len(r82):,} bản ghi, {len(s82):,} nghệ sĩ")
    print(f"  - MEGIDX 83B: {len(r83):,} bản ghi, {len(s83):,} nghệ sĩ")

    # 2. Load user Excel files
    print(f"\n[2/5] Đọc 2 file Excel người dùng chỉ định...")
    print(f"  - Đang đọc: {os.path.basename(excel_82_path)} ...")
    wb82 = openpyxl.load_workbook(excel_82_path, data_only=True)
    ws82 = wb82['Tất cả']
    rows82 = list(ws82.iter_rows(min_row=2, values_only=True))

    print(f"  - Đang đọc: {os.path.basename(excel_83_path)} ...")
    wb83 = openpyxl.load_workbook(excel_83_path, data_only=True)
    ws83 = wb83['Tất cả']
    rows83 = list(ws83.iter_rows(min_row=2, values_only=True))

    print(f"  -> Vol 82B: {len(rows82):,} bài hát")
    print(f"  -> Vol 83B: {len(rows83):,} bài hát")

    assert len(rows82) == len(r82), f"Số bài trong Excel 82B ({len(rows82)}) không khớp MEGIDX ({len(r82)})"
    assert len(rows83) == len(r83), f"Số bài trong Excel 83B ({len(rows83)}) không khớp MEGIDX ({len(r83)})"

    merged = {}

    # Process 82B
    for i in range(len(rows82)):
        ex_row = rows82[i]
        code = ex_row[1]
        ex_title = str(ex_row[2]).strip()
        nhac_val = str(ex_row[3] or '').strip() if len(ex_row) > 3 else ''
        loi_val = str(ex_row[4] or '').strip() if len(ex_row) > 4 else ''
        intro_val = str(ex_row[5] or '').strip() if len(ex_row) > 5 else ''

        rec = r82[i]
        raw_title_bytes = rec[0]
        meta = rec[1]
        flag = rec[2]
        raw_code, vocal_flag = c82[i]

        computed_code = (vocal_flag << 16) | (raw_code & 0xFFFF)
        assert code == computed_code, f"Mã bài hát không khớp tại dòng {i}: {code} vs {computed_code}"

        title = fix_chinese_mojibake(ex_title, raw_title_bytes, code)
        orig_title = decode_text(raw_title_bytes)

        singer = ''
        if (flag & 0x80) and len(meta) >= 18:
            s_idx = struct.unpack('<H', meta[16:18])[0]
            if s_idx < len(s82):
                singer = s82[s_idx]['name'].strip()

        offset_hex = ''
        if len(meta) >= 12:
            offset_val = struct.unpack('<I', meta[8:12])[0]
            offset_hex = f'{offset_val:08X}'

        code_str = str(code)
        if code_str.startswith('8'):
            lang_id = 1
            is_vocal = 1
            lang_str = 'Nhạc Ca Sĩ (Vocal)'
        elif code_str.startswith('1'):
            lang_id = 2
            is_vocal = 0
            lang_str = 'Tiếng Trung'
        elif code_str.startswith('3'):
            lang_id = 3
            is_vocal = 0
            lang_str = 'Tiếng Anh'
        else:
            lang_id = 0
            is_vocal = 0
            lang_str = 'Tiếng Việt'

        merged[code] = {
            'code': code,
            'title': title,
            'orig_title': orig_title,
            'singer': singer,
            'nhac': nhac_val,
            'loi': loi_val,
            'intro': intro_val,
            'note': '',
            'lang_id': lang_id,
            'lang_str': lang_str,
            'is_vocal': is_vocal,
            'vol': 'Vol 82B KTV',
            'vol_num': 82,
            'hex_offset': offset_hex,
            'pop_file': f"{offset_hex.lower()}.pop" if offset_hex else '',
            'in_82': True,
            'in_83': False
        }

    # Process 83B
    for i in range(len(rows83)):
        ex_row = rows83[i]
        code = ex_row[1]
        ex_title = str(ex_row[2]).strip()
        nhac_val = str(ex_row[3] or '').strip() if len(ex_row) > 3 else ''
        loi_val = str(ex_row[4] or '').strip() if len(ex_row) > 4 else ''
        intro_val = str(ex_row[5] or '').strip() if len(ex_row) > 5 else ''

        rec = r83[i]
        raw_title_bytes = rec[0]
        meta = rec[1]
        flag = rec[2]
        raw_code, vocal_flag = c83[i]

        computed_code = (vocal_flag << 16) | (raw_code & 0xFFFF)
        assert code == computed_code, f"Mã bài hát không khớp tại dòng 83B {i}: {code} vs {computed_code}"

        title = fix_chinese_mojibake(ex_title, raw_title_bytes, code)
        orig_title = decode_text(raw_title_bytes)

        singer = ''
        if (flag & 0x80) and len(meta) >= 18:
            s_idx = struct.unpack('<H', meta[16:18])[0]
            if s_idx < len(s83):
                singer = s83[s_idx]['name'].strip()

        offset_hex = ''
        if len(meta) >= 12:
            offset_val = struct.unpack('<I', meta[8:12])[0]
            offset_hex = f'{offset_val:08X}'

        code_str = str(code)
        if code_str.startswith('8'):
            lang_id = 1
            is_vocal = 1
            lang_str = 'Nhạc Ca Sĩ (Vocal)'
        elif code_str.startswith('1'):
            lang_id = 2
            is_vocal = 0
            lang_str = 'Tiếng Trung'
        elif code_str.startswith('3'):
            lang_id = 3
            is_vocal = 0
            lang_str = 'Tiếng Anh'
        else:
            lang_id = 0
            is_vocal = 0
            lang_str = 'Tiếng Việt'

        if code in merged:
            item = merged[code]
            item['in_83'] = True
            item['vol'] = 'Vol 82B & 83B'
            item['vol_num'] = 83

            # Title update from Vol 83B
            if title.lower() != item['title'].lower():
                old_t = item['title']
                item['title'] = title
                item['orig_title'] = orig_title
                item['note'] = f'[Cập nhật 83B] Tên cũ 82B: {old_t}'
            
            if singer:
                item['singer'] = singer
            if nhac_val:
                item['nhac'] = nhac_val
            if loi_val:
                item['loi'] = loi_val
            if intro_val:
                item['intro'] = intro_val
            if offset_hex:
                item['hex_offset'] = offset_hex
                item['pop_file'] = f"{offset_hex.lower()}.pop"
        else:
            # New song in Vol 83B
            merged[code] = {
                'code': code,
                'title': title,
                'orig_title': orig_title,
                'singer': singer,
                'nhac': nhac_val,
                'loi': loi_val,
                'intro': intro_val,
                'note': '[Bài mới Vol 83B]',
                'lang_id': lang_id,
                'lang_str': lang_str,
                'is_vocal': is_vocal,
                'vol': 'Vol 83B KTV',
                'vol_num': 83,
                'hex_offset': offset_hex,
                'pop_file': f"{offset_hex.lower()}.pop" if offset_hex else '',
                'in_82': False,
                'in_83': True
            }

    # Infer genre for each song
    for item in merged.values():
        item['genre'] = infer_genre(item['title'], item['note'])

    # Sort songs by code
    sorted_songs = sorted(merged.values(), key=lambda x: x['code'])
    for idx, s in enumerate(sorted_songs, start=1):
        s['stt'] = idx

    print(f"\n[3/5] Tổng hợp & Hợp nhất danh mục:")
    print(f"  - Tổng số bài hát duy nhất: {len(sorted_songs):,} bài")
    print(f"  - Bài có mặt ở cả 82B & 83B: {sum(1 for s in sorted_songs if s['in_82'] and s['in_83']):,} bài")
    print(f"  - Bài chỉ có ở 82B: {sum(1 for s in sorted_songs if s['in_82'] and not s['in_83']):,} bài")
    print(f"  - Bài mới chỉ có ở 83B: {sum(1 for s in sorted_songs if not s['in_82'] and s['in_83']):,} bài")
    print(f"  - Nhạc Ca Sĩ (Vocal 8xxxx): {sum(1 for s in sorted_songs if s['is_vocal'] == 1):,} bài")
    print(f"  - Nhạc Tiếng Việt (5xxxx, 6xxxx): {sum(1 for s in sorted_songs if s['lang_id'] == 0):,} bài")
    print(f"  - Nhạc Tiếng Trung (1xxxx): {sum(1 for s in sorted_songs if s['lang_id'] == 2):,} bài")
    print(f"  - Nhạc Tiếng Anh (3xxxx): {sum(1 for s in sorted_songs if s['lang_id'] == 3):,} bài")
    print(f"  - Số bài có thông tin Tác giả / Nhạc sĩ: {sum(1 for s in sorted_songs if s['nhac']):,} bài")
    print(f"  - Số bài có câu mở đầu (Lời đầu): {sum(1 for s in sorted_songs if s['intro']):,} bài")
    print(f"  - Số bài có thông tin Nghệ sĩ/Ca sĩ: {sum(1 for s in sorted_songs if s['singer']):,} bài")

    return s82, s83, sorted_songs

def export_to_excel(songs, output_path):
    print(f"\n[4/5] Xuất file Excel chính thức: {output_path}...")
    wb = openpyxl.Workbook()

    font_header = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
    fill_header = PatternFill(start_color='0E7490', end_color='0E7490', fill_type='solid') # Ocean Teal
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

    headers = [
        ("STT", 8, align_center),
        ("Mã bài hát", 14, align_center),
        ("Tên bài hát", 36, align_left),
        ("Tên gốc (MEGMID)", 36, align_left),
        ("Ca sĩ / Nghệ sĩ", 25, align_left),
        ("Tác giả / Nhạc sĩ", 28, align_left),
        ("Tác giả lời", 28, align_left),
        ("Lời đầu bài hát", 45, align_left),
        ("Ghi chú", 25, align_left),
        ("Ngôn ngữ / Phân loại", 20, align_center),
        ("Có lời ca sĩ (Vocal)", 18, align_center),
        ("Vol phát hành", 18, align_center),
        ("Offset MEGMID (Hex)", 20, align_center),
        ("File trích xuất (.pop)", 22, align_center),
    ]

    def write_sheet(ws, title, song_list):
        ws.title = title
        ws.views.sheetView[0].showGridLines = True

        for col_idx, (h_name, _, align) in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx, value=h_name)
            cell.font = font_header
            cell.fill = fill_header
            cell.alignment = align
            cell.border = border_thin
        ws.row_dimensions[1].height = 28

        for row_idx, s in enumerate(song_list, start=2):
            is_new = (s['vol'] == 'Vol 83B KTV')
            vocal_label = "Có lời ca sĩ 🎤" if s['is_vocal'] else "Beat / Nhạc nền"
            values = [
                s['stt'],
                s['code'],
                s['title'],
                s['orig_title'],
                s['singer'],
                s['nhac'],
                s['loi'],
                s['intro'],
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
                if is_new and col_idx in [2, 3, 12]:
                    cell.fill = fill_new_badge
                elif not is_even:
                    cell.fill = fill_zebra

        for col_idx, (_, width, _) in enumerate(headers, start=1):
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = width

        ws.freeze_panes = 'A2'
        last_col = get_column_letter(len(headers))
        ws.auto_filter.ref = f"A1:{last_col}{len(song_list)+1}"

    # Sheet 1: Tất cả bài hát
    ws_main = wb.active
    write_sheet(ws_main, "Tất cả bài hát", songs)
    print(f"  -> Sheet 'Tất cả bài hát' ({len(songs):,} bài)")

    # Sheet 2: Bài mới Vol 83B
    songs_83_new = [s for s in songs if s['vol'] == 'Vol 83B KTV']
    ws_83 = wb.create_sheet()
    write_sheet(ws_83, "Bài mới Vol 83B", songs_83_new)
    print(f"  -> Sheet 'Bài mới Vol 83B' ({len(songs_83_new):,} bài)")

    # Sheet 3: Nhạc Ca Sĩ (Vocal)
    songs_vocal = [s for s in songs if s['is_vocal'] == 1]
    ws_voc = wb.create_sheet()
    write_sheet(ws_voc, "Nhạc Ca Sĩ (Vocal)", songs_vocal)
    print(f"  -> Sheet 'Nhạc Ca Sĩ (Vocal)' ({len(songs_vocal):,} bài)")

    # Sheet 4: Nhạc Tiếng Việt
    songs_vi = [s for s in songs if s['lang_id'] == 0]
    ws_vi = wb.create_sheet()
    write_sheet(ws_vi, "Nhạc Tiếng Việt", songs_vi)
    print(f"  -> Sheet 'Nhạc Tiếng Việt' ({len(songs_vi):,} bài)")

    # Sheet 5: Nhạc Nước Ngoài
    songs_foreign = [s for s in songs if s['lang_id'] in [2, 3]]
    ws_foreign = wb.create_sheet()
    write_sheet(ws_foreign, "Nhạc Nước Ngoài", songs_foreign)
    print(f"  -> Sheet 'Nhạc Nước Ngoài' ({len(songs_foreign):,} bài)")

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
    print(f"  -> Sheet 'Danh mục Ca sĩ' ({len(sorted_singers):,} nghệ sĩ)")

    wb.save(output_path)
    print(f"  THÀNH CÔNG: Đã lưu {output_path} ({os.path.getsize(output_path):,} bytes)")

def export_json_and_js(songs, json_path, js_path):
    print(f"\n[5/5] Xuất file JSON & JS cho ứng dụng Web / PWA...")
    # Schema: [id, maso, title, intro, author, lan, g, v, isVocal, isChorus]
    rows = []
    for s in songs:
        intro_parts = []
        if s['intro']:
            intro_parts.append(s['intro'])
        if s['note']:
            intro_parts.append(s['note'])
        if s['is_vocal']:
            intro_parts.append("Có lời ca sĩ")
        intro_str = " - ".join(intro_parts)

        # Author logic: composer + singer if vocal
        author_parts = []
        if s['nhac']:
            author_parts.append(s['nhac'])
        if s['singer']:
            if s['nhac']:
                author_parts.append(f"(CS: {s['singer']})")
            else:
                author_parts.append(s['singer'])
        author_str = " ".join(author_parts) if author_parts else ''

        row = [
            s['stt'],
            s['code'],
            s['title'],
            intro_str,
            author_str,
            s['lang_id'],
            s['genre'],
            s['vol_num'],
            s['is_vocal'],
            0
        ]
        rows.append(row)

    # Write JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, separators=(',', ':'))
    print(f"  THÀNH CÔNG: Đã lưu JSON {json_path} ({os.path.getsize(json_path):,} bytes, {len(rows):,} bài)")

    # Write JS
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write("window.KARAOKE_DATA_DH=")
        json.dump(rows, f, ensure_ascii=False, separators=(',', ':'))
        f.write(";\n")
    print(f"  THÀNH CÔNG: Đã lưu JS {js_path} ({os.path.getsize(js_path):,} bytes)")

def update_version_json(version_path, count, vocal_count):
    if os.path.exists(version_path):
        with open(version_path, 'r', encoding='utf-8') as f:
            vdata = json.load(f)
        vdata['datasets']['donghai'] = {
            "vol": "Vol 83B",
            "vocal": vocal_count,
            "count": count
        }
        total_songs = sum(d.get('count', 0) for d in vdata.get('datasets', {}).values())
        vdata['totalSongs'] = total_songs
        with open(version_path, 'w', encoding='utf-8') as f:
            json.dump(vdata, f, ensure_ascii=False, indent=2)
        print(f"\nĐã cập nhật version.json: donghai count={count:,}, vocal={vocal_count:,}, tổng={total_songs:,}")

def main():
    base_dir = os.path.abspath(os.path.join(current_dir, '..'))
    
    excel_82 = os.path.join(base_dir, 'KTV Vol 82B Dong Hai.xlsx')
    excel_83 = os.path.join(base_dir, 'hanco Vol 83B Dong Hai.xlsx')
    meg_82 = os.path.join(base_dir, 'MEGIDX 82BKTV')
    meg_83 = os.path.join(base_dir, 'MEGIDX 83B')

    s82, s83, songs = build_donghai_dataset(excel_82, excel_83, meg_82, meg_83)

    out_excel = os.path.join(base_dir, 'LIST Nhạc Đông Hải.xlsx')
    export_to_excel(songs, out_excel)

    out_json = os.path.join(base_dir, 'data', 'donghai.json')
    out_js = os.path.join(base_dir, 'data', 'donghai.js')
    export_json_and_js(songs, out_json, out_js)

    vocal_count = sum(1 for s in songs if s['is_vocal'] == 1)
    version_json = os.path.join(base_dir, 'version.json')
    update_version_json(version_json, len(songs), vocal_count)

    print("\nHOÀN TẤT 100% QUÁ TRÌNH TẠO BỘ DATA ĐÔNG HẢI MỚI!")

if __name__ == '__main__':
    main()
