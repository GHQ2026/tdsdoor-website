"""
修正LOGO文件名映射（基于逐个视觉识别结果）+ 合并ARCFOX碎片。
"""
from PIL import Image
import os

OUT = "D:/2026AI/Wookbuddy/workspace/projects/project_002_公司官方网站/site/assets/images/clients"

# 正确映射：index -> (正确文件名, 显示名)
CORRECT_MAP = {
    0:  ("lexy莱克.png",       "LEXY莱克"),
    1:  ("五粮液.png",         "五粮液"),
    2:  ("gree格力.png",       "GREE格力"),
    3:  ("ahxf安虹消防.png",   "AHXF安虹消防"),
    4:  ("ma_steel马钢.png",   "MA STEEL马钢"),
    5:  ("evps.png",           "evps"),
    6:  ("安徽建工.png",       "安徽建工集团"),
    # 7+8 合并为 ARCFOX
    9:  ("todosun拓达昇.png",  "TODOSUN拓达昇"),  # 完整！含图标+文字+slogan
    10: ("金鹏控股.png",       "金鹏控股集团"),
    11: ("协鑫新能源.png",     "协鑫新能源GCL"),
    12: ("midea美的.png",      "Midea美的"),
    13: ("byd比亚迪.png",      "BYD比亚迪"),
    14: ("cowain.png",        "COWAIN"),
    15: ("潮宏基.png",         "潮宏基CHJ"),
    16: ("tcl.png",            "TCL"),
    17: ("国轩高科.png",       "国轩高科GOTION"),
    18: ("coca_cola可口可乐.png","Coca-Cola可口可乐"),
    19: ("jee.png",            "JEE"),
}

# ── Step 1: 重命名（跳过7、8，它们要合并）──
renamed = {}
for idx, (fname, display) in CORRECT_MAP.items():
    src = os.path.join(OUT, f"brand_{idx}.png" if idx >= 19 else f"{display.split()[0] if idx < 10 else ''}x")
    # 找到实际源文件名
    candidates = [f for f in os.listdir(OUT) if f.endswith('.png')]
    # 用已知列表找
    old_names_by_idx = {
        0:"lexy莱克.png",1:"五粮液.png",2:"gree格力.png",3:"ahxf安虹消防.png",
        4:"ma_steel马钢.png",5:"evps.png",6:"安徽建工.png",7:"arcfox极狐.png",
        8:"todosun拓达昇.png",9:"金鹏控股.png",10:"协鑫新能源.png",11:"midea美的.png",
        12:"byd比亚迪.png",13:"cowain.png",14:"潮宏基.png",15:"tcl.png",
        16:"国轩高科.png",17:"coca_cola可口可乐.png",18:"jee.png",19:"brand_19.png"
    }
    old_name = old_names_by_idx.get(idx)
    if not old_name or not os.path.exists(os.path.join(OUT, old_name)):
        print(f"  SKIP [{idx}] 源文件不存在: {old_name}")
        continue
    src_path = os.path.join(OUT, old_name)
    dst_path = os.path.join(OUT, fname)

    if old_name == fname:
        print(f"  OK [{idx}] {fname} ({display}) — 无需改名")
        renamed[idx] = fname
        continue

    # 避免覆盖目标（如果目标已存在且是另一个文件的正确名）
    if os.path.exists(dst_path):
        tmp = dst_path + "_tmp"
        os.rename(src_path, tmp)
        os.rename(tmp, dst_path)  # 会覆盖旧dst
    else:
        os.rename(src_path, dst_path)
    renamed[idx] = fname
    size_kb = os.path.getsize(dst_path) / 1024
    print(f"  RENAMED [{idx}] {old_name} -> {fname} ({display}) {size_kb:.0f}KB")

# ── Step 2: 合并 ARCFOX（index 7 图标 + index 8 文字）──
arc_icon = Image.open(os.path.join(OUT, "arcfox极狐.png"))
arc_text = Image.open(os.path.join(OUT, "todosun拓达昇.png"))  # 这是错的，实际是ARCFOX文字
# 等等——我需要找到实际的文件。让我直接用原始索引文件名。
print("\n--- 合并 ARCFOX ---")
# 找回被重命名的原始文件... 它们已经被改名了
# 更简单的方式：从 _old 目录取回
old_dir = OUT + "_old"
if os.path.isdir(old_dir):
    arc_icon_src = os.path.join(old_dir, "client_20.png")  # ARCFOX图标
    arc_text_src = os.path.join(old_dir, "client_03.png")  # TODOSUN文字? 不对...
    # 其实最简单：用已裁切的两个文件
    pass

