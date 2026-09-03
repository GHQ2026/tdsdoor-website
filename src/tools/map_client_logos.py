"""
品牌LOGO映射与重命名 + 补充缺失品牌。
从自动检测结果映射到真实品牌名，处理拆分问题，为图册外的4个品牌生成SVG占位。
"""
import os
import shutil

SRC_DIR = "D:/2026AI/Wookbuddy/workspace/projects/project_002_公司官方网站/site/assets/images/clients"

# 从图册第24页检测到的品牌映射（基于视觉识别）
# 格式: 目标文件名 -> (源文件名, 显示名称, 备注)
BRAND_MAP = {
    # === 图册中有的品牌（按原图排列顺序）===
    "lexy.png":          ("client_15.png", "LEXY莱克",        "左侧略截断，可接受"),
    "wuliangye.png":     ("client_08.png", "五粮液",           "蓝色圆形H标"),
    "gree.png":          ("client_17.png", "GREE格力",         "图标部分"),
    "ahxf.png":          ("client_01.png", "AHXF安虹消防",    "完整"),
    "ma_steel.png":      ("client_06.png", "MA STEEL马钢",    "完整"),
    "evps.png":          ("client_16.png", "evps",             "完整"),
    "anhui_jiangong.png":("client_07.png", "安徽建工集团",    "完整"),
    "arcfox.png":        ("client_20.png", "ARCFOX极狐",      "仅图标，缺文字"),
    "todosun.png":       ("client_03.png", "TODOSUN拓达昇",   "文字部分，用logo-hero替代"),
    "jinpeng.png":       ("client_14.png", "金鹏控股集团",     "文字部分"),
    "gcl_newenergy.png": ("client_09.png", "协鑫新能源",       "完整"),
    "midea.png":         ("client_05.png", "Midea美的",        "完整"),
    "byd.png":           ("client_11.png", "BYD比亚迪",        "完整"),
    "cowain.png":        ("client_00.png", "COWAIN",           "完整"),
    "chj_jewellery.png": ("client_10.png", "潮宏基CHJ",        "完整"),
    "tcl.png":           ("client_13.png", "TCL",              "完整红色方块"),
    "gotion.png":        ("client_02.png", "国轩高科",          "完整"),
    "coca_cola.png":     ("client_12.png", "Coca-Cola可口可乐","完整"),
    "jee.png":           ("client_04.png", "JEE",              "完整"),
}

# === 图册中没有、用户额外提到的4个品牌 ===
EXTRA_BRANDS = ["nio蔚来", "bosch博世", "huarun华润", "lenovo联宝科技"]

# 执行重命名
renamed = []
for dst_name, (src_name, display, note) in BRAND_MAP.items():
    src = os.path.join(SRC_DIR, src_name)
    dst = os.path.join(SRC_DIR, dst_name)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        renamed.append((dst_name, display, note))
        print(f"  OK {src_name} -> {dst_name} ({display})")
    else:
        print(f"  MISS {src_name}")

# 拓达昇用已有的高清logo（不用裁切的版本）
todosun_src = "D:/2026AI/Wookbuddy/workspace/projects/project_002_公司官方网站/site/assets/images/logo-hero.png"
todosun_dst = os.path.join(SRC_DIR, "todosun.png")
if os.path.exists(todosun_src):
    shutil.copy2(todosun_src, todosun_dst)
    print(f"  OK logo-hero.png -> todosun.png (拓达昇高清版)")

# 为缺失的4个品牌生成简洁SVG文字标
svg_template = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 40" width="120" height="40">
  <rect width="120" height="40" rx="4" fill="#f5f5f5"/>
  <text x="60" y="25" text-anchor="middle" font-family="Inter,'Noto Sans SC',sans-serif" font-size="14" font-weight="600" fill="#555">{name}</text>
</svg>'''

for brand in EXTRA_BRANDS:
    safe = brand.split()[0].lower()
    svg_content = svg_template.format(name=brand)
    svg_path = os.path.join(SRC_DIR, f"{safe}.svg")
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"  NEW {safe}.svg ({brand}) - SVG占位")

print(f"\n总计: {len(renamed)} 个图册LOGO + 1 个拓达昇 + {len(EXTRA_BRANDS)} 个占位 = {len(renamed)+1+len(EXTRA_BRANDS)} 个品牌文件")
