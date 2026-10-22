"""检查 VERSION、UPDATE.json、marketplace.json、入口 SKILL.md 里的版本号一致，plugin.json 和 marketplace.json 登记的技能对得上。"""
import re
import sys
from _common import ENTRY, MARKETPLACE, PLUGIN, SKILLS, UPDATE_FILE, load_json, skill_dirs, version

PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
LOCAL_VERSION = re.compile(r'YLSD_LOCAL_VERSION="(\d+\.\d+\.\d+)"')


def main():
    errors = []
    v = version()
    if not PATTERN.match(v):
        errors.append(f"VERSION 不是三段数字：{v}")
    entry = (SKILLS / ENTRY / "SKILL.md").read_text(encoding="utf-8")
    found = LOCAL_VERSION.findall(entry)
    if len(found) != 1:
        errors.append("入口 SKILL.md 里要有且只有一处 YLSD_LOCAL_VERSION")
    elif found[0] != v:
        errors.append(f"入口 SKILL.md 的 YLSD_LOCAL_VERSION {found[0]} 跟 VERSION {v} 不一致")
    upd = load_json(UPDATE_FILE)
    if upd.get("version") != v:
        errors.append(f"UPDATE.json 版本 {upd.get('version')} 跟 VERSION {v} 不一致")
    notice = upd.get("notice", "")
    if not (1 <= len(notice) <= 80) or any(c in notice for c in "\r\n\t"):
        errors.append("UPDATE.json 的 notice 要一句话、80 字以内、不换行")
    mk = load_json(MARKETPLACE)
    if mk.get("metadata", {}).get("version") != v:
        errors.append("marketplace.json 的 metadata.version 跟 VERSION 不一致")
    mk_names = set()
    for p in mk.get("plugins", []):
        mk_names.add(p["name"])
        if p.get("version") != v:
            errors.append(f"marketplace.json 里 {p['name']} 的版本跟 VERSION 不一致")
    pl = load_json(PLUGIN)
    pl_names = {s.rsplit("/", 1)[-1] for s in pl.get("skills", [])}
    disk = {d.name for d in skill_dirs()}
    if pl_names != disk:
        errors.append(f"plugin.json 登记的技能 {sorted(pl_names)} 跟目录 {sorted(disk)} 不一致")
    if mk_names != disk:
        errors.append(f"marketplace.json 登记的技能 {sorted(mk_names)} 跟目录 {sorted(disk)} 不一致")
    for e in errors:
        print("错误", e)
    print("版本和登记" + ("有问题" if errors else "都对"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
