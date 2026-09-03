# -*- coding: utf-8 -*-
"""
拓达昇官网 · 本地内容后台（零依赖，仅用 Python 标准库）
启动后浏览器访问 http://localhost:5000
改完点"保存并重新生成"，会自动写入 content/content.json 并重建 site/ 全部页面。
"""
import base64
import json
import mimetypes
import pathlib
import re
import shutil
import subprocess
import sys
import threading
import webbrowser
from urllib.parse import unquote
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT_FILE = ROOT / "content" / "content.json"
BACKUP_DIR = ROOT / "content" / "backups"
ADMIN_DIR = pathlib.Path(__file__).resolve().parent
BUILD = ROOT / "src" / "build.py"
IMAGES = ROOT / "site" / "assets" / "images"
CLIENTS = IMAGES / "clients"

# 上传限制
ALLOWED_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif")
MAX_BYTES = 12 * 1024 * 1024          # 单张 12MB
PLACEHOLDER_PREFIX = "ph-"            # 灰色占位图前缀


def safe_filename(name):
    """文件名白名单校验，防路径穿越。返回合法文件名或 None。"""
    name = re.sub(r"[\\/]", "", str(name or "")).strip()
    if not name or not re.fullmatch(r"[\w\u4e00-\u9fa9.\-]+", name):
        return None
    if not name.lower().endswith(ALLOWED_EXT):
        return None
    return name


def handle_upload(payload):
    """
    接收 base64 图片，写入正确的图片目录。
    命名规则：已有真实图→覆盖它；当前是占位图→用 slug 生成新名。
    """
    raw_name = safe_filename(payload.get("filename"))
    b64 = payload.get("data") or ""
    if not raw_name:
        return False, "文件名不合法（仅支持 png/jpg/jpeg/webp/gif）", None
    try:
        raw = base64.b64decode(b64)
    except Exception:
        return False, "图片数据解析失败", None
    if not raw:
        return False, "图片内容为空", None
    if len(raw) > MAX_BYTES:
        return False, f"图片超过 {MAX_BYTES // 1024 // 1024}MB，请压缩后再传", None

    path = payload.get("path") or ""
    current = payload.get("current") or ""
    ext = pathlib.Path(raw_name).suffix.lower() or ".png"

    # 已有真实图片 → 直接覆盖，保持文件名稳定
    if (current and not current.startswith(PLACEHOLDER_PREFIX)
            and current.lower().endswith(ALLOWED_EXT)):
        target = current
    else:
        # 占位图 / 空 → 用 slug 生成规范文件名
        slug = (payload.get("slug") or "image").strip() or "image"
        slug = re.sub(r"[^\w\-]", "-", slug)
        target = f"{slug}{ext}"

    # 客户 LOGO 单独存 clients 子目录
    sub = CLIENTS if path.startswith("clients") else IMAGES
    sub.mkdir(parents=True, exist_ok=True)

    # 覆盖前备份原图（用复制，不用移动——万一写入失败，原图仍在，不会丢图）
    dst = sub / target
    if dst.exists():
        bak = BACKUP_DIR / "images"
        bak.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        try:
            shutil.copy2(dst, bak / f"{pathlib.Path(target).stem}-{stamp}{dst.suffix}")
        except Exception:
            pass          # 备份失败不阻断上传

    try:
        dst.write_bytes(raw)
    except PermissionError:
        return False, "图片被占用（可能正被预览或图片查看器打开），请关闭后重试", None
    except Exception as e:
        return False, f"写入失败：{e}", None
    return True, f"已上传：{target}", target


def read_content():
    if not CONTENT_FILE.exists():
        return {}
    return json.loads(CONTENT_FILE.read_text(encoding="utf-8"))


def write_content(data):
    """保存前自动备份，避免改错无法恢复。"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if CONTENT_FILE.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        (BACKUP_DIR / f"content-{stamp}.json").write_text(
            CONTENT_FILE.read_text(encoding="utf-8"), encoding="utf-8"
        )
    CONTENT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                            encoding="utf-8")


def rebuild():
    """调用 build.py 重新生成全站页面。"""
    r = subprocess.run([sys.executable, str(BUILD)],
                       cwd=str(ROOT), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        return False, (r.stderr or r.stdout or "未知错误")[-800:]
    return True, "已重新生成全站页面"


class Handler(BaseHTTPRequestHandler):
    timeout = 60  # 单连接读超时，防止浏览器空连接长期占住线程

    def log_message(self, fmt, *args):
        pass  # 静默访问日志，避免刷屏

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def do_GET(self):
        # 中文文件名的 URL 会被浏览器编码成 %XX 形式，必须解码后才能在文件系统找到
        p = unquote(self.path.split("?")[0])
        if p in ("/", "/index.html", "/admin"):
            html = (ADMIN_DIR / "index.html").read_text(encoding="utf-8")
            self._send(200, html, "text/html; charset=utf-8")
        elif p == "/api/content":
            try:
                self._json(read_content())
            except Exception as e:
                self._json({"ok": False, "msg": f"读取失败：{e}"}, 500)
        elif p == "/api/ping":
            self._json({"ok": True, "root": str(ROOT)})
        elif p == "/api/images":
            def lst(d):
                if not d.exists():
                    return []
                return sorted(f.name for f in d.iterdir()
                              if f.is_file() and f.suffix.lower() in ALLOWED_EXT)
            self._json({"images": lst(IMAGES), "clients": lst(CLIENTS)})
        elif p.startswith("/site/"):
            # 静态预览（后台显示缩略图用），限制在项目目录内
            try:
                f = (ROOT / p.lstrip("/")).resolve()
                if str(f).startswith(str(ROOT.resolve())) and f.is_file():
                    ctype = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
                    self._send(200, f.read_bytes(), ctype)
                else:
                    self._send(404, "Not Found", "text/plain; charset=utf-8")
            except Exception:
                self._send(404, "Not Found", "text/plain; charset=utf-8")
        else:
            self._send(404, "Not Found", "text/plain; charset=utf-8")

    def do_POST(self):
        p = self.path.split("?")[0]
        if p not in ("/api/save", "/api/upload"):
            self._send(404, "Not Found", "text/plain; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8")
            data = json.loads(raw)
        except Exception as e:
            self._json({"ok": False, "msg": f"请求解析失败：{e}"}, 400)
            return

        if p == "/api/upload":
            try:
                ok, msg, fname = handle_upload(data)
                self._json({"ok": ok, "msg": msg, "filename": fname})
            except Exception as e:
                self._json({"ok": False, "msg": f"上传失败：{e}"}, 500)
            return

        try:
            write_content(data)
            ok, msg = rebuild()
            self._json({"ok": ok, "msg": msg})
        except Exception as e:
            self._json({"ok": False, "msg": f"保存失败：{e}"}, 500)


def find_port(start=5000, tries=20):
    import socket
    for port in range(start, start + tries):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return start


def main():
    port = find_port()
    url = f"http://localhost:{port}"
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("=" * 56)
    print("  拓达昇官网 · 内容后台已启动")
    print(f"  访问地址：{url}")
    print("  改完点页面底部「保存并重新生成」即可生效")
    print("  关闭此窗口 = 退出后台")
    print("=" * 56)
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n后台已关闭")
        server.shutdown()


if __name__ == "__main__":
    main()
