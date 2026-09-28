import struct
import sys
from export_donghai_excel import decode_text, clean_song_title

def parse_meg(data):
    p_start = data.find(b'1 2 3 Chia \xd1o\xe2i')
    p_tail = data.find(b'\xd7\xe6\xb9\xfa\xd7\xe6\xb9\xfa\xb6\xe0\xc3\xc0\xc0\xf6')
    p_code = p_tail + 14
    
    pos = data.find(b'popular\x05')
    if pos == -1: pos = 1159
    singers = []
    while pos < p_start:
        p05 = data.find(b'\x05', pos)
        if p05 == -1 or p05 >= p_start: break
        s_meta = data[p05:p05+5]
        s_cnt = s_meta[2] if len(s_meta) >= 3 else 0
        singers.append({'name': decode_text(data[pos:p05]), 'count': s_cnt})
        pos = p05 + 5
        
    records = []
    pos = p_start
    while pos < p_tail:
        p01 = data.find(b'\x01', pos)
        if p01 == -1 or p01 >= p_tail: break
        title = data[pos:p01]
        flag = data[p01+3]
        meta_len = 18 if (flag & 0x80) else 12
        meta = data[p01:p01+meta_len]
        records.append((title, meta, flag))
        pos = p01 + meta_len
    records.append((b'\xd7\xe6\xb9\xfa\xd7\xe6\xb9\xfa\xb6\xe0\xc3\xc0\xc0\xf6', b'', 2))
    
    table = data[p_code:]
    codes = []
    for i in range(len(table)//4):
        b = table[i*4 : (i+1)*4]
        code = (b[0] << 16) | (b[3] << 8) | b[2]
        codes.append(code)
    return singers, records, codes

with open('MEGIDX 82BKTV', 'rb') as f: d82 = f.read()
with open('MEGIDX 83B', 'rb') as f: d83 = f.read()

s82, r82, c82 = parse_meg(d82)
s83, r83, c83 = parse_meg(d83)

dict82 = {c: r for c, r in zip(c82, r82)}

diffs = []
for code, rec83 in zip(c83, r83):
    if code in dict82:
        rec82 = dict82[code]
        t82 = decode_text(rec82[0])
        t83 = decode_text(rec83[0])
        c82_title, _, _ = clean_song_title(t82)
        c83_title, _, _ = clean_song_title(t83)
        if c82_title.lower() != c83_title.lower():
            diffs.append((code, t82, t83))

print(f"Total meaningful diffs: {len(diffs)}")
for c, t1, t2 in diffs:
    print(f"Code {c}: [82B] {t1}  <===>  [83B] {t2}")
