"""列出同一个包里全部技能的名字、一句用途和交接说明，给入口安排技能用。

先找 .claude-plugin/marketplace.json 当登记名单；找不到就扫本技能同级目录下带 SKILL.md 的文件夹。
每个技能读 SKILL.md 文件头的 description 和 metadata.ylsd-handoff，打成 JSON。入口自己不列。
"""
import json
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SKILL_DIR = Path(__file__).resolve().parents[1]
ENTRY = "ylsd"


def find_root(start):
    for p in (start, *start.parents):
        if (p / ".claude-plugin" / "marketplace.json").is_file():
            return p
    return None


def frontmatter(text):
    m = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|\Z)", text, re.DOTALL)
    return m.group(1) if m else ""


def field(fm, key):
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", fm, re.M)
    return m.group(1).strip().strip("\"'") if m else ""


def handoff(fm):
    lines = fm.splitlines()
    out = []
    grab = False
    for line in lines:
        if line.strip() == "ylsd-handoff: |":
            grab = True
            continue
        if grab:
            if line.startswith("    "):
                out.append(line.strip())
            elif line.strip():
                break
    return out


def main():
    root = find_root(SKILL_DIR)
    if root is not None:
        mk = json.loads((root / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        names = [p["name"] for p in mk.get("plugins", [])]
        base = root / "skills"
    else:
        base = SKILL_DIR.parent
        names = sorted(p.name for p in base.iterdir() if (p / "SKILL.md").is_file())
    results = []
    for name in names:
        if name == ENTRY:
            continue
        path = base / name / "SKILL.md"
        if not path.is_file():
            print(f"登记了但找不到：{name}", file=sys.stderr)
            continue
        fm = frontmatter(path.read_text(encoding="utf-8"))
        if field(fm, "name") != name:
            print(f"名字对不上，跳过：{path}", file=sys.stderr)
            continue
        results.append({
            "name": name,
            "description": field(fm, "description"),
            "handoff": handoff(fm),
            "path": str(path),
        })
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
