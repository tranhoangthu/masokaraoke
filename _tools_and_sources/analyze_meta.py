import sys
import struct
import os

for fname, p_singer_start, p_start, p_tail in [
    ('MEGIDX 82BKTV', 1463, 26624, 378315),
    ('MEGIDX 83B', 1159, 18925, 257501)
]:
    with open(fname, 'rb') as f:
        d = f.read()

    # Sample 15 records with full metadata bytes
    pos = p_start
    cnt = 0
    print(f'=== {fname} ===')
    while pos < p_tail and cnt < 15:
        p01 = d.find(b'\x01', pos)
        if p01 == -1 or p01 >= p_tail:
            break
        title_bytes = d[pos:p01]
        flag = d[p01+3]
        mlen = 18 if (flag & 0x80) else 12
        meta = d[p01:p01+mlen]
        
        print(f'  [{cnt}] Title raw: {title_bytes[:40]}')
        print(f'       Meta hex({mlen}): {meta.hex()}')
        print(f'       flag=0x{flag:02X} lang_id={flag & 0x7F}')
        
        # Decode each byte of meta
        # meta[0] = 0x01 delimiter
        # meta[1..3] = ?
        # meta[8:12] = MEGMID offset
        megmid_off = struct.unpack('<I', meta[8:12])[0] if len(meta) >= 12 else 0
        print(f'       MEGMID offset: {megmid_off} (0x{megmid_off:08X})')
        
        if mlen == 18:
            s_idx = struct.unpack('<H', meta[16:18])[0]
            print(f'       singer_idx={s_idx}')
        
        # All 12 or 18 bytes broken down
        for bi in range(mlen):
            print(f'       meta[{bi:2d}] = 0x{meta[bi]:02X} ({meta[bi]:3d})', end='')
            if (bi+1) % 4 == 0: print()
        print()
        print()
        
        pos = p01 + mlen
        cnt += 1
