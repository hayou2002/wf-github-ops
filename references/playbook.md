# 本地 Git 整理与 GitHub 上传 · 详细步骤

下面每个步骤都写了命令和判据。命令里的 `<技能目录>` 指这份工作流自己的目录，盘点和体检都用它自带的 `scripts/repo_scan.py`。

## 目录

- 名词速查（不懂就看这里）
- 实际情况（摸底记录）
- 取舍规则（每趟先做这一件事）
- 底座（每趟都走）：盘点 · 定范围与通道 · 上传前体检 · 整理与提交 · 推送 · 验证与记录
- 支线 ① 备份上传
- 支线 ② 首次建库或公开
- 支线 ③ 远端维护
- 支线 ④ 正式发布
- 下一步可以补什么

## 名词速查（不懂就看这里）

- 仓库（repo）：一个项目的档案柜，装着文件和全部历史。
- 副本 / worktree：同一个仓库的另一个工作目录，共享同一份历史。`NewApi管理_repo` 就是这种，不是重复仓库。
- 提交（commit）：把这次的改动打包记一笔，附一句说明。
- 推送（push）：把本地记好的提交送到 GitHub。
- 分支（branch）：同一条线上的平行版本，`main` 是主线。
- 标签（tag）：给某一次提交起个好记的名字，比如 `v1.0`。
- 发布（Release）：在 GitHub 上把一个版本公开出来，写说明、放可下载的文件，一般挂在一个标签上。你要的就是这个。
- 问题（issue）：仓库里的留言板，记待办、报问题。这条流程里不做。
- PR（Pull Request）：把一份改动交出去给人看，通过后才并进主线。这条流程里不做；你明确要走正式发布时，由 git-ship 自己处理。
- 脱敏：把不该公开的内容（服务器地址、账号、客户名、本机目录）改掉或删掉再上传。

## 实际情况（2026-11-13 摸底，只在需要时复看）

- `D:\AI` 下 10 个仓库：三个有远端（`NewApi管理`、`bds-addon-hanhua`、`loomy-keeper`，另有上游克隆 `codex-host-inspect`），其余是本机目录。
- `NewApi管理_repo` **不是重复仓库**，它是主仓库 `NewApi管理` 的 git worktree（分支 `sync-main`），专用于推档案仓：命令是 `git push origin sync-main:main`，只挑脱敏后的改动文件，大二进制和历史目录不进档案仓。删掉它等于拆掉这条通道。
- 档案仓 `hayou2002/newapi-manager-backup`（私有）当前与本地 `sync-main` 一致；本地 `main` 比远端多出若干提交，是「精选推送」设计的正常状态，不是漏推。
- `NewApi管理` 里嵌着两个仓库：`new-api-src-rc50`（上游源码，无远端）和 `projects/loomy-keeper`（有远端）。提交前先确认它们是被 .gitignore 排除还是刻意保留。
- 本机没有 `gh` 命令；凭据走 Windows 凭据管理器（不在文件里）；GitHub 账号 `hayou2002`,token 权限 `gist, repo, workflow`。
- 凭据能取出来用:`printf 'protocol=https\nhost=github.com\n\n' | git credential fill` 返回 `password=`,拿它当 `Authorization: Bearer` 就能调 REST API——建库、改描述、加 topics、发 Release 都不必开浏览器。
- 本机 IPv6 不可用,`curl` 一律加 `-4`,否则会卡住。token 不写进命令行参数,用 `-K -` 从标准输入喂,免得留在进程列表里。

## 取舍规则（每趟先做这一件事）

不把这套流程和八个技能整包带上。每趟动手前：

1. 定支线：备份上传、首次公开、远端维护、正式发布，还是只走底座。
2. 逐条过技能，判「这次用得上吗」。用不上就不读、不写进本次记录，也不要为了走全流程硬凑。
3. 告诉用户结论：这次用哪几个、哪几个不用、为什么。一句话就够。

判断不了的先读那个技能的说明再定，不要先全读完再判断。

| 技能 | 什么情况用 | 什么情况不用 |
| --- | --- | --- |
| oil-explore | 目录陌生，或要判断一堆东西该不该整个传上去 | 这个仓库你天天在改，结构早就清楚 |
| oil-diff | 提交前想看清这轮到底改了什么、有没有夹带 | 改动很小，或你只想直接推 |
| oil-code-review | 这次改动里有代码，且要公开或用在对外的仓库 | 只改文档、只改配置、私人备份仓 |
| oil-govern | 远端维护：分支、worktree、过期文档要体检 | 平时的一次上传 |
| git-ship | 你明确要走分支加 PR 再合并 | 默认的直推 main |
| beautify-github-readme | 仓库要见人，首页需要重做 | 私人备份仓、还没定型的仓库 |
| oil-tone | 要写对外文案：仓库描述、README、Release 说明 | 只推代码、没有对外文字 |
| oil-visual | 首页或文档需要配图 | 不需要配图时一律不用 |

