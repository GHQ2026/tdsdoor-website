"""
最终版：从图册第24页裁切客户LOGO，直接输出正确文件名。
"""
from PIL import Image
import numpy as np
import os, shutil

SRC = "D:/公司资料/安徽拓达昇产品图册_24.jpg"
OUT = "D:/2026AI/Wookbuddy/workspace/projects/project_002_公司官方网站/site/assets/images/clients"

img = Image.open(SRC).convert("RGB")
W, H = img.size
gray = np.array(img.convert("L"))
mask = gray < 235

def find_bands(profile, min_gap=60, min_len=30):
    bands, start = [], None
    for i, v in enumerate(profile):
        if v > 0 and start is None: start = i
        elif v == 0 and start is not None:
            if i - start >= min_len: bands.append([start, i])
            start = None
    if start is not None and len(profile) - start >= min_len: bands.append([start, len(profile)])
    merged = []
    for b in bands:
        if merged and b[0] - merged[-1][1] < min_gap: merged[-1][1] = b[1]
        else: merged.append(b)
    return merged

# 行切分
row_bands = find_bands(mask.sum(axis=1), min_gap=60, min_len=30)

cells = []
for y1, y2 in row_bands:
    col_bands = find_bands(mask[y1:y2].sum(axis=0), min_gap=70, min_len=30)
    for x1, x2 in col_bands:
        cells.append((x1, y1, x2, y2))

print(f"检测到 {len(cells)} 个单元格")

# 正确的品牌名（按单元格阅读顺序：先行后列，行内左→右）
# 基于逐个视觉识别确认
NAMES = [
    "lexy莱克", "五粮液", "gree格力",           # 行1: 3个
    "ahxf安虹消防", "ma_steel马钢", "evps", "安徽建工",  # 行2: 4个
    # 行3: ARCFOX被拆成2格(图标+文字)，TODOSUN，金鹏 → 4格但3品牌
    "arcfox极狐",      # 格7: ARCFOX图标(碎片) — 后面合并处理
    "arcfox极狐_text", # 格8: ARCFOX文字(碎片) — 后面合并处理
    "todosun拓达昇",   # 格9: 完整！含图标+文字+slogan
    "金鹏控股集团",     # 格10
    "协鑫新能源",       # 行4第1格
    "midea美的",        # 行4第2格
    "byd比亚迪",        # 行4第3格
    "cowain",           # 行4第4格
    "潮宏基",           # 行5第1格
    "tcl",              # 行5第2格
    "国轩高科",         # 行5第3格
    "coca_cola可口可乐",# 行5第4格
    "jee",              # 行5第5格
]

# 清空重建（先移到 _old2）
if os.path.isdir(OUT):
    for i in range(100):
        bak = OUT + f"_bak{i}"
        if not os.path.exists(bak):
            os.rename(OUT, bak); break
os.makedirs(OUT, exist_ok=True)

TARGET_H = 200  # 统一最大高度
PAD = 0.08

for i, (x1, y1, x2, y2) in enumerate(cells):
    sub_mask = mask[y1:y2, x1:x2]
    ys, xs = np.where(sub_mask)
    if len(xs) == 0: continue
    cx1, cy1 = x1 + xs.min(), y1 + ys.min()
    cx2, cy2 = x1 + xs.max() + 1, y1 + ys.max() + 1
    cw, ch = cx2 - cx1, cy2 - cy1
    if cw < 50 or ch < 25: continue

    pw, ph = int(cw * PAD), int(ch * PAD)
    crop = img.crop((max(0,cx1-pw), max(0,cy1-ph), min(W,cx2+pw), min(H,cy2+ph)))
    if crop.height > TARGET_H:
        r = TARGET_H / crop.height
        crop = crop.resize((int(crop.width * r), TARGET_H), Image.LANCZOS)

    name = NAMES[i] if i < len(NAMES) else f"brand_{i}"
    fname = name + ".png"
    crop.save(os.path.join(OUT, fname), "PNG", optimize=True)
    print(f"  [{i:02d}] {fname}: {crop.size[0]}x{crop.size[1]}")

# ── 合并 ARCFOX（格7图标 + 格8文字）──
f_icon = os.path.join(OUT, "arcfox极狐.png")
f_text = os.path.join(OUT, "arcfox极狐_text.png")
if os.path.exists(f_icon) and os.path.exists(f_text):
    icon = Image.open(f_icon)
    text = Image.open(f_text)
    gap = 12  # 图标与文字间距
    merged_w = icon.width + gap + text.width
    merged_h = max(icon.height, text.height)
    merged = Image.new("RGB", (merged_w, merged_h), (255,255,255))
    merged.paste(icon, (0, (merged_h - icon.height)//2))
    merged.paste(text, (icon.width + gap, (merged_h - text.height)//2))
    if merged.height > TARGET_H:
        r = TARGET_H / merged.height
        merged = merged.resize((int(merged.width * r), TARGET_H), Image.LANCZOS)
    merged.save(f_icon, "PNG", optimize=True)
    os.remove(f_text)
    sz = os.path.getsize(f_icon) / 1024
    print(f"  [MERGED] arcfox极狐.png: {merged.size[0]}x{merged.size[1]} {sz:.0f}KB (icon+text)")

# ── 补充用户额外品牌 SVG 占位 ──
extras = {"nio蔚来":"NIO蔚来","bosch博世":"Bosch博世","huarun华润":"华润","lenovo联宝科技":"联宝科技"}
svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 44"><rect width="140" height="44" rx="4" fill="#f8f8f8"/><text x="70" y="28" text-anchor="middle" font-family="\'Noto Sans SC\',sans-serif" font-size="13" font-weight="600" fill="#666">{n}</text></svg>'
for fn, n in extras.items():
    with open(os.path.join(OUT, fn+".svg"), 'w', encoding='utf-8') as f:
        f.write(svg.format(n=n))
    print(f"  [NEW] {fn}.svg ({n})")

print(f"\n总计: {len([f for f in os.listdir(OUT) if not f.startswith('.')])} 个文件")
for f in sorted(os.listdir(OUT)):
    fp = os.path.join(OUT, f)
    print(f"  {f}: {os.path.getsize(fp)/1024:.0f}KB")
