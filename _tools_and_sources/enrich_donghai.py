import os
import sys
import re
import json
import time
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

if sys.stdout and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def norm_title(s):
    if not s: return ''
    s = s.strip().lower()
    # remove parenthesized terms like (remix), (vc), (tân cổ), (a), etc.
    s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'\[.*?\]', ' ', s)
    # replace punctuation with spaces
    s = re.sub(r'[^\w\s]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def clean_name(n):
    if not n: return ''
    n = n.strip()
    if n in ['-', 'Music: -', 'Nhạc: -', 'Lyrics: -', 'Lời: -']:
        return ''
    return n

def build_reference_kb():
    print("[1/4] Xây dựng cơ sở dữ liệu đối chiếu từ Acnos, Paramax, MusicCore, Arirang, VietKTV, California, Vitek...")
    t0 = time.time()
    
    code_kb = {}
    title_kb = {}

    def put_entry(key_type, key, nhac, loi, intro, src=''):
        nhac = clean_name(nhac)
        loi = clean_name(loi)
        intro = clean_name(intro)
        if not loi and nhac: loi = nhac
        if not (nhac or loi or intro): return

        e = {'nhac': nhac, 'loi': loi, 'intro': intro, 'src': src}
        if key_type == 'code':
            if key not in code_kb:
                code_kb[key] = e
        elif key_type == 'title':
            if key not in title_kb:
                title_kb[key] = e
            else:
                curr = title_kb[key]
                if not curr['nhac'] and nhac: curr['nhac'] = nhac
                if not curr['loi'] and loi: curr['loi'] = loi
                if not curr['intro'] and intro: curr['intro'] = intro

    # 1. ACNOS
    if os.path.exists('List ACNOS (2017).xlsx'):
        wb_acnos = openpyxl.load_workbook('List ACNOS (2017).xlsx', read_only=True)
        for sname in ['Tiếng Việt', 'Tiếng Anh']:
            ws = wb_acnos[sname]
            for r in ws.iter_rows(values_only=True):
                if not r or not r[0]: continue
                c0 = str(r[0]).strip()
                if c0 in ['MÃ SỐ', 'CODE'] or 'SONGBOOK' in c0: continue
                t_raw = str(r[1] or '')
                a_raw = str(r[2] or '')
                lines = [ln.strip() for ln in t_raw.split('\n') if ln.strip()]
                title = lines[0] if lines else ''
                intro = lines[1] if len(lines) > 1 else ''
                nhac, loi = '', ''
                for al in a_raw.split('\n'):
                    al = al.strip()
                    if al.lower().startswith('nhạc:') or al.lower().startswith('music:'):
                        nhac = al.split(':', 1)[1].strip()
                    elif al.lower().startswith('lời:') or al.lower().startswith('lyrics:'):
                        loi = al.split(':', 1)[1].strip()
                
                codes = []
                if '/' in c0:
                    for p in c0.split('/'):
                        try: codes.append(int(p.strip()))
                        except: pass
                else:
                    try: codes.append(int(c0))
                    except: pass
                
                for c in codes:
                    put_entry('code', c, nhac, loi, intro, 'Acnos')
                tn = norm_title(title)
                if tn:
                    put_entry('title', tn, nhac, loi, intro, 'Acnos')

    # 2. Paramax VN & EN
    paramax_vn = '_tools_and_sources/Danh mục bài hát Paramax (cập nhật tới vol 52).xlsx'
    if os.path.exists(paramax_vn):
        wbp = openpyxl.load_workbook(paramax_vn, read_only=True)
        for r in wbp.active.iter_rows(min_row=2, values_only=True):
            tn = norm_title(str(r[1] or ''))
            if tn:
                put_entry('title', tn, str(r[3] or ''), str(r[4] or ''), str(r[5] or ''), 'ParamaxVN')

    paramax_en = '_tools_and_sources/Danh mục bài hát tiếng Anh (Paramax) (cập nhật tới vol 52).xlsx'
    if os.path.exists(paramax_en):
        wbpe = openpyxl.load_workbook(paramax_en, read_only=True)
        for r in wbpe.active.iter_rows(min_row=2, values_only=True):
            tn = norm_title(str(r[1] or ''))
            if tn:
                put_entry('title', tn, str(r[3] or ''), str(r[4] or ''), str(r[5] or ''), 'ParamaxEN')

    # 3. MusicCore
    musiccore_fn = '_tools_and_sources/Danh mục bài hát MusicCore (cập nhật tới vol 102).xlsx'
    if os.path.exists(musiccore_fn):
        wbm = openpyxl.load_workbook(musiccore_fn, read_only=True)
        for r in wbm.active.iter_rows(min_row=2, values_only=True):
            tn = norm_title(str(r[1] or ''))
            if tn:
                put_entry('title', tn, str(r[2] or ''), str(r[3] or ''), '', 'MusicCore')

    # 4. JSONs
    for name in ['arirang', 'california', 'vietktv', 'vitek']:
        fp = f'data/{name}.json'
        if os.path.exists(fp):
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    for r in json.load(f):
                        tn = norm_title(r[2])
                        if tn:
                            put_entry('title', tn, r[4], r[4], r[3], name)
            except Exception:
                pass

    print(f"  -> KB xây dựng xong trong {time.time()-t0:.2f}s: {len(code_kb):,} mã số, {len(title_kb):,} tên bài hát")
    return code_kb, title_kb

def query_metadata(code, title, code_kb, title_kb):
    tn = norm_title(title)
    res = {'nhac': '', 'loi': '', 'intro': ''}

    # 1. Check title match first (most accurate across independent brands)
    if tn and tn in title_kb:
        m = title_kb[tn]
        res['nhac'] = m['nhac']
        res['loi'] = m['loi']
        res['intro'] = m['intro']

    # 2. Check code match only if title is compatible
    if code in code_kb:
        c_entry = code_kb[code]
        # Verify compatibility: if res already has intro, does code match?
        # Only use code if res is missing fields AND either tn is substring or vice versa
        if not res['nhac'] or not res['intro']:
            # Check if title is reasonably close or empty
            if not res['nhac'] and c_entry['nhac']:
                # If we don't have nhac yet, check if code entry looks plausible
                res['nhac'] = c_entry['nhac']
                res['loi'] = c_entry['loi']
            if not res['intro'] and c_entry['intro']:
                res['intro'] = c_entry['intro']

    # Ensure loi is filled if nhac is present
    if not res['loi'] and res['nhac']:
        res['loi'] = res['nhac']

    return res

def enrich_workbook(file_path, code_kb, title_kb):
    print(f"\nĐang xử lý làm giàu dữ liệu cho: {file_path} ...")
    wb = openpyxl.load_workbook(file_path)

    # Styles
    font_header = Font(name='Calibri', size=11, bold=True)
    fill_header = PatternFill(start_color='00D9EAF7', end_color='00D9EAF7', fill_type='solid')
    font_data = Font(name='Calibri', size=11)
    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    border_thin = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    stats = {'total': 0, 'nhac': 0, 'loi': 0, 'intro': 0}

    for sheet_name in wb.sheetnames:
        if sheet_name == 'Thông tin':
            continue
        ws = wb[sheet_name]
        is_all_sheet = (sheet_name == 'Tất cả')

        # Read all existing rows
        old_rows = list(ws.iter_rows(values_only=True))
        if not old_rows:
            continue

        header = old_rows[0]
        data_rows = old_rows[1:]

        # Clear worksheet
        ws.delete_rows(1, ws.max_row)

        # Build new header
        if is_all_sheet:
            new_header = ['Index', 'Mã bài hát', 'Tên bài hát', 'Nhạc', 'Lời', 'Lời đầu', 'Ngôn ngữ']
        else:
            new_header = ['Index', 'Mã bài hát', 'Tên bài hát', 'Nhạc', 'Lời', 'Lời đầu']

        # Write header
        ws.append(new_header)
        for col_idx in range(1, len(new_header) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = font_header
            cell.fill = fill_header
            cell.border = border_thin
            cell.alignment = align_center if col_idx in [1, 2, 7] else align_left

        # Write data rows
        for row_idx, r in enumerate(data_rows, start=2):
            idx_val = r[0]
            code_val = r[1]
            title_val = str(r[2] or '').strip()
            lang_val = r[5] if is_all_sheet and len(r) > 5 else ''

            meta = query_metadata(code_val, title_val, code_kb, title_kb)
            nhac_val = meta['nhac']
            loi_val = meta['loi']
            intro_val = meta['intro']

            if is_all_sheet:
                stats['total'] += 1
                if nhac_val: stats['nhac'] += 1
                if loi_val: stats['loi'] += 1
                if intro_val: stats['intro'] += 1
                new_row = [idx_val, code_val, title_val, nhac_val, loi_val, intro_val, lang_val]
            else:
                new_row = [idx_val, code_val, title_val, nhac_val, loi_val, intro_val]

            ws.append(new_row)
            for col_idx in range(1, len(new_row) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.font = font_data
                cell.border = border_thin
                cell.alignment = align_center if col_idx in [1, 2, 7] else align_left

        # Set column widths
        ws.column_dimensions['A'].width = 9.0
        ws.column_dimensions['B'].width = 14.0
        ws.column_dimensions['C'].width = 50.0
        ws.column_dimensions['D'].width = 28.0
        ws.column_dimensions['E'].width = 28.0
        ws.column_dimensions['F'].width = 55.0
        if is_all_sheet:
            ws.column_dimensions['G'].width = 18.0

        ws.freeze_panes = 'A2'
        print(f"  -> Sheet '{sheet_name}': hoàn thành {len(data_rows):,} bài hát.")

    wb.save(file_path)
    print(f"  THÀNH CÔNG: Đã lưu {file_path}")
    print(f"  Thống kê: Nhạc={stats['nhac']:,}/{stats['total']:,} ({stats['nhac']*100/stats['total']:.1f}%), Lời={stats['loi']:,}/{stats['total']:,} ({stats['loi']*100/stats['total']:.1f}%), Lời đầu={stats['intro']:,}/{stats['total']:,} ({stats['intro']*100/stats['total']:.1f}%)")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    f82 = os.path.join(base_dir, 'KTV Vol 82B Dong Hai.xlsx')
    f83 = os.path.join(base_dir, 'hanco Vol 83B Dong Hai.xlsx')

    code_kb, title_kb = build_reference_kb()

    enrich_workbook(f82, code_kb, title_kb)
    enrich_workbook(f83, code_kb, title_kb)

    print("\n[3/4] Cập nhật lại bộ dữ liệu hợp nhất Đông Hải (LIST Nhạc Đông Hải.xlsx, donghai.json, donghai.js)...")
    # Run build_donghai_data.py
    import build_donghai_data
    build_donghai_data.main()

if __name__ == '__main__':
    main()
