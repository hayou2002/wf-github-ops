# wf-github-ops

本地 Git 仓库的整理与上传工作流:先看清现场,再决定传什么,上传前体检,传完把远端也收拾干净。

给「只会用 GitHub 下载东西、存自己的东西」的人写的。命令都给全了,不需要先学 Git。

## 它会做什么

**底座(每趟都走)**:盘点 → 定范围 → 体检 → 提交 → 推送 → 验证

**支线(选一条)**:

| 支线 | 什么时候走 | 产出 |
| --- | --- | --- |
| 1 备份上传 | 平时的改动要传上去(默认) | 远端已同步 |
| 2 首次建库或公开 | 第一次把项目放上 GitHub | 一个能见人的仓库 |
| 3 远端维护 | 只想收拾线上仓库 | 远端状态清单 |
| 4 正式发布 | 走分支加 PR 再合并 | 合并进 main |

## 红线

- 凭据不进库:`.env`、密钥、令牌一律排除,只留示例文件。
- 破坏性操作先问:删仓库、强推、清分支、改远端设置。
- 传完要回读:远端真看到了什么,才算传完。

## 自带工具

```bash
py -3 scripts/repo_scan.py inventory <目录>   # 盘本机仓库:分支、未提交、未推送、worktree
py -3 scripts/repo_scan.py audit <目录>       # 体检:凭据文件、超大文件、内容里的密钥与本机路径
```

`audit` 退出码为 1,说明有该拦的东西被跟踪了,先处理再提交。

## 安装

```bash
npx skills add hayou2002/wf-github-ops
```

## 依赖

按支线按需挂:`oil-explore`、`oil-code-review`、`oil-diff`、`oil-govern`、`beautify-github-readme`、`oil-tone`、`oil-visual`、`git-ship`。不装也能走底座,只是少几个帮手。

## 同系列

- [wf-maker](https://github.com/hayou2002/wf-maker):把流程做成工作流 Skill
- [wf-design](https://github.com/hayou2002/wf-design):网页、演示、图片、正式文件
- [wf-vibecode](https://github.com/hayou2002/wf-vibecode):日常 Vibe Coding

## 许可

MIT
