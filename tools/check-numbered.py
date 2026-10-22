"""检查编号目录。

catalog.json：每个编号三位数字、不重复、有 title、purpose、sha256，有 PROMPT.md 且 SHA-256 对得上。
allocation.json：catalog 里的编号都在 issued 里；retired 里的不在 catalog 里；issued 和 retired 不重叠。
PROMPT.md：标题行“# 编号｜标题”，编号跟文件夹一致，六节齐全。
目录里没有登记外的编号文件夹。
"""
import hashlib
import re
import sys
from _common import SKILLS, ENTRY, load_json

DIR = SKILLS / ENTRY / "numbered-prompts"
CODE = re.compile(r"^[0-9]{3}$")
TITLE = re.compile(r"^# ([0-9]{3})｜(.+)$", re.M)
SECTIONS = ("## 用户要完成的事", "## 需要的输入", "## 执行步骤", "## 交付结果", "## 验收标准", "## 适用边界")


def main():
    errors = []
    catalog = load_json(DIR / "catalog.json")
    alloc = load_json(DIR / "allocation.json")
    issued = set(alloc.get("issued", []))
    retired = set(alloc.get("retired", []))
    for c in issued | retired:
        if not CODE.match(c):
            errors.append(f"allocation.json 里编号不是三位数字：{c}")
    if issued & retired:
        errors.append(f"issued 和 retired 重叠：{sorted(issued & retired)}")
    ids = set()
    for it in catalog.get("items", []):
        cid = it.get("id", "")
        if not CODE.match(cid):
            errors.append(f"编号不是三位数字：{cid}")
            continue
        if cid in ids:
            errors.append(f"编号重复：{cid}")
        ids.add(cid)
        if cid not in issued:
            errors.append(f"编号 {cid} 没在 allocation.json 的 issued 里登记")
        if cid in retired:
            errors.append(f"编号 {cid} 已作废还在 catalog 里")
        for k in ("title", "purpose", "sha256"):
            if not it.get(k):
                errors.append(f"编号 {cid} 缺 {k}")
        body = DIR / cid / "PROMPT.md"
        if not body.is_file():
            errors.append(f"编号 {cid} 没有 PROMPT.md")
            continue
        raw = body.read_bytes()
        if hashlib.sha256(raw).hexdigest() != it.get("sha256"):
            errors.append(f"编号 {cid} 的 SHA 对不上")
        text = raw.decode("utf-8")
        m = TITLE.search(text)
        if m is None or m.group(1) != cid:
            errors.append(f"编号 {cid} 的 PROMPT.md 标题行要写“# {cid}｜标题”")
        for s in SECTIONS:
            if s not in text:
                errors.append(f"编号 {cid} 的 PROMPT.md 缺“{s}”")
    for p in DIR.iterdir():
        if p.is_dir() and p.name not in ids:
            errors.append(f"目录里有没登记的编号文件夹：{p.name}")
    for e in errors:
        print("错误", e)
    print(f"编号目录 {len(ids)} 条" + ("，有问题" if errors else "，都对"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