## 底座（每趟都走）

### 步骤 1 · 盘点本机仓库

```bash
py -3 <技能目录>/scripts/repo_scan.py inventory "D:\AI"
```

判据：每个仓库都要看清远端、当前分支、未提交数、未推送数、是 worktree 还是普通目录、有没有套在别的仓库里。

- 「未推送」数字大不等于出问题：档案仓只收精选内容，本地比远端多是设计如此。看到同远端出现多处，先跑 `git -C <路径> worktree list` 确认关系。
- 产出：仓库清单。用户不追问就不留成文件，说清结论即可。

### 步骤 2 · 定范围与通道

```bash
git -C <仓库> worktree list
git -C <仓库> remote -v
git -C <仓库> ls-remote --heads origin
```

判据：同一个远端只留一个正本，worktree 保留不动；嵌套仓库决定是排除还是保留；这次要传的内容范围说清楚再动手。

**这份仓库的脱敏边界**（档案仓 `newapi-manager-backup`，私有）：

- 能进：脱敏后的文档、配置模板、脚本、索引。
- 不能进：任何凭据（token、口令、`.env`）、含本机绝对目录或服务器地址与账号的文件、大二进制、历史归档目录与会话散件 zip。
- 判定：跑步骤 3 的 `audit`，凡命中「含具体用户目录」「含根目录路径」「疑似密钥」的文件，要么改写要么不入库。
- 推送方式：在 worktree 里 `git push origin sync-main:main`，只挑改动到的文件。

### 步骤 3 · 上传前体检

```bash
py -3 <技能目录>/scripts/repo_scan.py audit <仓库路径>
```

判据与处理：

| 命中 | 判据 | 怎么办 |
| --- | --- | --- |
| 凭据类文件被跟踪 | 必须为 0，退出码为 1 就是有 | 先从版本库移除并写进 `.gitignore`，再提交 |
| 超过 5 MB 的已跟踪文件 | 逐个确认 | 私人备份仓可接受；对外仓库考虑移出或改用外部存放 |
| 内容命中密钥或个人目录 | 私人备份仓可接受，对外仓库必须改 | 改写口径或排除该文件 |
| README | 必须有 | 没有就补一个能说清用途的 |
| LICENSE | 对外仓库建议有 | 私人备份仓可跳过 |

### 步骤 4 · 本地整理与提交

```bash
git -C <仓库> status --short
git -C <仓库> diff <文件>
git -C <仓库> add <明确列出的文件>
git -C <仓库> commit -m "<做了什么 + 为什么>"
```

判据：

- 一个主题一条提交，文档、脚本、配置分开；不要 `git add -A` 一把梭。
- 说明沿用仓库现有风格（先看 `git log --oneline -20`），写清做了什么和为什么，不写「更新」「修改」这类空话。
- 如果 diff 显示整个文件都变了（换行符或编码），先停下查原因，不要直接提交。
- 构建产物不靠手动删，交给 `.gitignore`；只有确认没被忽略才动手删。

### 步骤 5 · 推送

```bash
git -C <仓库> pull --ff-only           # 远端有新提交时先同步
git -C <仓库> push origin main         # 普通仓库
git -C <worktree> push origin sync-main:main   # 档案仓走 worktree 通道
```

判据与处理：

- 认证走 Windows 凭据管理器：需要时会弹窗，填 GitHub 账号和一个有 repo 权限的 token，不要用密码。
- 认证失败先看 `git remote -v` 里有没有被写进地址的 token；有就换成干净地址，别把 token 留在配置里。
- 推送前先看这次要推的提交清单（`git log --oneline @{u}..HEAD`），确认没有夹带。
- 必须先问用户再做的动作：强推（`--force`）、覆盖远端历史、改仓库可见性。
- 远端结构性的动作(新建仓库、改描述与 topics、发 Release、删分支与标签)优先用 REST API 做,命令见上面的认证说明与支线 2、3。本机没有 `gh`,不要写 `gh repo create` 这类跑不了的命令。
- 改 README 是本地文件改动,走底座 4 提交推送,不要跑去网页上编辑。
- 需要用户看效果、确认可见性,或 API 报 403/429 时,再开浏览器带用户一起点,不要只丢一段文字让他自己找按钮。

### 步骤 6 · 验证与记录

```bash
git -C <仓库> fetch origin
git -C <仓库> log --oneline -3 origin/main
```

判据：远端确实有你刚推的提交；需要时打开仓库页面看文件和分支。推完必须回头看一次，`push` 没报错不等于远端就是想要的样子。

记录：这次踩到的坑写进 `habits.md`；留下的待办告诉用户。

## 支线 ① · 备份上传

什么时候走：平时的改动要传上去，远端不改结构。

顺序：底座 1 → 2 → 3 → 4 → 5 → 6。档案仓那类仓库在步骤 5 用 worktree 通道。

