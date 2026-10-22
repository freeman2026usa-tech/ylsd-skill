"""检查全部 .md 的用词：港台标点、退休词、公文词。

标点和退休词的表来自引力锁定产品的界面文字守卫，公文词表是本仓库自己的。
交接字段里的箭头是格式的一部分，不算。
"""
import re
import sys
from _common import ROOT

PUNCT = {
    "「": "引号用 “”",
    "」": "引号用 “”",
    "『": "引号用 ‘’",
    "』": "引号用 ‘’",
    "＋": "连词写“和”",
    "　": "全角空格改半角",
    "–": "范围写“3 到 5”",
    "←": "不用箭头",
}
RETIRED = {
    "客户经理": "没有这个角色",
    "其它": "其他",
}
BUREAU = ["方可", "务必", "请勿", "尚未具备", "即可执行", "以保障", "予以", "进行"]
SKIP_DIRS = {".git", "node_modules", "dist"}


def md_files():
    for p in ROOT.rglob("*.md"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        yield p


def main():
    errors = []
    for p in md_files():
        rel = p.relative_to(ROOT)
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for ch, fix in PUNCT.items():
                if ch in line:
                    errors.append(f"{rel}:{n} 标点“{ch}”：{fix}")
            if "→" in line and not line.lstrip().startswith("- ") and "handoff" not in line:
                errors.append(f"{rel}:{n} 句中箭头，改成话")
            for w, fix in RETIRED.items():
                if w in line:
                    errors.append(f"{rel}:{n} 退休词“{w}”：{fix}")
            for w in BUREAU:
                if w in line and not re.search(rf"[“\"]{w}[”\"]", line):
                    errors.append(f"{rel}:{n} 公文词“{w}”")
    for e in errors:
        print("错误", e)
    print("用词" + ("有问题" if errors else "都过"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
