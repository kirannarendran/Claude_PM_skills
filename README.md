# Claude_PM_skills

A collection of Claude Code skills for product management and related work. Skills are grouped into
category folders under `skills/`.

## Skills

| Category | Skill | What it does |
|---|---|---|
| [strategy-and-market](skills/strategy-and-market/) | [porters-five-forces](skills/strategy-and-market/porters-five-forces/) | Porter's Five Forces analysis of a company, with rated forces, dated evidence and a quality checker |

Planned categories: discovery and research, prioritization and planning, specs and communication, and metrics
and experiments.

## Install a skill

Clone the repo, then copy the skill folder into your Claude Code skills directory.

```bash
git clone https://github.com/kirannarendran/Claude_PM_skills.git
cd Claude_PM_skills

# For all of your projects:
mkdir -p ~/.claude/skills && cp -R skills/strategy-and-market/porters-five-forces ~/.claude/skills/

# Or for one project only, from inside that project:
# mkdir -p .claude/skills && cp -R /path/to/Claude_PM_skills/skills/strategy-and-market/porters-five-forces .claude/skills/
```

Start a new Claude Code session, then ask for what the skill does. For example, "Do a Five Forces analysis on
Swiggy" loads the Five Forces skill.

## Optional: automatic quality check (porters-five-forces)

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
python3 skills/strategy-and-market/porters-five-forces/scripts/check_output.py "Competitive Strategy/<company>-five-forces.md"
```

Exit code 0 means all checks passed. Exit code 1 lists the failures.

## Adding a skill

Each skill lives in `skills/<category>/<skill-name>/` with a `SKILL.md` at its root. Put it in an existing
category folder when one fits, or create a new one. Include `evals/` and `scripts/` when the skill has them.

## Limits

- Checkers test structure and internal consistency. They do not judge whether the reasoning or the sources are
  right. Read the output yourself before you rely on it.
- Skills that use web search depend on what is published, and figures can conflict across sources. The skills
  flag these as gaps rather than hiding them.

## License

TBD
