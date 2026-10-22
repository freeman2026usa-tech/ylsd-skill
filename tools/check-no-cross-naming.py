"""检查技能之间不互相提名字。

- 叶子技能的正文和 references 里不许出现别的技能名；结尾固定句必须有“不提别的技能的名字”和“可以输入 /ylsd”。
- 入口 ylsd 只许在“## 相近技能怎么分”那一节写技能名；ylsd-update 是工具依赖，入口哪里都能提。
"""
import re
import sys
from _common import ENTRY, read_frontmatter, skill_dirs

TOOL_DEPS = {"ylsd-update"}
NEIGHBOR_SECTION = "## 相近技能怎么分"
TRAILER_MARKS = ("不提别的技能的名字", "可以输入 /ylsd")


def mentions(text, names):
    return [n for n in names if re.search(rf"(?<![\w-]){re.escape(n)}(?![\w-])", text)]


def main():
    dirs = skill_dirs()
    names = [d.name for d in dirs]
    leaf_names = [n for n in names if n != ENTRY]
    errors = []
    for d in dirs:
        text = (d / "SKILL.md").read_text(encoding="utf-8")
        _, body = read_frontmatter(text)
        if d.name == ENTRY:
            if NEIGHBOR_SECTION not in body:
                errors.append(f"{ENTRY} 缺“{NEIGHBOR_SECTION}”一节")
                continue
            head, _, rest = body.partition(NEIGHBOR_SECTION)
            after = re.split(r"^## ", rest, maxsplit=1, flags=re.M)
            outside = head + ("\n## " + after[1] if len(after) > 1 else "")
            for n in mentions(outside, [x for x in leaf_names if x not in TOOL_DEPS]):
                errors.append(f"{ENTRY} 在相近技能那一节之外提了 {n}")
            continue
        for mark in TRAILER_MARKS:
            if mark not in body:
                errors.append(f"{d.name} 结尾固定句缺“{mark}”")
        others = [n for n in leaf_names if n != d.name]
        for n in mentions(body, others):
            errors.append(f"{d.name} 正文提了 {n}")
        for ref in sorted((d / "references").glob("*.md")) if (d / "references").is_dir() else []:
            for n in mentions(ref.read_text(encoding="utf-8"), others):
                errors.append(f"{d.name}/references/{ref.name} 提了 {n}")
    for e in errors:
        print("错误", e)
    print("互相点名" + ("有问题" if errors else "没有"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
