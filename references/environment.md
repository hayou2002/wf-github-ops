# wf-github-ops 环境清单

> 由 wf-maker 生成，请勿手改；要改就改 `sources.json` 后重跑 `wf.py env`。

更新时间：2026-11-13

## 技能依赖

| 技能 | 关系 | 来源 | 安装方式 |
| --- | --- | --- | --- |
| beautify-github-readme | 引用 | GitHub oil-oil/beautify-github-readme › skills/beautify-github-readme | npx skills add oil-oil/beautify-github-readme --skill beautify-github-readme |
| git-ship | 引用 | GitHub oil-oil/git-ship | npx skills add oil-oil/git-ship |
| oil-code-review | 引用 | GitHub oil-oil/oil-dev-skills › skills/oil-code-review | npx skills add oil-oil/oil-dev-skills --skill oil-code-review |
| oil-diff | 引用 | GitHub oil-oil/oil-diff | npx skills add oil-oil/oil-diff |
| oil-explore | 引用 | GitHub oil-oil/oil-dev-skills › skills/oil-explore | npx skills add oil-oil/oil-dev-skills --skill oil-explore |
| oil-govern | 引用 | GitHub oil-oil/oil-dev-skills › skills/oil-govern | npx skills add oil-oil/oil-dev-skills --skill oil-govern |
| oil-tone | 引用 | GitHub oil-oil/oil-tone › skills/oil-tone | npx skills add oil-oil/oil-tone --skill oil-tone |
| oil-visual | 引用 | GitHub oil-oil/oil-visual | npx skills add oil-oil/oil-visual |

## 凭据与配置

本清单不记录任何密钥值。需要你自行准备的项目：

- 暂无登记；如果用到了需要密钥的步骤，用 `wf.py link <工作流> <技能> --credentials "需要什么、放在哪"` 补上。

## 恢复步骤

1. 按上表逐项安装或确认技能已就位。
2. 用 `wf.py check <工作流>` 核对每个技能的版本是否和登记时一致。
3. 凭据按「凭据与配置」一节自行准备，不要写进本目录。
