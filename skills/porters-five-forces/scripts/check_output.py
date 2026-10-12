#!/usr/bin/env python3
"""Check a Porter's Five Forces write-up against the porters-five-forces skill contract.

Usage:
  check_output.py <file.md>            human-readable report; exit 0 = pass, 1 = fail
  check_output.py <file.md> --json     grading.json-style expectations (text/passed/evidence)
  check_output.py --hook               PostToolUse hook mode: reads hook JSON on stdin,
                                       ignores files that aren't five-forces outputs,
                                       exits 2 with the report on stderr when checks fail
"""
import datetime as dt
import json
import os
import re
import sys

FORCES = {
    "entrants": "Threat of new entrants",
    "supplier": "Bargaining power of suppliers",
    "buyer": "Bargaining power of buyers",
    "substitut": "Threat of substitutes",
    "rival": "Competitive rivalry",
}
OUTPUT_PATH_RE = re.compile(r"(^|/)Competitive Strategy/[^/]*five-forces[^/]*\.md$")
FILENAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*-five-forces(-\d{4}-\d{2}-\d{2})?\.md$")
YEAR_RE = re.compile(r"(?<!\d)(19|20)\d{2}(?!\d)")
CITATION_RE = re.compile(r"\[[^\]]*(?<!\d)(19|20)\d{2}(?!\d)[^\]]*\]")
UNDATED_RE = re.compile(r"undated|date unknown|n\.d\.|date not (confirmed|disclosed)", re.I)
PLACEHOLDERS = ["<Company>", "<company>", "<verdict>", "<date>", "<YYYY-MM-DD>", "<period>",
                "<boundary>", "<force>", "<why>", "<confidence>", "x/5", "(same four lines under each)",
                "(repeat for each force)"]


def force_key(text):
    t = text.lower()
    for key in FORCES:
        if key in t:
            return key
    return None


def split_sections(lines):
    """Return [(heading, [body lines])] for each '## ' heading, in order."""
    sections = []
    for line in lines:
        if line.startswith("## "):
            sections.append((line[3:].strip(), []))
        elif sections:
            sections[-1][1].append(line)
    return sections


def find(sections, pred):
    for heading, body in sections:
        if pred(heading):
            return heading, body
    return None, None


