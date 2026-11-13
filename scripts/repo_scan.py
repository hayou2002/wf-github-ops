#!/usr/bin/env python3
"""本地仓库盘点与上传前体检。只用 Python 3 标准库，不联网。"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "dist", ".idea"}
MAX_DEPTH = 3
BIG_FILE_BYTES = 5 * 1024 * 1024
SCAN_MAX_BYTES = 256 * 1024

CREDENTIAL_FILES = {
    ".env",
    ".git-credentials",
    ".htpasswd",
    ".netrc",
    ".npmrc",
    ".pypirc",
    "credentials.json",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
    "secrets.json",
    "service-account.json",
}
CREDENTIAL_SUFFIXES = {".jks", ".key", ".keystore", ".p12", ".pem", ".pfx", ".ppk"}
CREDENTIAL_EXEMPT = ("example", "sample", "template")

TEXT_SUFFIXES = {
    ".cfg", ".conf", ".css", ".csv", ".env", ".htm", ".html", ".ini", ".js", ".json",
    ".md", ".ps1", ".py", ".sh", ".sql", ".toml", ".ts", ".txt", ".yaml", ".yml",
}

# 这几个模式要避开字面量，否则本文件自己就会被扫出「含个人目录」。
_USERS_WIN = re.compile(
    r"[A-Za-z]:[\\/]+Use" r"rs[\\/]+"
    r"(?!(?:Public|Default(?: User)?|All Users)(?:[\\/]+|$))"
    r"[A-Za-z0-9._ -]+[\\/]+",
    re.IGNORECASE,
)
_USERS_MAC = re.compile("/Use" "rs/(?!Shared(?:/|$))[A-Za-z0-9._-]+/")
_HOME_LINUX = re.compile("/ho" "me/[A-Za-z0-9._-]+/")
_ROOT_LINUX = re.compile("/ro" "ot/")

SECRET_PATTERNS = (
    ("疑似 API Key", re.compile(r"\bsk-[A-Za-z0-9_-]{24,}\b")),
    ("疑似 GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("疑似云厂商密钥", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("疑似私钥块", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    (
        "疑似明文口令赋值",
        re.compile(
            r"(?im)(?:^|\n)[ \t]*(?:export[ \t]+)?[\"']?"
            r"(?:[A-Za-z0-9]+[_-])*(?:password|passwd|secret|token|api[_-]?key)"
            r"[\"']?[ \t]*[:=][ \t]*[\"']?[A-Za-z0-9_./+=:@-]{16,}",
        ),
    ),
)


def run_git(repo: Path, *args: str) -> tuple[int, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            errors="replace",
        )
    except OSError as exc:
        return 1, str(exc)
    return result.returncode, result.stdout.strip()


def git_root(path: Path) -> Path | None:
    if (path / ".git").exists():
        return path
    return None


def find_repos(roots: list[Path]) -> list[Path]:
    found: list[Path] = []
    for root in roots:
        for current, dirs, _ in os.walk(root):
            here = Path(current)
            depth = len(here.parts) - len(root.parts)
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            if depth >= MAX_DEPTH:
                dirs[:] = []
            if git_root(here):
                found.append(here)
    return sorted(set(found), key=lambda item: str(item).lower())


def describe(repo: Path) -> dict:
    git_dir = repo / ".git"
    worktree = git_dir.is_file()
    info: dict = {"path": str(repo), "worktree": worktree}
    if worktree:
        try:
            text = git_dir.read_text(encoding="utf-8", errors="replace").strip()
            info["gitdir"] = text.replace("gitdir:", "").strip()
        except OSError:
            info["gitdir"] = ""
    code, remote = run_git(repo, "remote", "get-url", "origin")
    info["remote"] = remote if code == 0 else ""
    code, branch = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    info["branch"] = branch if code == 0 else "?"
    code, status = run_git(repo, "status", "--porcelain")
    info["dirty"] = len(status.splitlines()) if code == 0 and status else 0
    code, ahead = run_git(repo, "rev-list", "--count", "@{u}..HEAD")
    info["ahead"] = int(ahead) if code == 0 and ahead.isdigit() else -1
    code, last = run_git(repo, "log", "-1", "--format=%ad %s", "--date=short")
    info["last"] = last if code == 0 else ""
    return info


def cmd_inventory(args) -> int:
    roots = [Path(item).expanduser().resolve() for item in (args.paths or [str(Path.cwd())])]
    missing = [str(root) for root in roots if not root.is_dir()]
    if missing:
        raise SystemExit("这些目录不存在：" + "、".join(missing))
    repos = find_repos(roots)
    rows = [describe(repo) for repo in repos]
    known = {str(repo) for repo in repos}
    for row in rows:
        parents = Path(row["path"]).parents
        row["nested"] = any(str(parent) in known for parent in parents)
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    if not rows:
        print("这些目录下没有找到 git 仓库：" + "、".join(str(root) for root in roots))
        return 0
    width = max(len(row["path"]) for row in rows)
    for row in rows:
        kind = "worktree" if row["worktree"] else "仓库"
        if row["nested"]:
            kind += "/嵌套"
        ahead = "未推送未知" if row["ahead"] < 0 else f"未推送 {row['ahead']}"
        print(f"{row['path']:<{width}}  {kind:<8} {row['branch']:<12} 未提交 {row['dirty']:<3} {ahead}")
        print(f"{'':<{width}}  远端 {row['remote'] or '（没有远端）'}")
        if row["last"]:
            print(f"{'':<{width}}  最近 {row['last']}")
    duplicates: dict[str, list[str]] = {}
    for row in rows:
        if row["remote"]:
            duplicates.setdefault(row["remote"], []).append(row["path"])
    shared = {url: paths for url, paths in duplicates.items() if len(paths) > 1}
    print(f"\n共 {len(rows)} 个仓库。")
    if shared:
        print("同一个远端出现在多处，先确认哪个是正本、哪些是 worktree：")
        for url, paths in shared.items():
            print(f"  {url}")
            for item in paths:
                print(f"    {item}")
    nested = [row["path"] for row in rows if row["nested"]]
    if nested:
        print("有仓库套在另一个仓库里面，提交前先确认是刻意保留还是该排除：")
        for item in nested:
            print(f"  {item}")
    return 0


def tracked_files(repo: Path) -> list[str]:
    code, out = run_git(repo, "ls-files")
    if code != 0 or not out:
        return []
    return [line for line in out.splitlines() if line.strip()]


def looks_like_credential(rel: str) -> bool:
    path = Path(rel)
    name = path.name.lower()
    if name.startswith(".env"):
        return not any(marker in name for marker in CREDENTIAL_EXEMPT)
    if name in CREDENTIAL_FILES:
        return True
    return path.suffix.lower() in CREDENTIAL_SUFFIXES


def scan_content(repo: Path, rel: str) -> list[str]:
    path = repo / rel
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return []
    try:
        if path.stat().st_size > SCAN_MAX_BYTES:
            return []
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    hits: list[str] = []
    for label, pattern in SECRET_PATTERNS:
        if pattern.search(text):
            hits.append(label)
    for label, pattern in (
        ("含具体用户目录", _USERS_WIN),
        ("含具体用户目录", _USERS_MAC),
        ("含具体用户目录", _HOME_LINUX),
        ("含根目录路径", _ROOT_LINUX),
    ):
        if pattern.search(text):
            hits.append(label)
    return sorted(set(hits))


def cmd_audit(args) -> int:
    repo = Path(args.repo).expanduser().resolve()
    if not git_root(repo):
        raise SystemExit(f"{repo} 不是 git 仓库根目录。")
    files = tracked_files(repo)
    credentials = [rel for rel in files if looks_like_credential(rel)]
    big: list[tuple[str, int]] = []
    for rel in files:
        path = repo / rel
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > BIG_FILE_BYTES:
            big.append((rel, size))
    content_hits: dict[str, list[str]] = {}
    for rel in files:
        hits = scan_content(repo, rel)
        if hits:
            content_hits[rel] = hits
    report = {
        "repo": str(repo),
        "tracked_files": len(files),
        "has_gitignore": (repo / ".gitignore").is_file(),
        "has_readme": any(rel.lower().startswith("readme") for rel in files),
        "has_license": any(Path(rel).name.lower().startswith("license") for rel in files),
        "credentials": credentials,
        "big_files": big,
        "content_hits": content_hits,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1 if credentials else 0
    print(f"{repo}")
    print(f"  已跟踪文件 {len(files)} 个；.gitignore {'有' if report['has_gitignore'] else '没有'}"
          f"；README {'有' if report['has_readme'] else '没有'}"
          f"；LICENSE {'有' if report['has_license'] else '没有'}")
    if credentials:
        print("  [必须处理] 这些凭据类文件正在被跟踪，推上去就等于公开：")
        for rel in credentials:
            print(f"    {rel}")
    else:
        print("  凭据类文件：没有")
    if big:
        print(f"  [要看一眼] 超过 {BIG_FILE_BYTES // (1024 * 1024)} MB 的已跟踪文件：")
        for rel, size in sorted(big, key=lambda item: -item[1]):
            print(f"    {size / (1024 * 1024):.1f} MB  {rel}")
    if content_hits:
        print("  [要看一眼] 文件内容里可能有敏感信息或个人目录：")
        for rel, hits in sorted(content_hits.items())[:20]:
            print(f"    {rel}  ({'、'.join(hits)})")
        if len(content_hits) > 20:
            print(f"    还有 {len(content_hits) - 20} 个文件，加 --json 看全")
    else:
        print("  文件内容：没有扫到疑似密钥或个人目录")
    print("  结论：" + ("先处理上面的凭据文件再提交。" if credentials else "可以进入提交环节。"))
    return 1 if credentials else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="repo_scan.py", description="本地仓库盘点与上传前体检")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    sub = parser.add_subparsers(dest="command", required=True)
    inventory = sub.add_parser("inventory", help="盘点目录下的 git 仓库")
    inventory.add_argument("paths", nargs="*", help="要扫的目录，默认是当前目录")
    inventory.set_defaults(func=cmd_inventory)
    audit = sub.add_parser("audit", help="上传前体检一个仓库")
    audit.add_argument("repo", help="仓库根目录")
    audit.set_defaults(func=cmd_audit)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
