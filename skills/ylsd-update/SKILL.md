---
name: ylsd-update
description: 更新 ylsd-skill 到最新版。用户说“更新 ylsd”“升级”“检查版本”，或在更新提醒后回“1”时用。只更新这一个包，不动别的技能，不动用户自己改过的文件。
metadata:
  ylsd-handoff: |
    - 用户说更新，或紧接着更新提醒回“1” → 按装法更新到最新版，记下更新时间，告诉他新开一个对话
    - 用户只问有没有新版、新版改了什么 → 读仓库的 UPDATE.json 回答，不动手
    - 不交出：更新别的技能、删他自己改过的文件、后台定时任务
---

# ylsd-update 更新

1. 用户明确要更新，或在上一条回复的版本提醒后回了“1”，直接更新，不再问一遍。

2. 只有上一条回复里确实有版本提醒，单独的“1”才算更新。

3. 没有这段上下文，不要自己解释数字的意思。

## 范围

- 只更新 ylsd-skill 这一个包。
- 不碰用户装的别的技能。
- 用户自己改过的文件一律留着，不覆盖。
- 不建后台任务、定时任务。

## 怎么做

1. 先判断是怎么装的。

   两种可能，只更新查到的那种；两种都查到时，按插件装的更新：

   - Claude Code 插件装的：本 SKILL.md 的路径里有 /.claude/plugins/，或 `claude plugin list` 里有以 @ylsd-skill 结尾的插件。
   - 手工下载装的：本 SKILL.md 在某个 skills 目录下，路径里没有 /.claude/plugins/。

2. 插件装的，运行：

   ```bash
   claude plugin marketplace update ylsd-skill
   claude plugin update ylsd@ylsd-skill
   ```

3. 手工下载装的：到 GitHub 或 Gitee 搜 ylsd-skill，重新下载，把新文件覆盖到原来的文件夹；他自己改过的那几份不覆盖，覆盖前问他改过哪些。
   - 原来的文件夹就是本 SKILL.md 所在目录往上两级。
   - AI 软件没法替他下载的，把这句话原样告诉他，让他自己下、自己覆盖。

4. 版本有变才记时间。

   更新成功后记下时间。这样当前对话还在用旧版时，不会反复提醒：

   ```bash
   python -c "import time,pathlib;p=pathlib.Path.home()/'.ylsd';p.mkdir(exist_ok=True);(p/'update_check_at').write_text(str(int(time.time())))"
   ```

5. 按命令结果说明有没有完成。

   完成了，就提醒他新开一个对话再用。

6. 没完成时：
   - 一句话说原因和他要处理的事（权限、网络）。
   - 不贴整段终端输出。

## 回复

成功：

> ylsd-skill 已更新完成（怎么装的就写哪种）。新开一个对话再用。

失败：

> ylsd-skill 没更新完成：原因一句。处理完再说一次“更新 ylsd”。

本来就是最新版：

> ylsd-skill 已经是最新版（版本号照命令结果写），不用更新。

## 边界

- 用户只问版本、新版改了什么、要不要更新：先回答，不动手。
- 不用 `npx skills update`，它会把用户装的别的技能一起更新。

完成当前任务后直接结束。

遇到以下情况时：
- 用户问的超出本技能范围。
- 材料里明摆着有后续需求。
- 用户问下一步。

说一句还缺哪种能力，不提别的技能的名字。
补一句“可以输入 /ylsd，它来匹配”。
