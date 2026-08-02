#!/usr/bin/env python3
"""List review threads on a GitLab MR, categorized by status and severity.

Replaces the inline `glab api ... | python3 -c "..."` snippets from the
mr-review skill. Shells out to `glab api` for auth (no token handling here),
parses the discussions, and prints each reviewable thread with:

  STATUS   SEVERITY  @author   <first line of the finding>      <discussion-id>

STATUS is OPEN or RESOLVED, computed with the resolvable-aware check (system
notes return `resolved: null`, so a naive `all(resolved)` lies — see the
skill's Pitfalls). The AI review bot's informational "work complete" summary
thread has no resolvable note and is skipped automatically.

Usage:
    show_threads.py <project> <iid>            # all threads
    show_threads.py <project> <iid> --open      # only unresolved
    show_threads.py <project> <iid> --json      # raw parse, no formatting

<project> may be raw ("group/project") or url-encoded; it is encoded here.

Exit code: 0 always (a clean MR just prints "no open threads").
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.parse

# Severity markers the GitLab AI Assistant prefixes findings with.
SEVERITY_MARKERS = {
    "🔴": "High",
    "🟠": "Medium",
    "🟡": "Low",
}


def encode_project(project: str) -> str:
    # Leave an already-encoded path (%2F present) alone.
    if "%2F" in project or "%2f" in project:
        return project
    return urllib.parse.quote(project.strip(), safe="")


def glab_api(path: str) -> list | dict:
    result = subprocess.run(
        ["glab", "api", path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr.strip() + "\n")
        sys.exit(result.returncode)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        sys.stderr.write("glab api returned non-JSON output:\n" + result.stdout[:500])
        sys.exit(1)


def first_line(body: str, width: int = 70) -> str:
    # Strip markdown severity / bold prefixes for a compact one-liner.
    line = body.strip().splitlines()[0] if body.strip() else ""
    return line[:width] + ("…" if len(line) > width else "")


def severity_of(body: str) -> str:
    for marker, label in SEVERITY_MARKERS.items():
        if marker in body:
            return label
    return ""


def thread_is_open(notes: list) -> bool:
    # A thread is open iff some resolvable note is unresolved. System/auto
    # notes are not resolvable and return resolved=null — exclude them.
    return any(n.get("resolvable") and not n.get("resolved") for n in notes)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", help="GitLab project path (group/project) or url-encoded")
    parser.add_argument("iid", help="Merge request IID")
    parser.add_argument("--open", action="store_true", help="show only unresolved threads")
    parser.add_argument("--json", action="store_true", help="emit raw parsed JSON")
    args = parser.parse_args()

    project = encode_project(args.project)
    discussions = glab_api(f"projects/{project}/merge_requests/{args.iid}/discussions")

    if args.json:
        print(json.dumps(discussions, indent=2))
        return

    rows: list[tuple[str, str, str, str, str]] = []
    for disc in discussions:
        notes = disc.get("notes", [])
        # Only threads that actually carry reviewable feedback (resolvable
        # notes). Drops system threads and the AI summary note.
        resolvable = [n for n in notes if n.get("resolvable")]
        if not resolvable:
            continue
        open_ = thread_is_open(notes)
        if args.open and not open_:
            continue
        # The finding text = first non-system note body (usually the bot's).
        finding = next((n for n in notes if not n.get("system")), notes[0])
        author = finding.get("author", {}).get("username", "?")
        rows.append(
            (
                "OPEN   " if open_ else "RESOLVED",
                severity_of(finding.get("body", "")),
                f"@{author}",
                first_line(finding.get("body", "")),
                disc.get("id", "")[:16],
            )
        )

    if not rows:
        print("no open threads" if args.open else "no reviewable threads")
        return

    open_count = sum(1 for r in rows if r[0] == "OPEN   ")
    print(f"{open_count} open / {len(rows)} threads\n")
    for status, sev, author, line, did in rows:
        sev = f"[{sev}]" if sev else "[----]"
        print(f"{status} {sev:9} {author:20} {line}")
        print(f"          {did}")


if __name__ == "__main__":
    main()