def check(path):
    results = []

    def add(name, passed, evidence):
        results.append({"text": name, "passed": bool(passed), "evidence": evidence})

    text = open(path, encoding="utf-8").read()
    lines = text.splitlines()
    sections = split_sections(lines)
    headings = [h for h, _ in sections]

    # 1. File location and name
    name = os.path.basename(path)
    in_folder = os.path.basename(os.path.dirname(os.path.abspath(path))) == "Competitive Strategy"
    add("File is saved in 'Competitive Strategy/' with a <company>[-segment]-five-forces[-YYYY-MM-DD].md name",
        in_folder and FILENAME_RE.match(name), f"path: {path}")

    # 2. Title, meta line, scale line
    title_ok = bool(lines) and re.match(r"^# .+: Porter's Five Forces\s*$", lines[0])
    add("Title line is '# <Company>: Porter's Five Forces'", title_ok, lines[0] if lines else "empty file")

    meta = next((l for l in lines[:6] if "As of" in l), "")
    m = re.search(r"As of (\d{4}-\d{2}-\d{2})", meta)
    asof = None
    if m:
        try:
            asof = dt.date.fromisoformat(m.group(1))
        except ValueError:
            pass
    add("Header gives 'As of YYYY-MM-DD', Horizon and Market",
        asof and "Horizon:" in meta and "Market:" in meta, meta or "no 'As of' line in header")
    add("Header states the rating scale (1 = weak/favorable ... 5 = strong/unfavorable)",
        any(re.search(r"Scale:.*1.*5", l) for l in lines[:8]), "looked in first 8 lines")

    # 3. Required sections, in order
    required = [("Summary", lambda h: h.lower() == "summary"),
                ("Force ratings", lambda h: h.lower() == "force ratings")]
    required += [(FORCES[k], (lambda k: lambda h: re.match(r"^\d\.", h) and force_key(h) == k)(k)) for k in FORCES]
    required += [("Positioning and margin check", lambda h: h.lower().startswith("positioning")),
                 ("Implications", lambda h: h.lower() == "implications"),
                 ("What this does and doesn't establish", lambda h: h.lower().startswith("what this does")),
                 ("Sources", lambda h: h.lower() == "sources"),
                 ("Gaps", lambda h: h.lower() == "gaps")]
    positions, missing = [], []
    for label, pred in required:
        idx = next((i for i, h in enumerate(headings) if pred(h)), None)
        if idx is None:
            missing.append(label)
        else:
            positions.append(idx)
    in_order = positions == sorted(positions)
    add("All required sections are present and in template order", not missing and in_order,
        f"missing: {missing}" if missing else ("order OK" if in_order else f"out of order: {headings}"))

    # 4. Ratings table
    _, table_body = find(sections, lambda h: h.lower() == "force ratings")
    table = {}
    table_problems = []
    for row in (table_body or []):
        if not row.startswith("|") or re.match(r"^\|[\s\-:|]+\|$", row):
            continue
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        key = force_key(cells[0]) if cells else None
        if not key:
            continue
        if len(cells) < 4:
            table_problems.append(f"{cells[0]}: expected 4 columns")
            continue
        rating, conf, verdict = cells[1], cells[2].lower(), cells[3]
        if not re.fullmatch(r"[1-5]", rating):
            table_problems.append(f"{cells[0]}: rating '{rating}' is not an integer 1-5")
        if conf not in ("high", "medium", "low"):
            table_problems.append(f"{cells[0]}: confidence '{cells[2]}' is not high/medium/low")
        if not verdict:
            table_problems.append(f"{cells[0]}: empty verdict")
        table[key] = (int(rating) if rating.isdigit() else None, conf)
    absent = [FORCES[k] for k in FORCES if k not in table]
    add("Ratings table has all five forces with an integer 1-5 rating, a confidence level and a verdict",
        not absent and not table_problems, "; ".join(table_problems + [f"missing row: {a}" for a in absent]) or "OK")

    # 5. Per-force sections
    section_problems, citation_problems = [], []
    for key, label in FORCES.items():
        _, body = find(sections, lambda h: re.match(r"^\d\.", h) and force_key(h) == key)
        if body is None:
            continue
        joined = "\n".join(body)
        rm = re.search(r"\*\*Rating:\*\*\s*([1-5])/5\s*\((high|medium|low) confidence\)", joined, re.I)
        if not rm:
            section_problems.append(f"{label}: no '**Rating:** n/5 (<level> confidence)' line")
        elif key in table and (int(rm.group(1)), rm.group(2).lower()) != table[key]:
            section_problems.append(f"{label}: section says {rm.group(1)}/5 {rm.group(2)}, table says {table[key]}")
        for field in ("Drivers:", "Evidence:", "What would change it:"):
            if not re.search(rf"^- {re.escape(field)}", joined, re.M):
                section_problems.append(f"{label}: missing '- {field}' line")
        ev = re.search(r"^- Evidence:(.*?)(?=^- What would change it:|\Z)", joined, re.M | re.S)
        low = key in table and table[key][1] == "low"
        if ev and not CITATION_RE.search(ev.group(1)) and not low:
            citation_problems.append(f"{label}: no [source, date] citation in Evidence")
    add("Each force section has a Rating line matching the table, plus Drivers, Evidence and What would change it",
        not section_problems, "; ".join(section_problems) or "OK")
    add("Every force's Evidence cites at least one dated source, or the force is rated low confidence",
        not citation_problems, "; ".join(citation_problems) or "OK")

    # 6. Summary labels and consistency with the ratings
    _, summary = find(sections, lambda h: h.lower() == "summary")
    summary_text = "\n".join(summary or []).replace("**", "")
    attr = re.search(r"Industry attractiveness:\s*(Attractive|Mixed|Unattractive)\b", summary_text)
    pos = re.search(r"Company position:\s*(Advantaged|Neutral|Exposed)\b", summary_text)
    dom = re.search(r"Dominant force:\s*(.+)", summary_text)
    dom_ok = bool(dom and force_key(dom.group(1).split("—")[0].split(".")[0]))
    add("Summary gives attractiveness (Attractive/Mixed/Unattractive), position (Advantaged/Neutral/Exposed) "
        "and names one of the five forces as dominant",
        attr and pos and dom_ok,
        f"attractiveness={attr and attr.group(1)}, position={pos and pos.group(1)}, dominant force named={dom_ok}")

    ratings = [r for r, _ in table.values() if r]
    if attr and len(ratings) == 5:
        avg = sum(ratings) / 5
        expected = {"Attractive"} if avg < 2.5 else {"Unattractive"} if avg > 3.5 else {"Mixed"}
        if avg == 2.5:
            expected = {"Attractive", "Mixed"}
        if avg == 3.5:
            expected = {"Mixed", "Unattractive"}
        label = attr.group(1)
        # An override must be explained in the Summary or Force ratings section, not merely mentioned ("no override").
        near = summary_text + "\n" + "\n".join(table_body or [])
        overridden = re.search(r"(?<!no )(?<!without )overrid", near, re.I)
        consistent = label in expected or overridden
        if 5 in ratings and label == "Attractive":
            consistent = False
        add("Attractiveness label matches the average rating (<=2.5 Attractive, 2.5-3.5 Mixed, >=3.5 Unattractive) "
            "or the override is explained; never 'Attractive' with a force rated 5",
            consistent, f"average {avg:.1f} -> expected {sorted(expected)}, got {label}"
            + (" (override explained in text)" if label not in expected and overridden else ""))
    else:
        add("Attractiveness label matches the average rating", False, "could not read the label or all five ratings")

    # 7. Sources dated, stale data flagged
    _, sources = find(sections, lambda h: h.lower() == "sources")
    entries = [l for l in (sources or []) if l.startswith("- ")]
    undated = [e[2:60] for e in entries if not YEAR_RE.search(re.sub(r"https?://\S+", "", e)) and not UNDATED_RE.search(e)]
    add("Sources lists at least 3 entries, each with a date or marked 'undated'",
        len(entries) >= 3 and not undated, f"{len(entries)} entries; no date: {undated}" if undated else f"{len(entries)} entries, all dated")

    if asof:
        old = []
        for e in entries:
            years = [int(y.group(0)) for y in YEAR_RE.finditer(re.sub(r"https?://\S+", "", e))]
            if years and max(years) < asof.year - 2:
                old.append(e[2:50])
        add("Sources older than ~2 years are flagged as stale somewhere in the analysis",
            not old or re.search(r"\bstale\b", text, re.I), f"old sources: {old}" if old else "no sources older than 2 years")

    # 8. Gaps, peer comparison, leftovers
    _, gaps = find(sections, lambda h: h.lower() == "gaps")
    add("Gaps lists at least one specific unverified item", any(l.startswith("- ") for l in (gaps or [])),
        f"{sum(l.startswith('- ') for l in (gaps or []))} gap bullets")

    _, peers = find(sections, lambda h: h.lower().startswith("peer comparison"))
    if peers is not None:
        add("Peer comparison section, when present, contains a forces x companies table",
            any(l.startswith("|") for l in peers), "table found" if any(l.startswith("|") for l in peers) else "no table")

    left = [p for p in PLACEHOLDERS if p in text]
    add("No template placeholders left in the file", not left, f"found: {left}" if left else "none")
    return results