用到：`oil-diff`（改动不小、想一次看清时）。

不用：门面三个、`oil-code-review`、`oil-govern`、`git-ship`。

产出：远端已同步，并告诉用户推了哪些提交。

## 支线 ② · 首次建库或公开

什么时候走：一个本地目录第一次放上 GitHub，或者要把私人项目变成能见人的项目。

顺序：底座 1 → 2 → 整理（`oil-explore` 摸清结构 → 有代码时 `oil-code-review` 审一遍 → 门面：`beautify-github-readme` 做首页、`oil-tone` 定文案、`oil-visual` 配图）→ 底座 3 → 4 → 5（建库）→ 6。

**公开前必须处理**：内部服务器地址与端口、账号与口令、客户或平台名、本机绝对目录、内部工具名。拿不准的先问用户，不要自己决定。

**公开还是私有**：只给自己备份 → 私有；要给同事或客户看 → 公开，并且 LICENSE 与 README 都要有。

**新建仓库(默认走 REST API)**:

```bash
TOKEN=$(printf 'protocol=https\nhost=github.com\n\n' | git credential fill | sed -n 's/^password=//p')
curl -4 -sS -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" \
  -d '{"name":"<仓库名>","description":"<一句话>","private":false}' \
  https://api.github.com/user/repos
```

1. 请求体里**不要**带 `auto_init`:勾了初始化 README / .gitignore / license 会让首次 `push` 被拒。
2. 可见性按上面第 2 条选;技能与工具类仓库通常公开,只给自己备份的用 `"private": true`。
3. 本地:`git -C <仓库> remote add origin https://github.com/<owner>/<仓库名>.git`;已有 origin 就 `git remote set-url`。
4. `git -C <仓库> push -u origin main`。
5. 门面顺手补齐:`description` 已在建库请求里给;topics 用 `PUT /repos/<owner>/<repo>/topics`,请求体 `{"names":[...]}`。
6. 验证:回读 `/repos/<owner>/<repo>/git/trees/main?recursive=1`,看文件是不是都到了。

API 拿不到权限或被限流时,退回 GitHub 网站:打开 `github.com/new` 建空库(同样不勾初始化),再按上面第 3 步接本地。


8. 验证：刷新仓库页面能看到文件和提交。

## 支线 ③ · 远端维护

什么时候走：不改代码，只想收拾线上仓库。

顺序：`oil-govern` 体检分支、worktree 与过期文档 → 需要时 `beautify-github-readme` + `oil-tone` + `oil-visual` 更新门面 → 发 Release → 底座 6 验证。

只做三件事：仓库描述与 README、分支清理、发 Release。Issue 和 PR 不做。

清理分支前先确认它已经合并进主线（`git branch --merged main`），删远端分支在网站上做，并且必须先问用户。

**版本号规则**：给别人用的项目用 `v1.0.0` 这种（加功能第二位加一，修小问题第三位加一，首个版本 `v1.0.0`）；只做备份、不发功能的仓库用日期式 `v2026.11.13`。标签名和 Release 标题用同一个版本号。

**发 Release(默认走 REST API)**:

```bash
TOKEN=$(printf 'protocol=https\nhost=github.com\n\n' | git credential fill | sed -n 's/^password=//p')
curl -4 -sS -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" \
  -d '{"tag_name":"v0.1.0","name":"v0.1.0","body":"这次改了什么 / 怎么用 / 要注意什么","draft":false,"prerelease":false}' \
  https://api.github.com/repos/<owner>/<repo>/releases
```

1. 版本号按上面的规则定;`tag_name` 和 `name` 用同一个。
2. 说明写三行就够:这次改了什么、怎么用、有没有要注意的。别把 README 全文贴进去。
3. 标签跟着 Release 一起建,不用先手动打 tag。
4. 要挂可下载文件时先建 Release,再往 `upload_url` 传附件;不想折腾就走网站拖拽。
5. 验证:`GET /repos/<owner>/<repo>/releases/latest`,确认版本号与说明都在。

退回网站:仓库页右侧 `Releases` → `Draft a new release`,填版本号 → `Create new tag on publish`。


## 支线 ④ · 正式发布

什么时候走：明确要走分支加 PR 再合并。

顺序：`git-ship` 接管提交与推送，它自己切分支、提 PR、合并回 main；本工作流只在发布前后做体检与验证。

用到：`git-ship`。

不用：其余技能，只有需要改文档时才用门面三个。

提醒：`git-ship` 一调用就是全流程授权（会自动合并到 main），只在用户明确要求正式发布时才走这条。

## 下一步可以补什么

- 哪天愿意装 `gh`，把「新建仓库」和「发 Release」从网页点击改成一条命令（需要用户同意装软件）。
- 让盘点脚本顺手记住上次的仓库清单，下次只报变化。
- 把「脱敏边界」再写成一份自动检查，推送前跑一遍。
