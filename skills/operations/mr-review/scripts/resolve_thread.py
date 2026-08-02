#!/usr/bin/env python3
"""Reply to a GitLab MR discussion thread and resolve it, in one call.

Wraps the two-step resolve loop from the mr-review skill:

    POST   .../discussions/<id>/notes   { body: "<note>" }
    PUT    .../discussions/<id>         { resolved: true }

Building the URLs in Python (and calling `glab api` via subprocess) sidesteps
the rtk-wrapper gotcha where shell-variable-interpolated glab URLs silently
404 — see the skill's Pitfalls. The discussion id is never on the shell
command line as part of a URL.

Usage:
    resolve_thread.py <project> <iid> <discussion_id> "<note>"
    resolve_thread.py <project> <iid> <discussion_id> --note-file -
    echo "fixed in abc123" | resolve_thread.py <project> <iid> <id> --note-file -

Always cite the fix commit SHA in the note. Resolving before pushing makes the
fix untraceable if the push fails — push first.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.parse


def encode_project(project: str) -> str:
    if "%2F" in project or "%2f" in project:
        return project
    return urllib.parse.quote(project.strip(), safe="")


def glab(method: str, path: str, fields: dict | None = None) -> dict:
    cmd = ["glab", "api", "-X", method, path]
    for key, value in (fields or {}).items():
        # -F sends form data (needed for the boolean resolved=true); -f for strings.
        if isinstance(value, bool):
            cmd += ["-F", f"{key}={'true' if value else 'false'}"]
        else:
            cmd += ["-f", f"{key}={value}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(f"glab api {method} {path} failed:\n{result.stderr.strip()}\n")
        sys.exit(result.returncode)
    if not result.stdout.strip():
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"_raw": result.stdout[:500]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", help="GitLab project path (group/project) or url-encoded")
    parser.add_argument("iid", help="Merge request IID")
    parser.add_argument("discussion_id", help="Discussion (thread) id")
    parser.add_argument("note", nargs="?", help="Reply body (mutually exclusive with --note-file)")
    parser.add_argument("--note-file", help="Read reply body from a file (- for stdin)")
    args = parser.parse_args()

    if args.note and args.note_file:
        parser.error("provide either a positional note or --note-file, not both")

    if args.note_file:
        if args.note_file == "-":
            body = sys.stdin.read()
        else:
            with open(args.note_file, encoding="utf-8") as fh:
                body = fh.read()
    else:
        body = args.note or ""

    body = body.strip()
    if not body:
        parser.error("note body is empty")

    project = encode_project(args.project)
    base = f"projects/{project}/merge_requests/{args.iid}/discussions/{args.discussion_id}"

    posted = glab("POST", f"{base}/notes", {"body": body})
    note_id = posted.get("id")

    resolved = glab("PUT", base, {"resolved": True})
    resolvable = [n for n in resolved.get("notes", []) if n.get("resolvable")]
    all_resolved = all(n.get("resolved") for n in resolvable)

    status = "RESOLVED" if all_resolved else "STILL OPEN"
    print(f"note #{note_id} posted → {status} ({args.discussion_id[:16]})")
    if not all_resolved:
        sys.exit(2)


if __name__ == "__main__":
    main()