def report(path, results):
    failed = [r for r in results if not r["passed"]]
    out = [f"Five-forces eval for {os.path.basename(path)}: {len(results) - len(failed)}/{len(results)} checks passed"]
    for r in results:
        out.append(f"  [{'PASS' if r['passed'] else 'FAIL'}] {r['text']}" + ("" if r["passed"] else f"\n         -> {r['evidence']}"))
    return "\n".join(out), failed


def main():
    args = sys.argv[1:]
    if "--hook" in args:
        try:
            payload = json.load(sys.stdin)
        except ValueError:
            return 0
        path = (payload.get("tool_input") or {}).get("file_path") or (payload.get("tool_response") or {}).get("filePath") or ""
        if not OUTPUT_PATH_RE.search(path) or not os.path.isfile(path):
            return 0
        text, failed = report(path, check(path))
        if failed:
            print(text + "\n\nFix every FAIL above in the file before replying to the user "
                  "(the check reruns on each write).", file=sys.stderr)
            return 2
        print(json.dumps({"systemMessage": text.splitlines()[0],
                          "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}}))
        return 0

    if not args:
        print(__doc__)
        return 1
    path = args[0]
    results = check(path)
    if "--json" in args:
        print(json.dumps({"expectations": results}, indent=2))
    else:
        print(report(path, results)[0])
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
