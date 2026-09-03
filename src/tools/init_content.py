"""
从 build.py 抽取全站可编辑文案，生成 content/content.json。
用 ast 解析，避免手抄出错。已存在 content.json 时默认不覆盖（除非 --force）。
"""
import ast
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
BUILD = ROOT / "src" / "build.py"
OUT = ROOT / "content" / "content.json"

SCALARS = ["PHONE", "EMAIL", "ADDR", "COMPANY",
           "SLOGAN", "HERO_TITLE", "HERO_SUB", "HERO_MOTTO"]
LISTS = ["STATS", "PRODUCTS", "CATEGORIES", "CLIENT_LOGO_ROWS", "CASES", "NEWS"]


def extract():
    src = BUILD.read_text(encoding="utf-8")
    tree = ast.parse(src)
    values = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in SCALARS + LISTS:
                    try:
                        values[t.id] = ast.literal_eval(node.value)
                    except Exception as e:
                        print(f"  [warn] 跳过 {t.id}: {e}")
    return src, values


def extract_about_intro(src):
    """从 build_about() 的 f-string 里提取企业简介两段正文。"""
    m = re.search(r'def build_about\(\):(.*?)\n    \(BASE', src, re.S)
    if not m:
        return None
    block = m.group(1)
    # 提取 prose 里的两个 <p>...</p>
    paras = re.findall(r'<p>(.*?)</p>', block, re.S)
    cleaned = []
    for p in paras:
        # 去掉 {COMPANY} 等插值占位符
        p = p.replace("{COMPANY}", "").replace("{SLOGAN}", "")
        p = p.replace("——", "")
        p = p.strip()
        # 只保留看起来像正文的长段落
        if len(p) > 50:
            cleaned.append(p)
    return cleaned


def main():
    force = "--force" in sys.argv
    if OUT.exists() and not force:
        print(f"content.json 已存在，跳过（如需重建加 --force）\n  {OUT}")
        return

    src, values = extract()
    intro = extract_about_intro(src)

    content = {
        "_meta": {
            "说明": "本文件是网站全部可编辑文案。修改后运行 python src/build.py 重新生成页面，或在后台点保存自动生效。",
            "注意": "image 字段只填文件名，图片本体放在 site/assets/images/ 下",
        },
        "site": {k: values.get(k, "") for k in SCALARS},
        "stats": values.get("STATS", []),
        "products": values.get("PRODUCTS", []),
        "categories": values.get("CATEGORIES", []),
        "clients": values.get("CLIENT_LOGO_ROWS", []),
        "cases": values.get("CASES", []),
        "news": values.get("NEWS", []),
        "about": {
            "title": "企业简介",
            "subtitle": "专注工业门领域，以可靠的产品与规范的服务赢得客户信赖",
            "intro": intro or [],
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"已生成 {OUT}")
    print(f"  site 标量 {len(content['site'])} 项")
    for key in ["stats", "products", "categories", "clients", "cases", "news"]:
        print(f"  {key}: {len(content[key])} 条")
    print(f"  about.intro: {len(content['about']['intro'])} 段")


if __name__ == "__main__":
    main()
