"""
从PPT风格产品图册中提取主照片区域。
混合策略：自动纹理检测 + 关键图片手动预设区域。
"""
from PIL import Image
import numpy as np
from pathlib import Path

OUT_DIR = Path("site/assets/images")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def auto_crop(img: Image.Image):
    """自动检测最大照片区域，返回裁剪后的图。"""
    w, h = img.size
    # 缩小分析
    thumb = img.convert("RGB").resize((400, int(400 * h / w)), Image.Resampling.LANCZOS)
    arr = np.array(thumb).astype(np.float32)
    th, tw, _ = arr.shape

    # 局部方差（简单滑动窗口）
    k = 5
    from scipy.ndimage import uniform_filter
    var = np.zeros((th, tw), dtype=np.float32)
    for c in range(3):
        mean_c = uniform_filter(arr[:, :, c], size=k, mode="reflect")
        mean2_c = uniform_filter(arr[:, :, c] ** 2, size=k, mode="reflect")
        var += np.clip(mean2_c - mean_c ** 2, 0, None)
    texture = np.sqrt(var)

    threshold = np.percentile(texture, 45)
    mask = texture > threshold

    row_sum = mask.sum(axis=1)
    col_sum = mask.sum(axis=0)
    row_thr = tw * 0.12
    col_thr = th * 0.12
    photo_rows = row_sum > row_thr
    photo_cols = col_sum > col_thr

    def longest_segment(bits):
        best = (0, 0)
        cur_start = 0
        in_seg = False
        for i, b in enumerate(bits):
            if b and not in_seg:
                cur_start = i
                in_seg = True
            elif not b and in_seg:
                if i - cur_start > best[1] - best[0]:
                    best = (cur_start, i)
                in_seg = False
        if in_seg and len(bits) - cur_start > best[1] - best[0]:
            best = (cur_start, len(bits))
        return best

    r0, r1 = longest_segment(photo_rows)
    c0, c1 = longest_segment(photo_cols)

    scale_x = w / tw
    scale_y = h / th
    left = max(0, int(c0 * scale_x) - 8)
    top = max(0, int(r0 * scale_y) - 8)
    right = min(w, int(c1 * scale_x) + 8)
    bottom = min(h, int(r1 * scale_y) + 8)

    if (right - left) * (bottom - top) < w * h * 0.12:
        left, top, right, bottom = 0, 0, w, int(h * 0.70)

    return img.crop((left, top, right, bottom))


def save_thumb(img: Image.Image, target_w: int, target_h: int, out_name: str):
    """保持比例缩放到目标框内，保存PNG。"""
    img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    out_path = OUT_DIR / out_name
    img.save(out_path, "PNG", optimize=True)
    print(f"  -> {out_name}: {img.size}")


# ========== 批量处理配置 ==========
# 每条: (源图册, 输出名, 目标尺寸, 裁剪模式)
# 裁剪模式: 'auto' | (left%, top%, right%, bottom%) 百分比

JOBS = [
    # --- 工业门6款（大卡 1200x800）---
    ("D:/公司资料/安徽拓达昇产品图册_2.jpg",  "pvc-fast-door.png",           (1200, 800), "auto"),
    ("D:/公司资料/安徽拓达昇产品图册_3.jpg",  "turbine-hard-fast-door.png",  (1200, 800), (0, 0, 65, 55)),   # 取上左大图
    ("D:/公司资料/安徽拓达昇产品图册_4.jpg",  "accumulation-door.png",       (1200, 800), (45, 0, 100, 75)),  # 取右侧大图
    ("D:/公司资料/安徽拓达昇产品图册_6.jpg",  "lift-door.png",               (1200, 800), (0, 0, 45, 70)),    # 取左侧大图
    ("D:/公司资料/安徽拓达昇产品图册_7.jpg",  "roller-hard-fast-door.png",   (1200, 800), (0, 0, 58, 65)),    # 取左侧大图

    # --- 电动卷帘门类（标准 800x600）---
    ("D:/公司资料/安徽拓达昇产品图册_19.jpg", "wind-resistant-door.png",     (800, 600), (0, 0, 55, 50)),     # 上左大图
    ("D:/公司资料/安徽拓达昇产品图册_20.jpg", "aluminum-profile-door.png",   (800, 600), (35, 0, 100, 72)),   # 右下/右上大图
    ("D:/公司资料/安徽拓达昇产品图册_21.jpg", "crystal-door.png",            (800, 600), (50, 10, 100, 75)),  # 右下商场水晶门
    ("D:/公司资料/安徽拓达昇产品图册_22.jpg", "mesh-door.png",               (800, 600), (50, 10, 100, 55)),  # 右上/下网型门
    ("D:/公司资料/安徽拓达昇产品图册_22.jpg", "stainless-roller-door.png",   (800, 600), (0, 0, 48, 50)),     # 左上不锈钢卷帘门
    ("D:/公司资料/安徽拓达昇产品图册_23.jpg", "arc-sliding-door.png",        (800, 600), (50, 55, 100, 100)), # 右下Five Plus弧形门

    # --- 电动伸缩门类（标准 800x600）---
    ("D:/公司资料/安徽拓达昇产品图册_11.jpg", "ss-retractable-door.png",     (800, 600), (0, 0, 55, 55)),     # 左上伸缩门
    ("D:/公司资料/安徽拓达昇产品图册_10.jpg", "segment-sliding-door.png",    (800, 600), (48, 0, 100, 65)),   # 右侧段滑门
    ("D:/公司资料/安徽拓达昇产品图册_9.jpg",  "floating-door.png",           (800, 600), (0, 0, 60, 50)),     # 左上悬浮门
    ("D:/公司资料/安徽拓达昇产品图册_8.jpg",  "linear-door.png",             (800, 600), (50, 40, 100, 100)), # 下右直线门大图

    # --- 防火门类（标准 800x600）---
    ("D:/公司资料/安徽拓达昇产品图册_16.jpg", "inorganic-fire-shutter.png",  (800, 600), (0, 0, 50, 50)),     # 左上防火卷帘
    ("D:/公司资料/安徽拓达昇产品图册_17.jpg", "steel-fire-door.png",         (800, 600), (0, 0, 35, 65)),     # 左侧防火门
    ("D:/公司资料/安徽拓达昇产品图册_18.jpg", "smoke-barrier.png",           (800, 600), (0, 20, 48, 100)),   # 左下活动式挡烟垂壁

    # --- 智能门控类（标准 800x600）---
    ("D:/公司资料/安徽拓达昇产品图册_12.jpg", "barrier-gate.png",            (800, 600), (0, 0, 65, 45)),     # 上左道闸夜景
    ("D:/公司资料/安徽拓达昇产品图册_13.jpg", "access-control.png",          (800, 600), (0, 0, 35, 45)),     # 左上车牌识别立柱
]


def main():
    for src, out_name, target, mode in JOBS:
        try:
            img = Image.open(src)
            w, h = img.size
            if mode == "auto":
                cropped = auto_crop(img)
            else:
                l, t, r, b = mode
                left = int(w * l / 100)
                top = int(h * t / 100)
                right = int(w * r / 100)
                bottom = int(h * b / 100)
                cropped = img.crop((left, top, right, bottom))
            save_thumb(cropped, target[0], target[1], out_name)
        except Exception as e:
            print(f"  ERROR {out_name}: {e}")


if __name__ == "__main__":
    main()
