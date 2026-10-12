# Claude_PM_skills

A collection of Claude Code skills for product management and related work. Skills are grouped into
category folders under `skills/`.

## Skills

| Category | Skill | What it does |
|---|---|---|
| [strategy-and-market](skills/strategy-and-market/) | [porters-five-forces](skills/strategy-and-market/porters-five-forces/) | Porter's Five Forces analysis of a company, saved as a PDF with a Markdown source |

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

## PDF output

Each skill that produces a write-up saves it as a PDF, next to a Markdown copy. The Five Forces skill writes to
`Competitive Strategy/` in the folder where Claude Code is running:

- `Competitive Strategy/<company>-five-forces.md`: editable source
- `Competitive Strategy/<company>-five-forces.pdf`: the deliverable

To regenerate a PDF from an edited Markdown file:

```bash
python3 ~/.claude/skills/porters-five-forces/scripts/md_to_pdf.py "Competitive Strategy/<company>-five-forces.md"
```

The converter needs the `markdown` Python package (`pip3 install markdown`) and Google Chrome. Set `CHROME_PATH`
to use another Chromium-based browser.

## Adding a skill

Each skill lives in `skills/<category>/<skill-name>/` with a `SKILL.md` at its root. Put it in an existing
category folder when one fits, or create a new one. Include `scripts/` when the skill has them.

## Limits

- Skills that use web search depend on what is published, and figures can conflict across sources. The skills
  flag these as gaps rather than hiding them.
- Read the output yourself before you rely on it. The skills don't check whether the reasoning is right.

## License

TBD
