#!/usr/bin/env bash
#
# setup.sh — Link AI harness instruction files to ~/.agents/instructions/
#
# Detects installed AI coding harnesses and symlinks their instruction
# files to canonical copies in instructions/. Existing files are backed
# up with a .bak suffix. Safe to re-run.
#
# Usage:
#   ./setup.sh              # link all detected harnesses
#   ./setup.sh --unlink     # remove symlinks, restore .bak if available
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTRUCTIONS="${SCRIPT_DIR}/instructions"

# ── Helpers ──────────────────────────────────────────────────────────

green() { printf '\033[0;32m✓\033[0m %s\n' "$1"; }
yellow() { printf '\033[1;33m⚠\033[0m %s\n' "$1"; }
dim() { printf '\033[2m  ⊘ %s\033[0m\n' "$1"; }

# Create or refresh a symlink, backing up any existing real file.
link() {
	local canonical="$1" target="$2"

	mkdir -p "$(dirname "$target")"

	# Already linked to the right place?
	if [ -L "$target" ]; then
		local current
		current="$(readlink "$target")"
		if [ "$current" = "$canonical" ]; then
			dim "$(basename "$target") already linked"
			return 0
		fi
		rm "$target"
	elif [ -f "$target" ]; then
		mv "$target" "${target}.bak"
		yellow "Backed up $(basename "$target") → $(basename "$target").bak"
	fi

	ln -s "$canonical" "$target"
	green "$(basename "$target") → $(basename "$canonical")"
}

# Write a small file (for @import wrappers). Backs up if content differs.
write_file() {
	local target="$1" content="$2"

	if [ -L "$target" ]; then
		rm "$target"
	elif [ -f "$target" ]; then
		if printf '%s\n' "$content" | diff - "$target" >/dev/null 2>&1; then
			dim "$(basename "$target") already correct"
			return 0
		fi
		mv "$target" "${target}.bak"
		yellow "Backed up $(basename "$target") → $(basename "$target").bak"
	fi

	printf '%s\n' "$content" >"$target"
	green "$(basename "$target") written"
}

# Remove a symlink created by this script, restore .bak if it exists.
unlink_one() {
	local target="$1"

	if [ -L "$target" ]; then
		rm "$target"
		if [ -f "${target}.bak" ]; then
			mv "${target}.bak" "$target"
			green "Restored $(basename "$target") from .bak"
		else
			dim "Removed $(basename "$target") symlink"
		fi
	elif [ -f "${target}.bak" ]; then
		mv "${target}.bak" "$target"
		green "Restored $(basename "$target") from .bak"
	fi
}

# ── Pre-flight ───────────────────────────────────────────────────────

if [ ! -f "${INSTRUCTIONS}/AGENTS.md" ]; then
	echo "Error: ${INSTRUCTIONS}/AGENTS.md not found." >&2
	exit 1
fi

# ── Mode ─────────────────────────────────────────────────────────────

MODE="${1:-link}"

if [ "$MODE" = "--unlink" ]; then
	echo ""
	echo "Unlinking harness instruction files…"
	echo ""

	# Pi
	if [ -d "${HOME}/.pi/agent" ]; then
		echo "Pi"
		unlink_one "${HOME}/.pi/agent/SYSTEM.md"
		unlink_one "${HOME}/.pi/agent/AGENTS.md"
		unlink_one "${HOME}/.pi/agent/RTK.md"
		echo ""
	fi

	# Claude Code
	if [ -d "${HOME}/.claude" ]; then
		echo "Claude Code"
		unlink_one "${HOME}/.claude/CLAUDE.md"
		unlink_one "${HOME}/.claude/SYSTEM.md"
		unlink_one "${HOME}/.claude/AGENTS.md"
		unlink_one "${HOME}/.claude/RTK.md"
		echo ""
	fi

	# Codex
	if [ -d "${HOME}/.codex" ]; then
		echo "Codex"
		unlink_one "${HOME}/.codex/AGENTS.md"
		echo ""
	fi

	# Gemini CLI
	if [ -d "${HOME}/.gemini" ]; then
		echo "Gemini CLI"
		unlink_one "${HOME}/.gemini/GEMINI.md"
		echo ""
	fi

	echo "Done. Originals restored from .bak where available."
	exit 0
fi

# ── Link ─────────────────────────────────────────────────────────────

echo ""
echo "Linking harness instructions → ${INSTRUCTIONS}/"
echo ""

# ── Pi ───────────────────────────────────────────────────────────────
if [ -d "${HOME}/.pi/agent" ]; then
	echo "Pi"
	link "${INSTRUCTIONS}/SYSTEM.md" "${HOME}/.pi/agent/SYSTEM.md"
	link "${INSTRUCTIONS}/AGENTS.md" "${HOME}/.pi/agent/AGENTS.md"
	[ -f "${INSTRUCTIONS}/RTK.md" ] && link "${INSTRUCTIONS}/RTK.md" "${HOME}/.pi/agent/RTK.md"
	echo ""
fi

# ── Claude Code ──────────────────────────────────────────────────────
# CLAUDE.md is a thin @import wrapper; SYSTEM.md and AGENTS.md are
# symlinks so Claude Code resolves them relative to ~/.claude/.
if [ -d "${HOME}/.claude" ]; then
	echo "Claude Code"
	link "${INSTRUCTIONS}/SYSTEM.md" "${HOME}/.claude/SYSTEM.md"
	link "${INSTRUCTIONS}/AGENTS.md" "${HOME}/.claude/AGENTS.md"
	[ -f "${INSTRUCTIONS}/RTK.md" ] && link "${INSTRUCTIONS}/RTK.md" "${HOME}/.claude/RTK.md"
	write_file "${HOME}/.claude/CLAUDE.md" '@SYSTEM.md

@AGENTS.md'
	echo ""
fi

# ── Codex ────────────────────────────────────────────────────────────
if [ -d "${HOME}/.codex" ]; then
	echo "Codex"
	link "${INSTRUCTIONS}/AGENTS.md" "${HOME}/.codex/AGENTS.md"
	echo ""
fi

# ── Gemini CLI ───────────────────────────────────────────────────────
if [ -d "${HOME}/.gemini" ]; then
	echo "Gemini CLI"
	link "${INSTRUCTIONS}/AGENTS.md" "${HOME}/.gemini/GEMINI.md"
	echo ""
fi

# ── Add more harnesses here ──────────────────────────────────────────
# Pattern:
#   if [ -d "${HOME}/.your-harness" ]; then
#     echo "Your Harness"
#     link "${INSTRUCTIONS}/AGENTS.md" "${HOME}/.your-harness/INSTRUCTIONS.md"
#     echo ""
#   fi

echo "Done. Edit ${INSTRUCTIONS}/ to update all linked harnesses at once."
echo "Run ./setup.sh --unlink to restore originals."
echo ""
