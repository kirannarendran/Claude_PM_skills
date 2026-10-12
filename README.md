# porters-five-forces

A Claude Code skill that produces a Porter's Five Forces analysis of a company: each force rated 1–5 with
confidence, the evidence and dated sources behind every rating, what would change it, and what it means for
the company's position. Output is a Markdown write-up, which you can convert to PDF.

It also ships a checker (`scripts/check_output.py`) that tests each write-up against the skill's contract:
required sections, a ratings table that matches the rating lines, dated citations, an attractiveness label that
matches the scores, dated sources, and no leftover placeholders.

## Install

Clone the repo, then copy the skill folder into your Claude Code skills directory.

```bash
git clone https://github.com/<owner>/porters-five-forces-skill.git
cd porters-five-forces-skill

# For all of your projects:
mkdir -p ~/.claude/skills && cp -R skills/porters-five-forces ~/.claude/skills/

# Or for one project only, from inside that project:
# mkdir -p .claude/skills && cp -R /path/to/porters-five-forces-skill/skills/porters-five-forces .claude/skills/
```

Start a new Claude Code session. Ask something like "Do a Five Forces analysis on Swiggy" and the skill loads.

## Optional: automatic quality check

Without this step, the checker still runs if you ask for it, but not automatically after each write. To run it
after every write or edit of a five-forces file, add this to `~/.claude/settings.json`, merging with any
existing `hooks` entries:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -I \"$HOME/.claude/skills/porters-five-forces/scripts/check_output.py\" --hook",
            "timeout": 30,
            "statusMessage": "Evaluating five-forces output"
          }
        ]
      }
    ]
  }
}
```

If you installed the skill into a project's `.claude/skills/` instead, use
`"$CLAUDE_PROJECT_DIR/.claude/skills/porters-five-forces/scripts/check_output.py"` as the path.

The hook only checks files whose path matches `Competitive Strategy/*five-forces*.md`. Other files are ignored.

## Check a write-up by hand

```bash
python3 scripts/check_output.py "Competitive Strategy/<company>-five-forces.md"
```

Exit code 0 means all checks passed. Exit code 1 lists the failures.

## What's in the repo

| Path | Purpose |
|---|---|
| `skills/porters-five-forces/SKILL.md` | The skill: process, rating rules, output template |
| `skills/porters-five-forces/scripts/check_output.py` | The quality checker, also used as the hook |
| `skills/porters-five-forces/evals/evals.json` | Five test prompts, with expectations for judgment-based checks |

## Limits

- The checker tests structure and internal consistency. It does not judge whether the reasoning or the sources
  are right. Read the analysis yourself before you rely on it.
- The skill uses web search for evidence. Results depend on what is published, and figures can conflict across
  sources. The skill flags these as gaps rather than hiding them.
- The write-up is a lens, not a valuation. It doesn't say whether a stock is cheap or expensive.

## License

TBD
