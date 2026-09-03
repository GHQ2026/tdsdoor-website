#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""站点质量门禁（机器验收，非人工目测）。

检查项：
  1. emoji 功能图标（P0-1）
  2. CSS 硬编码色值（P0-3，仅允许 #fff / #000）
  3. 紫粉渐变（P0-2）
  4. 弹跳缓动（P0-3）
  5. 内部死链
  6. 图片引用缺失 / 未引用
  7. LOGO 实际显示尺寸 vs 源图像素（防放大模糊）
  8. 首页首屏左右列宽与分栏比（从 CSS 解析，非目测）
  9. 卖点项数量一致性

用法：python src/tools/gate_check.py
退出码：0 全通过；1 存在阻断项
"""
import os
import re
import sys
import glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SITE = os.path.join(ROOT, "site")
CSS = os.path.join(SITE, "assets", "css", "style.css")

EMOJI = re.compile(
    "[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF\uFE00-\uFE0F"
    "\U0001F000-\U0001F02F\U0001F0A0-\U0001F0FF\U0001F100-\U0001F64F"
    "\U0001F680-\U0001F6FF\U0001FA00-\U0001FAFF\u200D\u20E3]"
)
BOUNCE = "cubic-bezier(0.68, -0.55, 0.265, 1.55)"
PURPLE_PINK = re.compile(r"#7C3AED|#A855F7|#EC4899|#6366F1|#4F46E5", re.I)

results = []


def check(name, ok, detail=""):
    results.append((ok, name, detail))
    return ok


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


# ---------- 采集 ----------
pages = sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True))
all_html = "".join(read(p) for p in pages)
css = read(CSS)

# 1. emoji
hits = {}
for p in pages:
    m = EMOJI.findall(read(p))
    if m:
        hits[os.path.relpath(p, SITE)] = set(m)
check("P0-1 emoji 功能图标", not hits, str(hits) if hits else "0 命中")

# 2. 硬编码色值
hexes = {h.lower() for h in re.findall(r"#[0-9a-fA-F]{3,8}\b", css)}
bad = sorted(h for h in hexes if h not in ("#fff", "#000"))
check("P0-3 CSS 硬编码色值", not bad, ",".join(bad) if bad else "0 命中")

# 3. 紫粉渐变
pp = PURPLE_PINK.findall(css)
check("P0-2 紫粉渐变", not pp, ",".join(set(pp)) if pp else "0 命中")

# 4. 弹跳缓动
check("P0-3 弹跳缓动", BOUNCE not in css.replace(" ", ""), "存在" if BOUNCE in css.replace(" ", "") else "无")

# 5. 死链
dead = []
for p in pages:
    base = os.path.dirname(p)
    for href in re.findall(r'href="([^"]+)"', read(p)):
        if href.startswith(("http", "mailto:", "tel:", "#")):
            continue
        if not os.path.exists(os.path.normpath(os.path.join(base, href.split("#")[0]))):
            dead.append((os.path.relpath(p, SITE), href))
check("内部死链", not dead, str(dead) if dead else "0")

# 6. 图片引用
missing = []
for p in pages:
    base = os.path.dirname(p)
    for src in re.findall(r'<img[^>]+src="([^"]+)"', read(p)):
        if src.startswith("http"):
            continue
        if not os.path.exists(os.path.normpath(os.path.join(base, src))):
            missing.append((os.path.relpath(p, SITE), src))
check("图片引用完整性", not missing, str(missing) if missing else "全部存在")


home = read(os.path.join(SITE, "index.html"))
about = read(os.path.join(SITE, "about.html"))

# 7. LOGO 显示尺寸 vs 源图像素 + 有效内容占比
# 关键：仅比对 max-width 与画布宽度是不够的。若源图含大量透明边距（如 logo-full.png
# 内容仅占 47.7%），画布像素再高也会被稀释 —— 可见内容反而更小。必须按 alpha 求内容框。
import struct as _struct
import zlib as _zlib


def png_size(path):
    d = open(path, "rb").read(33)
    if d[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h = _struct.unpack(">II", d[16:24])
    return w, h


def png_content_bbox(path):
    """返回 (画布w, 画布h, 内容w, 内容h)。alpha>24 视为不透明。"""
    d = open(path, "rb").read()
    pos, idat = 8, b""
    w = h = ct = None
    while pos < len(d):
        ln = _struct.unpack(">I", d[pos:pos + 4])[0]
        typ = d[pos + 4:pos + 8]
        body = d[pos + 8:pos + 8 + ln]
        pos += 12 + ln
        if typ == b"IHDR":
            w, h, _bd, ct, _c, _f, _i = _struct.unpack(">IIBBBBB", body)
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
    if ct != 6:
        return w, h, w, h
    bpp, stride = 4, w * 4
    raw = _zlib.decompress(idat)
    out = bytearray()
    prev = bytearray(stride)
    i = 0
    for _ in range(h):
        ft = raw[i]
        i += 1
        line = bytearray(raw[i:i + stride])
        i += stride
        if ft == 1:
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x - bpp]) & 255
        elif ft == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif ft == 3:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 255
        elif ft == 4:
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
    minx, miny, maxx, maxy = w, h, -1, -1
    for y in range(h):
        base = y * w * 4
        for x in range(w):
            if out[base + x * 4 + 3] > 24:
                if x < minx:
                    minx = x
                if x > maxx:
                    maxx = x
                if y < miny:
                    miny = y
                if y > maxy:
                    maxy = y
    return w, h, maxx - minx + 1, maxy - miny + 1


# 页面实际引用了哪些 LOGO
referenced = sorted(set(re.findall(r"images/(logo-[a-z-]+\.png)", all_html)))
logo_issues = []
logo_report = []
MIN_CONTENT_RATIO = 0.80   # 内容占比下限：低于此值说明画布含大量透明边距

for fn in referenced:
    fp = os.path.join(SITE, "assets", "images", fn)
    if not os.path.exists(fp):
        logo_issues.append("%s 缺失" % fn)
        continue
    cw, ch, bw, bh = png_content_bbox(fp)
    ratio = bw / cw
    logo_report.append("%s 内容占比%.0f%%" % (fn, 100 * ratio))
    if ratio < MIN_CONTENT_RATIO:
        logo_issues.append("%s 内容占比仅 %.0f%%（画布含大量透明边距，可见内容被稀释）" % (fn, 100 * ratio))

# 首屏 LOGO 的可见尺寸
m = re.search(r"\.hero-logo\s*\{[^}]*max-width:\s*(\d+)px", css)
hero_logo = re.search(r'class="hero-logo"[^>]*src="[^"]*images/([^"]+)"', home) \
    or re.search(r'src="[^"]*images/([^"]+)"[^>]*class="hero-logo"', home)
if hero_logo:
    fn = hero_logo.group(1)
    fp = os.path.join(SITE, "assets", "images", fn)
    cw, ch, bw, bh = png_content_bbox(fp)
    disp = int(m.group(1)) if m else cw
    vis_w = disp * bw / cw
    density = cw / disp
    logo_report.append("首屏LOGO可见 %.0fx%.0fpx 密度%.2fx" % (vis_w, vis_w * bh / bw, density))
    if disp > cw:
        logo_issues.append("首屏 %s 显示 %dpx > 画布 %dpx（放大失真）" % (fn, disp, cw))

check("LOGO 有效内容占比 ≥80%%（防透明边距稀释）",
      not logo_issues, "; ".join(logo_report) if not logo_issues else "; ".join(logo_issues))

# 8. 首屏分栏比
m = re.search(r"\.home-hero \.grid\s*\{([^}]*)\}", css)
if m:
    body = m.group(1)
    cols = re.search(r"grid-template-columns:\s*([^;]+);", body)
    cols = cols.group(1).strip() if cols else "未声明"
    gap = re.search(r"gap:\s*([^;]+);", body)
    check("首屏分栏声明", True, "columns: %s | gap: %s" % (cols, gap.group(1).strip() if gap else "默认"))
    # 计算实际比例（容器 1152px，即桌面 1200 容器减去 gutter）
    cw = 1152.0
    g = 64.0  # --space-16 默认值，宽松估计
    nums = re.findall(r"([\d.]+)(fr|px)", cols)
    if len(nums) == 2 and all(u == "fr" for _, u in nums):
        a, b = float(nums[0][0]), float(nums[1][0])
        total = a + b
        w1 = (cw - g) * a / total
        w2 = (cw - g) * b / total
        check("首屏左右比例 ≈4:6",
              0.30 <= a / total <= 0.46,
              "左 %.0fpx (%.0f%%) / 右 %.0fpx (%.0f%%)" % (w1, 100 * a / total, w2, 100 * b / total))
    else:
        check("首屏左右比例 ≈4:6", False, "无法解析 columns: %s" % cols)
else:
    check("首屏分栏声明", False, "未找到 .home-hero .grid")

# 9. 卖点项一致性
n_home = len(re.findall(r'class="stat[ "]', home))
n_about = len(re.findall(r'class="stat[ "]', about))
check("卖点项一致性", n_home == n_about == 4, "首页 %d / 关于页 %d" % (n_home, n_about))

# 10. 关于页卖点带未被误改
check("关于页 .stat-bar 保留", 'class="stat-bar"' in about, "存在" if 'class="stat-bar"' in about else "被移除")

# ---------- 输出 ----------
print("=" * 68)
print("站点质量门禁  |  页面 %d 个  |  CSS %d 行" % (len(pages), css.count("\n") + 1))
print("=" * 68)
fails = 0
for ok, name, detail in results:
    print("  [%s] %-28s %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        fails += 1
print("=" * 68)
print("结果：%d 项通过，%d 项阻断" % (len(results) - fails, fails))
sys.exit(1 if fails else 0)