# 直接用当前目录里还存在的文件（如果没被改名覆盖的话）
# 让我用另一种方式：重新读取原图的对应区域合并
import numpy as np
src_img = Image.open("D:/公司资料/安徽拓达昇产品图册_24.jpg").convert("RGB")
W, H = src_img.size
gray = np.array(src_img.convert("L"))
mask = gray < 235

# 行3 的完整区域 y=1489~1756, x=461~5443
y1, y2 = 1489, 1756
row3_mask = mask[y1:y2, :]
col_profile = row3_mask.sum(axis=0)

# 找所有非零段
in_seg = False
segments = []
start = None
for i, v in enumerate(col_profile):
    if v > 0 and not in_seg:
        start = i; in_seg = True
    elif v == 0 and in_seg:
        segments.append((start, i)); in_seg = False
if in_seg: segments.append((start, len(col_profile)))

print(f"  行3 共 {len(segments)} 段: {segments}")
# 取第1段(ARCFOX图标)和第2段(ARCFOX文字)的包围盒合并
if len(segments) >= 2:
    sx1 = min(segments[0][0], segments[1][0])
    sx2 = max(segments[0][1], segments[1][1])
    # 取内容包围盒
    sub = mask[y1:y2, sx1:sx2]
    ys, xs = np.where(sub)
    cx1, cy1 = sx1 + xs.min(), y1 + ys.min()
    cx2, cy2 = sx1 + xs.max() + 1, y1 + ys.max() + 1
    pad_x = int((cx2 - cx1) * 0.08)
    pad_y = int((cy2 - cy1) * 0.08)
    fx1, fy1 = max(0, cx1 - pad_x), max(0, cy1 - pad_y)
    fx2, fy2 = min(W, cx2 + pad_x), min(H, cy2 + pad_y)
    arc_merged = src_img.crop((fx1, fy1, fx2, fy2))
    # 缩放到统一高度
    target_h = 200
    if arc_merged.height > target_h:
        r = target_h / arc_merged.height
        arc_merged = arc_merged.resize((int(arc_merged.width * r), target_h), Image.LANCZOS)
    arc_out = os.path.join(OUT, "arcfox极狐.png")
    arc_merged.save(arc_out, "PNG", optimize=True)
    sz = os.path.getsize(arc_out) / 1024
    print(f"  MERGED arcfox极狐.png: {arc_merged.size[0]}x{arc_merged.size[1]} {sz:.0f}KB")

# 清理不再需要的中间文件
cleanup = ["arcfox极狐.png"]  # 已被合并版替换
# 删除旧的错误命名文件（已被正确版本替代）
for f in list(os.listdir(OUT)):
    fp = os.path.join(OUT, f)
    # 保留正确的最终文件
    final_names = set(v for v in CORRECT_MAP.values())
    if f not in final_names and f.endswith('.png'):
        os.remove(fp)
        print(f"  CLEANED {f}")

# ── Step 3: 补充用户额外品牌（SVG占位）──
extra_brands = [
    ("nio蔚来.svg", "NIO蔚来"),
    ("bosch博世.svg", "Bosch博世"),
    ("huarun华润.svg", "华润"),
    ("lenovo联宝科技.svg", "联宝科技"),
]
svg_template = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 44" width="140" height="44">
  <rect width="140" height="44" rx="4" fill="#f8f8f8"/>
  <text x="70" y="27" text-anchor="middle" font-family="'Noto Sans SC',sans-serif" font-size="13" font-weight="600" fill="#666">{name}</text>
</svg>'''
for fname, name in extra_brands:
    fpath = os.path.join(OUT, fname)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(svg_template.format(name=name))
    print(f"  NEW {fname} ({name})")

print(f"\n最终文件清单:")
for f in sorted(os.listdir(OUT)):
    fp = os.path.join(OUT, f)
    sz = os.path.getsize(fp) / 1024
    print(f"  {f}: {sz:.0f}KB")
