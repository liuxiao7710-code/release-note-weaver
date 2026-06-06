from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


CONVENTIONAL_RE = re.compile(
    r"^(?P<type>[a-zA-Z]+)(?:\((?P<scope>[^)]+)\))?(?P<bang>!)?: (?P<description>.+)$"
)

SECTION_ORDER = [
    ("breaking", "Breaking Changes"),
    ("feat", "Features"),
    ("fix", "Bug Fixes"),
    ("perf", "Performance"),
    ("refactor", "Refactoring"),
    ("docs", "Documentation"),
    ("test", "Tests"),
    ("chore", "Maintenance"),
    ("other", "Other Changes"),
]


@dataclass(frozen=True)
class Commit:
    raw: str
    type: str
    scope: str | None
    description: str
    breaking: bool = False


def parse_commit(subject: str) -> Commit | None:
    subject = subject.strip()
    if not subject:
        return None
    match = CONVENTIONAL_RE.match(subject)
    if not match:
        return Commit(raw=subject, type="other", scope=None, description=subject, breaking=False)

    commit_type = match.group("type").lower()
    breaking = bool(match.group("bang"))
    return Commit(
        raw=subject,
        type=commit_type if commit_type in {key for key, _ in SECTION_ORDER} else "other",
        scope=match.group("scope"),
        description=match.group("description").strip(),
        breaking=breaking,
    )


def parse_commits(lines: list[str]) -> list[Commit]:
    commits: list[Commit] = []
    for line in lines:
        commit = parse_commit(line)
        if commit is not None:
            commits.append(commit)
    return commits


def filter_commits(commits: list[Commit], exclude_types: list[str] | None = None) -> list[Commit]:
    excluded = {commit_type.lower() for commit_type in (exclude_types or [])}
    if not excluded:
        return commits
    return [commit for commit in commits if commit.type.lower() not in excluded]


def format_commit(commit: Commit) -> str:
    if commit.scope:
        return f"- **{commit.scope}:** {commit.description}"
    return f"- {commit.description}"


def render_release_notes(commits: list[Commit], version: str, date: str | None = None) -> str:
    release_date = date or dt.date.today().isoformat()
    groups: dict[str, list[Commit]] = {key: [] for key, _ in SECTION_ORDER}
    for commit in commits:
        key = "breaking" if commit.breaking else commit.type
        groups.setdefault(key, []).append(commit)

    lines = [f"## {version} - {release_date}", ""]
    wrote_section = False
    for key, heading in SECTION_ORDER:
        entries = groups.get(key, [])
        if not entries:
            continue
        wrote_section = True
        lines.extend([f"### {heading}", ""])
        lines.extend(format_commit(commit) for commit in entries)
        lines.append("")

    if not wrote_section:
        lines.extend(["### Changes", "", "- No commit subjects were provided.", ""])

    return "\n".join(lines).rstrip() + "\n"


def read_commit_lines(path: str) -> list[str]:
    if path == "-":
        return sys.stdin.read().splitlines()
    return Path(path).read_text(encoding="utf-8").splitlines()


def git_commit_lines(commit_range: str | None, limit: int | None) -> list[str]:
    command = ["git", "log", "--format=%s"]
    if limit is not None:
        command.insert(2, f"-n{limit}")
    if commit_range:
        command.append(commit_range)
    completed = subprocess.run(command, text=True, capture_output=True, check=True)
    return completed.stdout.splitlines()


def prepend_to_changelog(path: str | Path, notes: str) -> None:
    changelog = Path(path)
    if not changelog.exists():
        changelog.write_text("# Changelog\n\n" + notes, encoding="utf-8")
        return

    existing = changelog.read_text(encoding="utf-8")
    if existing.startswith("# Changelog"):
        head, _, tail = existing.partition("\n")
        updated = head + "\n\n" + notes + ("\n" + tail.lstrip("\n") if tail else "")
    else:
        updated = notes + "\n" + existing
    changelog.write_text(updated, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate release notes from Conventional Commit subjects.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--from-file", help="Read commit subjects from a file, or '-' for stdin.")
    source.add_argument("--range", dest="commit_range", help="Git revision range, for example v0.1.0..HEAD.")
    parser.add_argument("--limit", type=int, default=None, help="Limit git log entries when reading from git.")
    parser.add_argument("--version", required=True, help="Release version heading.")
    parser.add_argument("--date", default=None, help="Release date, defaults to today.")
    parser.add_argument("--update", help="Prepend generated notes to this changelog file.")
    parser.add_argument("--exclude-type", action="append", default=[], help="Commit type to omit from generated notes. May be used more than once.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    lines = read_commit_lines(args.from_file) if args.from_file else git_commit_lines(args.commit_range, args.limit)
    notes = render_release_notes(filter_commits(parse_commits(lines), args.exclude_type), args.version, args.date)
    if args.update:
        prepend_to_changelog(args.update, notes)
    else:
        print(notes, end="")
    return 0
