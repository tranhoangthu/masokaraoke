"""
Analyze meta byte meanings more carefully.
meta[1] = title length (bytes of title)
meta[2] = ?
meta[3] = flag (lang + has_singer flag)
meta[4:8] = some kind of secondary offset/data?
meta[8:12] = MEGMID offset (confirmed)
meta[12:16] = ? (could be MEGMID block size)
meta[16:18] = singer index (confirmed, only when flag & 0x80)
"""
import sys
import struct

sys.stdout.reconfigure(encoding='utf-8')

for fname, p_singer_start, p_start, p_tail in [
    ('MEGIDX 82BKTV', 1463, 26624, 378315),
]:
    with open(fname, 'rb') as f:
        d = f.read()

    # Parse singers
    singers = []
    pos = p_singer_start
    while pos < p_start:
        p05 = d.find(b'\x05', pos)
        if p05 == -1 or p05 >= p_start:
            break
        smeta = d[p05:p05+5]
        sname_bytes = d[pos:p05]
        singers.append({
            'name_bytes': sname_bytes,
            'meta': smeta,
            'idx_in_list': len(singers),
        })
        pos = p05 + 5

    print(f'=== {fname} - Total {len(singers)} singers ===')
    print('First 30 singers:')
    for i, s in enumerate(singers[:30]):
        # Show all 5 meta bytes
        m = s['meta']
        print(f'  [{i:4d}] meta={m.hex()} bytes={[m[j] for j in range(5)]} name_bytes={s["name_bytes"][:30]}')

    print('\nLast 30 singers:')
    for i, s in enumerate(singers[-30:], start=len(singers)-30):
        m = s['meta']
        print(f'  [{i:4d}] meta={m.hex()} bytes={[m[j] for j in range(5)]} name_bytes={s["name_bytes"][:30]}')

    # Look at singer indices referenced in songs
    pos = p_start
    unique_sidx = set()
    cnt = 0
    while pos < p_tail:
        p01 = d.find(b'\x01', pos)
        if p01 == -1 or p01 >= p_tail:
            break
        flag = d[p01+3]
        mlen = 18 if (flag & 0x80) else 12
        meta = d[p01:p01+mlen]
        if mlen == 18:
            s_idx = struct.unpack('<H', meta[16:18])[0]
            unique_sidx.add(s_idx)
        pos = p01 + mlen

    print(f'\nUnique singer indices in songs: {len(unique_sidx)}')
    print(f'Min: {min(unique_sidx)}, Max: {max(unique_sidx)}')
    oob = [x for x in unique_sidx if x >= len(singers)]
    print(f'Out-of-range indices: {len(oob)}')
    if oob[:10]:
        print(f'OOB samples: {sorted(oob)[:10]}')
    
    # What is meta[1]? Let's check against title length
    pos = p_start
    mismatches = 0
    for i in range(200):
        p01 = d.find(b'\x01', pos)
        if p01 == -1 or p01 >= p_tail:
            break
        title_bytes = d[pos:p01]
        flag = d[p01+3]
        mlen = 18 if (flag & 0x80) else 12
        meta = d[p01:p01+mlen]
        
        title_len = len(title_bytes)
        meta1 = meta[1]
        
        if meta1 != title_len:
            mismatches += 1
            if mismatches <= 5:
                print(f'  MISMATCH: title_len={title_len} meta[1]={meta1} title={title_bytes[:30]}')
        
        pos = p01 + mlen
    
    print(f'\nmeta[1] vs title_len mismatches (first 200 songs): {mismatches}')
