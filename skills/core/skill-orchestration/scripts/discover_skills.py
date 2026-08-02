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
                    skills.append(Skill(name, description, str(skill_path.absolute())))

        stack.extend(reversed(child_directories))

    name_counts = Counter(skill.name for skill in skills)
    duplicate_names = {name for name, count in name_counts.items() if count > 1}
    for name in sorted(duplicate_names):
        paths = ", ".join(skill.path for skill in skills if skill.name == name)
        issues.append(f"duplicate skill name {name!r}: {paths}")

    return sorted(skills, key=lambda skill: (skill.name, skill.path)), issues


def default_skills_root() -> Path:
    # Preserve the installed path if this skill is itself symlinked. Resolving
    # __file__ here could incorrectly scan the source repository's skills.
    script_path = Path(__file__).absolute()
    return next(
        (parent for parent in script_path.parents if parent.name == "skills"),
        script_path.parents[3],
    )


def project_skills_roots(agent: str) -> list[Path]:
    shared_root = default_skills_root()
    relative_roots: tuple[str, ...] = {
        "auto": (".agents/skills", ".pi/skills", ".claude/skills"),
        "pi": (".pi/skills", ".agents/skills"),
        "claude": (".claude/skills", ".agents/skills"),
        "codex": (".codex/skills", ".agents/skills"),
    }[agent]
    roots: list[Path] = []
    found_roots: set[str] = set()
    start = Path.cwd().absolute()
    home = Path.home().absolute()
    for parent in (start, *start.parents):
        if parent == home:
            break
        for relative_root in relative_roots:
            if relative_root in found_roots:
                continue
            candidate = (parent / relative_root).absolute()
            if candidate == shared_root or not candidate.is_dir():
                continue
            roots.append(candidate)
            found_roots.add(relative_root)
        if len(found_roots) == len(relative_roots):
            break
    return roots


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List discoverable skills from SKILL.md frontmatter."
    )
    parser.add_argument(
        "--agent",
        choices=("auto", "pi", "claude", "codex"),
        default="auto",
        help="project skill root selection (default: auto)",
    )
    parser.add_argument(
        "--root",
        action="append",
        type=Path,
        help="skills root; repeat to search in precedence order",
    )
    parser.add_argument(
        "--format",
        choices=("tsv", "json"),
        default="tsv",
        help="output format (default: tsv)",
    )
    parser.add_argument(
        "--name",
        help="print the exact path for one skill name",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero when metadata or links are invalid",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    # Keep symlink spelling in emitted paths so callers can read the discovered
    # entry instead of reconstructing a different namespace from its name.
    configured_roots = args.root
    if configured_roots is None:
        configured_roots = project_skills_roots(args.agent) + [default_skills_root()]
    roots = [root.expanduser().absolute() for root in configured_roots]
    skills: list[Skill] = []
    issues: list[str] = []
    for root in roots:
        if not root.is_dir():
            issues.append(f"{root}: skills root does not exist")
            continue
        discovered, root_issues = discover(root)
        skills.extend(discovered)
        issues.extend(root_issues)

    # Earlier roots win, allowing project skills to override shared skills by
    # name without flattening either namespace or changing emitted paths.
    unique_skills: list[Skill] = []
    seen_names: set[str] = set()
    for skill in skills:
        if skill.name in seen_names:
            continue
        seen_names.add(skill.name)
        unique_skills.append(skill)

    if args.name is not None:
        matches = [skill for skill in unique_skills if skill.name == args.name.strip()]
        if len(matches) != 1:
            detail = "not found" if not matches else "duplicate name"
            print(f"error: skill {args.name!r}: {detail}", file=sys.stderr)
            return 1
        print(matches[0].path)
    elif args.format == "json":
        print(json.dumps([skill._asdict() for skill in unique_skills], indent=2))
    else:
        for skill in unique_skills:
            print(f"{skill.name}\t{skill.path}\t{skill.description}")

    for issue in issues:
        print(f"warning: {issue}", file=sys.stderr)

    return 1 if args.check and issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
