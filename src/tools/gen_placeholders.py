"""
生成产品占位图（方案C）。
设计：工业技术风——浅灰底 + 简洁门体线稿 + 产品名，看起来是"有意设计的占位"而非AI生成图。
后期替换：直接用同名 PNG/JPG 覆盖即可，无需改代码。
"""
import os

OUT = "D:/2026AI/Wookbuddy/workspace/projects/project_002_公司官方网站/site/assets/images"

# 需要生成占位图的产品：(文件名, 显示名, 英文名)
PLACEHOLDERS = [
    # 电动卷帘门类
    ("ph-electric-roller-1.svg", "电动抗风门", "Wind Resistant Door"),
    ("ph-electric-roller-2.svg", "铝合金型材门", "Aluminum Profile Door"),
    ("ph-electric-roller-3.svg", "电动车库门", "Garage Door"),
    ("ph-electric-roller-4.svg", "水晶门", "Crystal Door"),
    ("ph-electric-roller-5.svg", "电动网型门", "Mesh Door"),
    ("ph-electric-roller-6.svg", "不锈钢卷帘门", "Stainless Roller Door"),
    ("ph-electric-roller-7.svg", "弧形推拉门", "Arc Sliding Door"),
    ("ph-electric-roller-8.svg", "电动弧形门", "Arc Door"),
    # 电动伸缩门类
    ("ph-retractable-1.svg", "不锈钢伸缩门", "Retractable Door"),
    ("ph-retractable-2.svg", "铝合金伸缩门", "Aluminum Retractable Door"),
    ("ph-retractable-3.svg", "直线门", "Linear Door"),
    ("ph-retractable-4.svg", "段滑门", "Segment Sliding Door"),
    ("ph-retractable-5.svg", "悬浮门", "Floating Door"),
    # 防火门类
    ("ph-fireproof-1.svg", "无机布防火卷帘门", "Inorganic Fire Shutter"),
    ("ph-fireproof-2.svg", "钢制防火卷帘门", "Steel Fire Shutter"),
    ("ph-fireproof-3.svg", "钢制平开防火门", "Steel Fire Door"),
    ("ph-fireproof-4.svg", "挡烟垂壁", "Smoke Barrier"),
    # 智能门控类
    ("ph-smart-1.svg", "道闸", "Barrier Gate"),
    ("ph-smart-2.svg", "停车场车牌识别系统", "LPR System"),
    ("ph-smart-3.svg", "智能电动门", "Smart Door"),
    ("ph-smart-4.svg", "别墅庭院门", "Villa Gate"),
    ("ph-smart-5.svg", "岗亭", "Guard House"),
    ("ph-smart-6.svg", "玻璃感应门", "Glass Sensor Door"),
    ("ph-smart-7.svg", "人行通道摆闸", "Swing Gate"),
    # 日常维保类
    ("ph-maint-1.svg", "定期巡检保养", "Routine Inspection"),
    ("ph-maint-2.svg", "紧急故障抢修", "Emergency Repair"),
    ("ph-maint-3.svg", "配件供应更换", "Parts Supply"),
    ("ph-maint-4.svg", "门体升级改造", "Door Upgrade"),
    ("ph-maint-5.svg", "年度维保合约", "Annual Contract"),
]

# 工业技术风 SVG 模板：浅灰底 + 门体线稿 + 产品名
TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="400" height="300" role="img" aria-label="{name}">
  <rect width="400" height="300" fill="#F4F5F7"/>
  <!-- 背景网格：技术图纸感 -->
  <defs>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#E3E6EA" stroke-width="1"/>
    </pattern>
  </defs>
  <rect width="400" height="300" fill="url(#grid)"/>
  <!-- 门体线稿 -->
  <g stroke="#0B4F8C" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.75">
    <rect x="140" y="80" width="120" height="150" rx="3"/>
    <line x1="140" y1="115" x2="260" y2="115"/>
    <line x1="140" y1="150" x2="260" y2="150"/>
    <line x1="140" y1="185" x2="260" y2="185"/>
    <circle cx="248" cy="162" r="4"/>
  </g>
  <!-- 地面基线 -->
  <line x1="110" y1="230" x2="290" y2="230" stroke="#C9CDD4" stroke-width="2" stroke-linecap="round"/>
  <!-- 品牌色点缀 -->
  <rect x="140" y="248" width="120" height="3" rx="1.5" fill="#E8922A" opacity="0.85"/>
  <!-- 产品名 -->
  <text x="200" y="278" text-anchor="middle" font-family="'Noto Sans SC','Microsoft YaHei',sans-serif"
        font-size="15" font-weight="600" fill="#2B3138">{name}</text>
  <text x="200" y="294" text-anchor="middle" font-family="Inter,sans-serif"
        font-size="9" fill="#8A9199" letter-spacing="0.06em">{en}</text>
</svg>'''

os.makedirs(OUT, exist_ok=True)
count = 0
for fname, name, en in PLACEHOLDERS:
    svg = TEMPLATE.format(name=name, en=en)
    fpath = os.path.join(OUT, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(svg)
    count += 1
    print(f"  {fname}: {name}")

print(f"\n共生成 {count} 个占位图 → {OUT}")
print("提示：后期替换只需用同名 .png/.jpg 覆盖，并在 build.py 中把 .svg 改成对应扩展名")
