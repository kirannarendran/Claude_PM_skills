#!/usr/bin/env python3
"""Compare every low-cardinality column's groups to the overall figure, and flag which ones differ.

Usage:
  python3 -I segment_scan.py <file.csv> --value <numeric column> [--value ...]
      [--flag <column>=<value> ...] [--where <column>=<value>] [--max-groups 30]
      [--min-size 200] [--threshold 5] [--z 3] [--quiet]

For each candidate column (2..max-groups distinct values) it prints, per group, the row count, the
mean of each --value, and the rate of each --flag. It then ranks columns by how much their groups
differ. A measure counts as a real difference only when both:
  - the spread (highest minus lowest group, among groups of at least --min-size rows) is at least
    --threshold percent of the overall figure, and
  - some group sits at least --z standard errors from the overall figure, so chance alone is an
    unlikely explanation.
Columns with no such measure are marked FLAT. Ignore columns that are part of a flag's own
definition (e.g. return_reason when flagging returns): they differ by construction.

Example:
  python3 -I segment_scan.py orders.csv --value net_sales --value profit_margin_percentage \
      --flag order_status=Returned --flag order_status=Cancelled --where order_status!=Pending
"""
import argparse
import sys

import pandas as pd


def parse_pair(text):
    for op in ("!=", "="):
        if op in text:
            col, val = text.split(op, 1)
            return col.strip(), op, val.strip()
    raise SystemExit(f"Expected column=value or column!=value, got: {text}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--value", action="append", default=[], help="numeric column to average per group")
    ap.add_argument("--flag", action="append", default=[], help="column=value whose rate to compare per group")
    ap.add_argument("--where", action="append", default=[], help="row filter, column=value or column!=value")
    ap.add_argument("--max-groups", type=int, default=30)
    ap.add_argument("--min-size", type=int, default=200, help="ignore smaller groups when measuring spread")
    ap.add_argument("--threshold", type=float, default=5.0, help="minimum spread, %% of the overall figure")
    ap.add_argument("--z", type=float, default=3.0, help="minimum standard errors from overall for a real difference")
    ap.add_argument("--quiet", action="store_true", help="print only the ranking, not each column's groups")
    a = ap.parse_args()
    if not a.value and not a.flag:
        ap.error("give at least one --value or --flag")

    df = pd.read_csv(a.csv, low_memory=False)
    for w in a.where:
        col, op, val = parse_pair(w)
        keep = df[col].astype(str) == val
        df = df[keep if op == "=" else ~keep]
    measures = {}
    for v in a.value:
        measures[f"mean {v}"] = pd.to_numeric(df[v], errors="coerce")
    for f in a.flag:
        col, op, val = parse_pair(f)
        hit = df[col].astype(str) == val
        measures[f"% {col}={val}"] = (hit if op == "=" else ~hit).astype(float) * 100
    m = pd.DataFrame(measures)
    used = {v for v in a.value} | {parse_pair(f)[0] for f in a.flag}
    cands = [c for c in df.columns if c not in used and 2 <= df[c].nunique() <= a.max_groups]

    print(f"{len(df):,} rows after filters · overall: " +
          " · ".join(f"{k} {m[k].mean():,.2f}" for k in m))
    ranking = []
    for c in cands:
        key = df[c].astype(str).where(df[c].notna(), "(blank)")
        g = m.groupby(key)
        t = g.mean()
        t.insert(0, "rows", g.size())
        found = {}
        for k in m:
            overall = m[k].mean()
            stats = pd.DataFrame({"mean": g[k].mean(), "sd": g[k].std(), "n": g[k].count()})
            stats = stats[stats.n >= a.min_size]
            if len(stats) < 2 or not overall:
                continue
            spread = (stats["mean"].max() - stats["mean"].min()) / abs(overall) * 100
            se = (stats.sd / stats.n ** 0.5).replace(0, float("nan"))
            z = ((stats["mean"] - overall) / se).abs().max()
            z = 0.0 if pd.isna(z) else z
            found[k] = (spread, z, spread >= a.threshold and z >= a.z)
        real = [k for k, v in found.items() if v[2]]
        score = max((found[k][0] for k in real), default=0.0)
        ranking.append((len(real) > 0, score, c, found))
        if not a.quiet:
            label = "FLAT" if not real else "differs on: " + ", ".join(real)
            print(f"\n=== {c} ({label})")
            print(t.sort_values("rows", ascending=False).round(2).to_string())

    print(f"\n{'=' * 80}\nColumns ranked by real differences: spread % of overall (z = largest standard-error gap)")
    print(f"FLAT = no measure with spread >= {a.threshold:g}% and z >= {a.z:g}; * marks the measures that pass")
    for has_real, score, c, found in sorted(ranking, key=lambda r: (r[0], r[1]), reverse=True):
        detail = ", ".join(f"{'*' if ok else ''}{k} {sp:.1f}% (z {z:.1f})" for k, (sp, z, ok) in found.items())
        print(f"  {'    ' if has_real else 'FLAT'}  {c:<28} {detail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
