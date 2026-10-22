"""几个检查脚本共用的小函数。"""
import json
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
VERSION_FILE = ROOT / "VERSION"
UPDATE_FILE = ROOT / "UPDATE.json"
SHARED = ROOT / "shared"
ENTRY = "ylsd"


def skill_dirs():
    return sorted(p for p in SKILLS.iterdir() if (p / "SKILL.md").is_file())


def read_frontmatter(text):
    """返回 (frontmatter 文本, 正文)。没有合法 frontmatter 时抛 ValueError。"""
    if not text.startswith("---\n"):
        raise ValueError("缺少 frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("frontmatter 没有结束线")
    return text[4:end], text[end + 5:]


def frontmatter_field(fm, key):
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", fm, re.M)
    return m.group(1).strip() if m else None


def read_handoff(fm):
    """读 metadata.ylsd-handoff 块，返回行列表；没有返回 None。"""
    lines = fm.splitlines()
    try:
        i = lines.index("metadata:")
    except ValueError:
        return None
    j = i + 1
    while j < len(lines) and lines[j].startswith("  ") and lines[j].strip() != "ylsd-handoff: |":
        j += 1
    if j >= len(lines) or lines[j].strip() != "ylsd-handoff: |":
        return None
    out = []
    for line in lines[j + 1:]:
        if line.startswith("    "):
            out.append(line[4:])
        elif line.strip() == "":
            continue
        else:
            break
    return out


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def version():
    return VERSION_FILE.read_text(encoding="utf-8").strip()
