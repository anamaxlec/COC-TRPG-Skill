#!/usr/bin/env python3
"""Explicit GitHub backup of v2 saves; Git stores history and sync ancestry."""
import argparse
import os
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

import memory


BRANCH = "coc-saves"
REMOTE_REF = "refs/remotes/origin/" + BRANCH


def git(repo, *args, check=True):
    env = os.environ.copy()
    env.update(GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    try:
        result = subprocess.run(
            ["git", "-c", "core.autocrlf=false", *args], cwd=repo,
            env=env, text=True, encoding="utf-8", capture_output=True, timeout=45,
        )
    except FileNotFoundError:
        raise SystemExit("需要安装 Git；本地记忆未改变。")
    except subprocess.TimeoutExpired:
        raise SystemExit("Git 操作超时；本地记忆保留。请检查网络后重试。")
    if check and result.returncode:
        raise SystemExit(f"Git 操作失败（{args[0]}）: {(result.stderr or result.stdout).strip()}\n本地记忆保留；不会强制推送或自动合并存档。")
    return result


def github_url(repo, transport="https"):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+", repo):
        raise SystemExit("--repo 请使用 GitHub 的 用户名/仓库名，不要填写 URL 或 Token。")
    if repo.split("/")[1] in {".", ".."}:
        raise SystemExit("仓库名无效。")
    return f"git@github.com:{repo}.git" if transport == "ssh" else f"https://github.com/{repo}.git"


def configure(data_dir, url):
    cache = Path(data_dir) / "github-cache"
    if cache.exists():
        if not (cache / ".git").is_dir():
            raise SystemExit(f"目录已存在且不是存档仓库: {cache}")
        old = git(cache, "remote", "get-url", "origin").stdout.strip()
        if old != url:
            raise SystemExit("此数据目录已配置其他仓库。请使用另一个 --data-dir，避免混用团档。")
        return cache
    cache.mkdir(parents=True)
    git(cache, "init", "--quiet")
    git(cache, "symbolic-ref", "HEAD", f"refs/heads/{BRANCH}")
    git(cache, "remote", "add", "origin", url)
    return cache


def repository(data_dir):
    cache = Path(data_dir) / "github-cache"
    if not (cache / ".git").is_dir():
        raise SystemExit("尚未配置 GitHub 存档。先运行 init --repo 用户名/仓库名。")
    if git(cache, "symbolic-ref", "--short", "HEAD").stdout.strip() != BRANCH:
        raise SystemExit(f"存档缓存不在 {BRANCH} 分支；请先检查缓存仓库。")
    return cache


def revision(cache, ref):
    result = git(cache, "rev-parse", "--verify", ref, check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def fetch_remote(cache):
    listed = git(cache, "ls-remote", "--heads", "origin", f"refs/heads/{BRANCH}").stdout
    if not listed.strip():
        return None
    git(cache, "fetch", "--quiet", "--no-tags", "origin", f"refs/heads/{BRANCH}:{REMOTE_REF}")
    return revision(cache, REMOTE_REF)


def save_relative_path(name):
    return f"saves/{memory.slugify(name)}.cocsave.json"


def campaign_ref(name):
    return f"refs/coc-campaigns/{memory.slugify(name)}"


def blob(cache, ref, path):
    if not ref:
        return None
    entry = git(cache, "ls-tree", ref, "--", path).stdout
    if not entry:
        return None
    if entry.split()[0] != "100644":
        raise SystemExit("云端存档必须是普通 JSON 文件，不能是链接或可执行文件。")
    return git(cache, "show", f"{ref}:{path}").stdout


def require_clean(cache):
    if git(cache, "status", "--porcelain").stdout.strip():
        raise SystemExit(f"存档缓存有未提交改动，请先检查: {cache}。不会清理或覆盖这些文件。")


def advance(cache, remote):
    require_clean(cache)
    if remote:
        if revision(cache, "HEAD"):
            git(cache, "merge", "--ff-only", "--no-edit", remote)
        else:
            git(cache, "checkout", "--quiet", "-B", BRANCH, remote)


def push(data_dir, name, include_keeper=False):
    if not include_keeper:
        raise SystemExit("完整存档包含 Keeper 秘密与全部剧情。确认目标及公开范围后，加 --include-keeper 上传。公开 fork 的所有分支都公开。")
    cache = repository(data_dir)
    require_clean(cache)
    path = save_relative_path(name)
    # Keep writers out while preparing the exact state being uploaded.
    with memory.MemoryLock(data_dir, name):
        current = memory.load_memory(data_dir, name)
        if current["meta"]["campaign"] != name:
            raise SystemExit("团名对应的文件名与另一个团冲突；请先为团档改名。")
        remote = fetch_remote(cache)
        base = revision(cache, campaign_ref(name))
        remote_save = blob(cache, remote, path)
        base_save = blob(cache, base, path)
        if remote_save != base_save:
            raise SystemExit("云端同团存档已变化，或本机从未同步过该团。先下载检查；需要保留两条剧情时，将本地存档导入为另一个团名。没有上传。")
        head = revision(cache, "HEAD")
        if head:
            pending = (git(cache, "-c", "core.quotePath=false", "diff", "--name-only", remote, head).stdout
                       if remote else git(cache, "-c", "core.quotePath=false", "ls-tree", "-r", "--name-only", head).stdout)
            if any(p != path for p in pending.splitlines()):
                # Remote-only changes are safe to fast-forward; local outgoing changes are not.
                if not remote or git(cache, "merge-base", "--is-ancestor", head, remote, check=False).returncode:
                    raise SystemExit("缓存还有其他团档的未上传变更，请先处理原团，避免顺带上传。")
        advance(cache, remote)
        git(cache, "var", "GIT_AUTHOR_IDENT")
        git(cache, "var", "GIT_COMMITTER_IDENT")
        if (cache / "saves").is_symlink():
            raise SystemExit("存档目录不能是符号链接。")
        memory.refresh_summaries(current)
        memory.write_save_file(cache, current, path, force=True)
        git(cache, "add", "--", path)
        diff = git(cache, "diff", "--cached", "--quiet", "--", path, check=False)
        if diff.returncode == 1:
            git(cache, "commit", "--quiet", "--only", "-m", f"Save campaign: {name}", "--", path)
        elif diff.returncode:
            raise SystemExit(f"无法检查待上传改动: {diff.stderr.strip()}")
        # An ordinary push rejects a remote race; never force-push or auto-resolve JSON.
        git(cache, "push", "origin", f"HEAD:refs/heads/{BRANCH}")
        head = revision(cache, "HEAD")
        git(cache, "update-ref", campaign_ref(name), head)
    return path, head


def decode_save(data_dir, content):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "download.cocsave.json"
        path.write_text(content, encoding="utf-8")
        try:
            loaded, _ = memory.read_save_file(data_dir, str(path))
        except (ValueError, TypeError, AttributeError, KeyError) as exc:
            raise SystemExit(f"云端存档结构无效: {exc}")
    return loaded


def pull(data_dir, name, replace_local=False):
    cache = repository(data_dir)
    require_clean(cache)
    remote = fetch_remote(cache)
    content = blob(cache, remote, save_relative_path(name))
    if content is None:
        raise SystemExit(f"云端 {BRANCH} 分支没有这个团的存档。")
    incoming = decode_save(data_dir, content)
    if incoming["meta"]["campaign"] != name:
        raise SystemExit("云端文件的实际团名不匹配；没有导入。")
    head = revision(cache, "HEAD")
    if head and git(cache, "merge-base", "--is-ancestor", head, remote, check=False).returncode:
        raise SystemExit("缓存中有未上传或分歧的提交，先检查并保留这些进度；没有覆盖本地记忆。")
    with memory.MemoryLock(data_dir, name):
        target, _ = memory.memory_paths(data_dir, name)
        if target.exists() and not replace_local:
            raise SystemExit("本地已有同名团档。确认用云端替换后加 --replace-local；替换前会自动备份。")
        advance(cache, remote)
        backup = None
        if target.exists():
            current = memory.load_memory(data_dir, name)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            backup, _ = memory.write_save_file(data_dir, current, f"saves/{memory.slugify(name)}_before_github_{stamp}.cocsave.json")
        memory.save_memory(data_dir, incoming, preserve_summaries=True)
        git(cache, "update-ref", campaign_ref(name), remote)
    return backup


def list_cloud(data_dir):
    cache = repository(data_dir)
    remote = fetch_remote(cache)
    if not remote:
        return []
    paths = git(cache, "-c", "core.quotePath=false", "ls-tree", "-r", "--name-only", remote, "--", "saves/").stdout
    return [p for p in paths.splitlines() if p.endswith(".cocsave.json")]


def main():
    parser = argparse.ArgumentParser(description="GitHub 团档：独立 coc-saves 分支，显式上传/下载")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "status", "list", "push", "pull"):
        p = sub.add_parser(command)
        p.add_argument("--data-dir", default="", help="与 memory.py 使用同一个数据目录")
        if command == "init":
            p.add_argument("--repo", required=True, help="独立私有存档库或自己的 fork：用户名/仓库名")
            p.add_argument("--transport", choices=("https", "ssh"), default="https")
        if command in ("push", "pull"):
            p.add_argument("--name", required=True)
        if command == "push":
            p.add_argument("--include-keeper", action="store_true", help="确认上传包含 Keeper 秘密的完整存档")
        if command == "pull":
            p.add_argument("--replace-local", action="store_true", help="备份后用云端替换本地同名团档")
    args = parser.parse_args()
    data_dir = memory.resolve_data_dir(args)
    with memory.MemoryLock(data_dir, "_github_sync"):
        if args.command == "init":
            cache = configure(data_dir, github_url(args.repo, args.transport))
            print(f"已配置: {args.repo} / {BRANCH}\n缓存: {cache}\n仅配置本地，尚未上传。公开 fork 的团档也会公开；私密团请指定独立私有库。")
        elif args.command == "status":
            cache = repository(data_dir)
            print(f"目标: {git(cache, 'remote', 'get-url', 'origin').stdout.strip()}\n分支: {BRANCH}\n数据目录: {data_dir}\n缓存: {cache}")
        elif args.command == "list":
            print("\n".join(list_cloud(data_dir)) or "云端暂无存档。")
        elif args.command == "push":
            path, commit = push(data_dir, args.name, args.include_keeper)
            print(f"已上传: {BRANCH}/{path}\nGit commit: {commit}")
        elif args.command == "pull":
            backup = pull(data_dir, args.name, args.replace_local)
            print(f"已下载并导入: {args.name}")
            if backup:
                print(f"覆盖前的本地备份: {backup}")


if __name__ == "__main__":
    main()
