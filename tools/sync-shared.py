"""把 shared/references/ 里的共享文件复制成各技能自己的副本。

多个技能共用的文件只在 shared/references/ 维护一份；shared/manifest.json 登记每份复制到哪些技能。
装了以后每个技能只有自己的目录，运行时读的是 skills/<name>/references/<文件> 这份副本。
默认执行复制；加 --check 只比对副本和真源是否一致，不写入。
"""
import shutil
import sys
from _common import SHARED, SKILLS, load_json

SRC = SHARED / "references"


def main(argv):
    check = "--check" in argv
    manifest = load_json(SHARED / "manifest.json")
    errors = []
    for fname, targets in manifest.items():
        src = SRC / fname
        if not src.is_file():
            errors.append(f"真源不存在：{fname}")
            continue
        for skill in targets:
            dst = SKILLS / skill / "references" / fname
            if check:
                if not dst.is_file():
                    errors.append(f"{skill} 缺副本 {fname}")
                elif dst.read_bytes() != src.read_bytes():
                    errors.append(f"{skill} 的 {fname} 跟真源不一致")
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
                print(f"已复制 {fname} 到 {skill}")
    for e in errors:
        print("错误", e)
    if check:
        print("共享副本" + ("有问题" if errors else "都一致"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
