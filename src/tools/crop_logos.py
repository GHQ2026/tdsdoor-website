#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""裁切 LOGO 透明边距，导出三个用途档位。

背景：素材 PNG 画布内含有大量透明留白（logo-white.png 有效内容仅占画布 8.9% 高度），
直接用 CSS 设定显示尺寸会导致实际可见标记过小。必须先按内容边界框裁切。

依赖：仅标准库（struct / zlib），无需 PIL。
用法：python src/tools/crop_logos.py
"""
import os
import struct
import zlib

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
IMG = os.path.join(ROOT, "site", "assets", "images")

# 源文件 -> (输出文件名, 裁切后四周留白比例)
JOBS = [
    ("logo-full.png", "logo-hero.png", 0.02),     # 完整版：Hero 左侧主视觉
    ("logo-nav.png", "logo-header.png", 0.02),    # 横版深色：导航栏（浅底）
    ("logo-white.png", "logo-footer.png", 0.02),  # 横版白色：页脚（深底）
]

ALPHA_MIN = 24  # 低于此 alpha 视为透明


def read_png(path):
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a png: %s" % path
    pos, idat = 8, b""
    w = h = bd = ct = None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
        if typ == b"IHDR":
            w, h, bd, ct, _, _, _ = struct.unpack(">IIBBBBB", body)
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
    assert bd == 8 and ct in (2, 6), "unsupported png (bitdepth=%s colortype=%s)" % (bd, ct)
    channels = 4 if ct == 6 else 3
    bpp = channels
    stride = w * bpp
    raw = zlib.decompress(idat)

    out = bytearray()
    prev = bytearray(stride)
    i = 0
    for _ in range(h):
        f = raw[i]
        i += 1
        line = bytearray(raw[i:i + stride])
        i += stride
        if f == 1:
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x - bpp]) & 255
        elif f == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif f == 3:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 255
        elif f == 4:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x - bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        out += line
        prev = line
    return w, h, bpp, bytes(out)


def content_bbox(w, h, bpp, px):
    minx, miny, maxx, maxy = w, h, -1, -1
    for y in range(h):
        base = y * w * bpp
        for x in range(w):
            if px[base + x * bpp + 3] > ALPHA_MIN:
                if x < minx:
                    minx = x
                if x > maxx:
                    maxx = x
                if y < miny:
                    miny = y
                if y > maxy:
                    maxy = y
    return minx, miny, maxx, maxy


def write_png(path, w, h, rows):
    """rows: list[bytes]，每行 RGBA，长度 w*4"""
    raw = bytearray()
    for r in rows:
        raw.append(0)  # filter type 0 (None)
        raw += r
    def chunk(typ, body):
        c = struct.pack(">I", len(body)) + typ + body
        return c + struct.pack(">I", zlib.crc32(typ + body) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) \
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    for src, dst, pad_ratio in JOBS:
        src_path = os.path.join(IMG, src)
        w, h, bpp, px = read_png(src_path)
        minx, miny, maxx, maxy = content_bbox(w, h, bpp, px)
        if maxx < 0:
            print("skip %s (empty)" % src)
            continue
        pad = int(max(maxx - minx + 1, maxy - miny + 1) * pad_ratio)
        x0 = max(0, minx - pad)
        y0 = max(0, miny - pad)
        x1 = min(w, maxx + 1 + pad)
        y1 = min(h, maxy + 1 + pad)
        cw, ch = x1 - x0, y1 - y0

        rows = []
        for y in range(y0, y1):
            base = y * w * bpp
            rows.append(px[base + x0 * bpp: base + x1 * bpp])
        dst_path = os.path.join(IMG, dst)
        write_png(dst_path, cw, ch, rows)
        print("%-16s %dx%d  ->  %-16s %dx%d  (ratio %.2f, %.1f KB)" % (
            src, w, h, dst, cw, ch, cw / ch, os.path.getsize(dst_path) / 1024.0))


if __name__ == "__main__":
    main()
