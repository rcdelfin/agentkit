#!/usr/bin/env python3
"""Discover skill metadata without loading or executing skill bodies."""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import NamedTuple


class Skill(NamedTuple):
    name: str
    description: str
    path: str


def parse_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value[1:-1]
        return parsed if isinstance(parsed, str) else str(parsed)
    return value


def read_frontmatter(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8", errors="replace") as source:
        if source.readline().strip() != "---":
            raise ValueError("missing YAML frontmatter")

        lines: list[str] = []
        for line in source:
            if line.strip() == "---":
                break
            lines.append(line.rstrip("\n"))
        else:
            raise ValueError("unterminated YAML frontmatter")

    fields: dict[str, str] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line or line[0].isspace() or ":" not in line:
            index += 1
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        block_style = (
            value[0]
            if value
            and value[0] in {"|", ">"}
            and all(character in "+-123456789" for character in value[1:])
            else None
        )
        if block_style is None:
            fields[key] = parse_scalar(value)
            index += 1
            continue

        folded = block_style == ">"
        index += 1
        block: list[str] = []
        while index < len(lines):
            block_line = lines[index]
            if block_line and not block_line[0].isspace():
                break
            block.append(block_line.strip())
            index += 1

        if folded:
            fields[key] = " ".join(part for part in block if part)
        else:
            fields[key] = "\n".join(block).strip()

    return fields


def discover(root: Path) -> tuple[list[Skill], list[str]]:
    skills: list[Skill] = []
    issues: list[str] = []
    visited_directories: set[tuple[int, int]] = set()
    stack = [root]

    while stack:
        directory = stack.pop()
        try:
            stat = directory.stat()
        except OSError as error:
            issues.append(f"{directory}: {error}")
            continue

        identity = (stat.st_dev, stat.st_ino)
        if identity in visited_directories:
            continue
        visited_directories.add(identity)

        try:
            entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
        except OSError as error:
            issues.append(f"{directory}: {error}")
            continue

        child_directories: list[Path] = []
        for entry in entries:
            entry_path = Path(entry.path)
            if entry.name.startswith("."):
                continue
            if entry.is_symlink() and not entry_path.exists():
                issues.append(f"{entry_path}: broken symlink")
                continue
            try:
                if entry.is_dir(follow_symlinks=True):
                    child_directories.append(entry_path)
            except OSError as error:
                issues.append(f"{entry_path}: {error}")

        skill_path = directory / "SKILL.md"
        if skill_path.is_file():
            try:
                metadata = read_frontmatter(skill_path)
            except (OSError, ValueError) as error:
                issues.append(f"{skill_path}: {error}")
            else:
                name = metadata.get("name", "").strip()
                description = " ".join(metadata.get("description", "").split())
                if not name or not description:
                    issues.append(
                        f"{skill_path}: frontmatter requires name and description"
                    )
                else:
                    try:
                        display_path = skill_path.relative_to(root.parent)
                    except ValueError:
                        display_path = skill_path
                    skills.append(Skill(name, description, str(display_path)))

        stack.extend(reversed(child_directories))

    name_counts = Counter(skill.name for skill in skills)
    duplicate_names = {name for name, count in name_counts.items() if count > 1}
    for name in sorted(duplicate_names):
        paths = ", ".join(skill.path for skill in skills if skill.name == name)
        issues.append(f"duplicate skill name {name!r}: {paths}")

    return sorted(skills, key=lambda skill: (skill.name, skill.path)), issues


def parse_args() -> argparse.Namespace:
    # Preserve the installed path if this skill is itself symlinked. Resolving
    # __file__ here could incorrectly scan the source repository's skills.
    default_root = Path(__file__).absolute().parents[2]
    parser = argparse.ArgumentParser(
        description="List discoverable skills from SKILL.md frontmatter."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=default_root,
        help=f"skills root (default: {default_root})",
    )
    parser.add_argument(
        "--format",
        choices=("tsv", "json"),
        default="tsv",
        help="output format (default: tsv)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero when metadata or links are invalid",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"error: skills root does not exist: {root}", file=sys.stderr)
        return 2

    skills, issues = discover(root)
    if args.format == "json":
        print(json.dumps([skill._asdict() for skill in skills], indent=2))
    else:
        for skill in skills:
            print(f"{skill.name}\t{skill.path}\t{skill.description}")

    for issue in issues:
        print(f"warning: {issue}", file=sys.stderr)

    return 1 if args.check and issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
