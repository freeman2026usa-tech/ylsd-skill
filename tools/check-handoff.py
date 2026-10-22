"""检查每个技能文件头的交接字段 metadata.ylsd-handoff。

格式：
metadata:
  ylsd-handoff: |
    - <接手时的状态> → <交出的东西>
    - 不交出：<容易被误以为会做、其实不做的事>

入口技能 ylsd 不要求有交接字段。
"""
import sys
from _common import ENTRY, read_frontmatter, read_handoff, skill_dirs

ARROW = "→"
NOT = "不交出："


def main():
    errors = []
    for d in skill_dirs():
        if d.name == ENTRY:
            continue
        text = (d / "SKILL.md").read_text(encoding="utf-8")
        try:
            fm, _ = read_frontmatter(text)
        except ValueError as e:
            errors.append(f"{d.name}: {e}")
            continue
        lines = read_handoff(fm)
        if not lines:
            errors.append(f"{d.name}: 缺 ylsd-handoff")
            continue
        body = [ln for ln in lines if ln.strip()]
        if not all(ln.startswith("- ") for ln in body):
            errors.append(f"{d.name}: 交接字段每行要以“- ”开头")
        if not body[-1].startswith("- " + NOT):
            errors.append(f"{d.name}: 最后一行要是“- 不交出：…”")
        for ln in body[:-1]:
            if ARROW not in ln:
                errors.append(f"{d.name}: 缺箭头：{ln}")
    for e in errors:
        print("错误", e)
    print("交接字段" + ("有问题" if errors else "都对"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
