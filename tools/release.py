"""发版：把新版本号和一句收益写进 VERSION、UPDATE.json、marketplace.json、入口 SKILL.md 的 YLSD_LOCAL_VERSION。

用法：python tools/release.py 0.2.0 "这版给你什么，80 字以内"
"""
import json
import re
import sys
from _common import ENTRY, MARKETPLACE, SKILLS, UPDATE_FILE, VERSION_FILE, load_json

PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
LOCAL_VERSION = re.compile(r'(YLSD_LOCAL_VERSION=")(\d+\.\d+\.\d+)(")')


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv):
    if len(argv) != 2 or not PATTERN.match(argv[0]):
        print(__doc__)
        return 2
    v, notice = argv
    if not (1 <= len(notice) <= 80) or any(c in notice for c in "\r\n\t"):
        print("收益那句要 1 到 80 字，不换行")
        return 2
    VERSION_FILE.write_text(v + "\n", encoding="utf-8")
    upd = load_json(UPDATE_FILE)
    upd["version"] = v
    upd["notice"] = notice
    dump(UPDATE_FILE, upd)
    mk = load_json(MARKETPLACE)
    mk.setdefault("metadata", {})["version"] = v
    for p in mk.get("plugins", []):
        p["version"] = v
    dump(MARKETPLACE, mk)
    entry = SKILLS / ENTRY / "SKILL.md"
    text, n = LOCAL_VERSION.subn(rf"\g<1>{v}\g<3>", entry.read_text(encoding="utf-8"))
    if n != 1:
        print("入口 SKILL.md 里找不到唯一的 YLSD_LOCAL_VERSION，没写")
        return 1
    entry.write_text(text, encoding="utf-8")
    print(f"已写 {v}：VERSION、UPDATE.json、marketplace.json、入口 SKILL.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
