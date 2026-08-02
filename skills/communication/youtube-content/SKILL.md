---
name: youtube-content
description: "YouTube transcripts to summaries, threads, blogs."
platforms: [linux, macos, windows]
---

# YouTube Content Tool

## When to use

Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video. Transforms transcripts into structured content (chapters, summaries, threads, blog posts).

Extract transcripts from YouTube videos and convert them into useful formats.

## Setup

```bash
pip install youtube-transcript-api
```

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file. The script accepts any standard YouTube URL format, short links (youtu.be), shorts, embeds, live links, or a raw 11-character video ID.

```bash
# JSON output with metadata
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## Output Formats

After fetching the transcript, format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

### Example — Chapters Output

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Workflow

1. **Fetch** the transcript using the helper script with `--text-only --timestamps`.
2. **Validate**: confirm the output is non-empty and in the expected language. If empty, retry without `--language` to get any available transcript. If still empty, tell the user the video likely has transcripts disabled.
3. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
4. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
5. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## Pipeline: Transcript → LLM Wiki

When the user shares a YouTube URL and asks to add it to their wiki/knowledge base:

1. **Fetch transcript** with the JSON output (not `--text-only`):
   ```bash
   python3 SKILL_DIR/scripts/fetch_transcript.py "URL" 2>/dev/null
   ```
   Returns JSON: `{video_id, segment_count, duration, full_text}`.
   Note: `full_text` is a single unbroken line (no `\n`). Parse with `json.load()`.

2. **Get video title/channel** — the JSON response often lacks `title` and `channel`.
   Use `browser_navigate` to the YouTube URL and read the `<h1>` heading. The page title
   follows the pattern: `"Video Title - YouTube"`.

3. **Save raw transcript** to `raw/transcripts/<topic-slug>-YYYY-MM.md` with frontmatter:
   ```yaml
   ---
   source_url: https://www.youtube.com/watch?v=VIDEO_ID
   video_id: VIDEO_ID
   channel: Channel Name
   title: "Video Title"
   duration: "MM:SS"
   ingested: "YYYY-MM-DD"
   sha256: <hex of body>
   ---
   ```
   Then the `full_text` content. Compute sha256 over body only (after closing `---`).

4. **Read the wiki's existing state** — SCHEMA.md/CLAUDE.md, index.md, recent log.md (per llm-wiki skill).
   This is non-negotiable: orient before ingesting.

5. **Read and chunk the transcript** — `full_text` is one line. Use `execute_code` with
   `re.split(r'(?<=[.!?])\s+', text)` to break into ~2000-char sentence-bounded chunks.
   Read through all chunks to identify entities, concepts, and themes.

6. **Identify entities and concepts** from the transcript that meet the wiki's page thresholds.
   A single video typically yields 1 main page + 2-4 glossary entries.

7. **Create/update wiki pages** — entities, concepts, cross-references.
   Update `index.md` and `log.md` after all pages are written.

8. **Lint immediately** — run wikilink resolution, required-sections check, index completeness,
   and raw-path wikilink audit as a `terminal` inline-python block. Catches issues while context is fresh.
   See `llm-wiki` skill for the repeatable lint pattern.
   **Do NOT use `execute_code` for the lint script** — it requires user approval and times out
   if the user doesn't respond within ~30s. Use `terminal` with inline python3 -c "..." instead.

   **Pitfall: editing index.md with `patch` tool**. The LLM wiki `index.md` uses `||` pipe-prefixed
   table rows. The `patch` tool's fuzzy matching can silently fail on pipe characters — it reports
   success but the file is unchanged (e.g., `|||` ≠ `||` to the matcher). When you need to fix
   table row formatting in `index.md`, use `terminal` with `sed` directly:
   ```bash
   sed -i '' 's/^||| /|| /g' wiki/index.md
   ```
   Verify with `sed -n '<line>p' wiki/index.md` after.

Some videos (tech talks, hardware reviews) produce fewer entity pages but rich comparison/analysis
pages — adapt the page types to the content, don't force entity pages when the source is
primarily analytical.

## Multi-Video Session Pattern

When ingesting multiple videos in one session:
1. Fetch all transcripts first (one `terminal` call each, saving to `/tmp/yt_transcript_N.md`)
2. Save all raw transcripts with frontmatter
3. For each video: read chunks, create pages + glossary entries
4. Single pass: update index.md and log.md for ALL ingests
5. Run the lint script once against ALL new pages from ALL ingests

This avoids redundant lint runs and catches cross-ingest wikilink issues in one pass.

## Cross-Referencing Existing Pages

After creating new pages from a video, search for existing glossary/pages that cover related
concepts and add cross-references to the new pages. This is NOT optional — it's what makes
the wiki compound rather than accumulate. Typical trigger: new page mentions a concept that
already has its own glossary entry. Add a `[[pages/new-page]]` link to the existing page's
Related section.

**Before creating wikilinks**, always `search_files` or `ls` the target directory to confirm
the actual filename. Wikilinks must match the real filename (minus `.md`). A common error:
linking to `glossary/llama-cpp-local-inference` when the file is actually `glossary/local-llm-inference.md`.

## Error Handling

- **Transcript disabled**: tell the user, then offer fallback paths (see below).
- **Private/unavailable video**: relay the error and ask the user to verify the URL.
- **No matching language**: retry without `--language` to fetch any available transcript, then note the actual language to the user.
- **Dependency missing**: run `pip install youtube-transcript-api` and retry.

### Fallback: Transcript Disabled

When the transcript API returns "Transcripts are disabled for this video," the user can still get a clipping. Offer these options (in order):

1. **Web research fallback** — Search for recaps, recaps, play-by-play, and articles about the video content. Use `web_search` with the video title + channel + date to find detailed coverage. Extract multiple sources with `web_extract`. Combine into a structured clipping using the same output formats (summary, chapters, blog post, etc.). This works well for sports highlights, news clips, and trending videos that have been covered by sports/news media.

2. **Browser vision fallback** — Navigate to the video with `browser_navigate`, play it, and capture screenshots at intervals with `browser_vision`. Then summarize from the screenshots. **Note:** this only works if the active model supports native vision; non-vision models will fail on `vision_analyze` / `browser_vision`. Check before offering this path.

3. **Skip** — If neither fallback fits, tell the user honestly.

For the web research path, the workflow is:
1. `browser_navigate` to the YouTube URL to get the video title from the `<h1>` heading.
2. `web_search` for recaps/highlights using the video title, channel name, and date.
3. `web_extract` the top 2–3 results for detailed content.
4. If the video is a sports game, also check `basketball-reference.com` (or equivalent) for play-by-play data.
5. Synthesize into the requested format, citing sources.
