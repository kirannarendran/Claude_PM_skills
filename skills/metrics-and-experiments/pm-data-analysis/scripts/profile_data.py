#!/usr/bin/env python3
"""Profile every table in a dataset: shape, keys, nulls, dates, categories, and join columns.

Usage:
  python3 -I profile_data.py <file.csv|file.xlsx|folder> [--max-rows N]

Reads CSV, TSV and Excel files (Excel needs openpyxl). For a folder, profiles every such file
in it and then lists columns shared across tables with their value overlap, which suggests joins.
"""
import argparse
import os
import sys

import pandas as pd

EXTS = (".csv", ".tsv", ".xlsx", ".xls")


def load(path, max_rows):
    if path.endswith((".xlsx", ".xls")):
        return pd.read_excel(path, nrows=max_rows)
    return pd.read_csv(path, sep="\t" if path.endswith(".tsv") else ",", nrows=max_rows, low_memory=False)


def as_dates(s):
    if s.dtype != object or not s.astype(str).str.match(r"^\d{4}-\d{2}-\d{2}").mean() > 0.9:
        return None
    d = pd.to_datetime(s, errors="coerce")
    return d if d.notna().mean() > 0.9 else None


def profile(name, df):
    print(f"\n{'=' * 80}\n{name}: {len(df):,} rows × {df.shape[1]} columns")
    keys = [c for c in df.columns if df[c].notna().all() and df[c].is_unique]
    print("Unique, non-null columns (candidate keys):", ", ".join(map(str, keys)) or "none — check for a composite key")
    rows = []
    for c in df.columns:
        s = df[c]
        nulls = s.isna().mean() * 100
        n = s.nunique(dropna=True)
        d = as_dates(s)
        if d is not None:
            note = f"dates {d.min().date()} → {d.max().date()}"
        elif pd.api.types.is_numeric_dtype(s) and n > 20:
            note = f"min {s.min():,.2f} · median {s.median():,.2f} · max {s.max():,.2f}"
            if pd.api.types.is_float_dtype(s):
                frac = (s.dropna() * 100 % 1).round(6)
                if ((frac > 1e-6) & (frac < 1 - 1e-6)).mean() > 0.05:
                    note += " · float noise, round for display"
            if (s < 0).any():
                note += f" · {(s < 0).mean() * 100:.1f}% negative"
        elif n <= 30:
            vc = s.value_counts(dropna=True)
            note = "; ".join(f"{k} {v / len(s) * 100:.1f}%" for k, v in vc.head(8).items())
            if n > 8:
                note += f"; … ({n} values)"
        else:
            note = f"{n:,} distinct · e.g. {', '.join(map(str, s.dropna().unique()[:3]))}"
        rows.append((str(c), str(s.dtype), f"{nulls:.1f}%" if nulls else "", note))
    w = max(len(r[0]) for r in rows)
    for c, t, nl, note in rows:
        print(f"  {c:<{w}}  {t:<8} {nl:>6}  {note}")
    dup = df.duplicated().sum()
    if dup:
        print(f"  ! {dup:,} fully duplicated rows")


def joins(tables):
    print(f"\n{'=' * 80}\nShared columns across tables (possible joins)")
    names = list(tables)
    found = False
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            for c in set(tables[a].columns) & set(tables[b].columns):
                va, vb = set(tables[a][c].dropna().unique()), set(tables[b][c].dropna().unique())
                if not va or not vb or len(va) < 10:
                    continue
                found = True
                both = len(va & vb)
                print(f"  {c}: {a} ({len(va):,} values) ↔ {b} ({len(vb):,}) · {both:,} shared"
                      f" · {len(va - vb):,} only in {a} · {len(vb - va):,} only in {b}")
    if not found:
        print("  none found by column name — look for differently named keys")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--max-rows", type=int, default=None, help="read only the first N rows of each file")
    a = ap.parse_args()
    if os.path.isdir(a.path):
        files = sorted(os.path.join(a.path, f) for f in os.listdir(a.path) if f.lower().endswith(EXTS))
    else:
        files = [a.path]
    if not files:
        print("No CSV, TSV or Excel files found.", file=sys.stderr)
        return 1
    tables = {}
    for f in files:
        name = os.path.basename(f)
        try:
            tables[name] = load(f, a.max_rows)
        except Exception as e:  # keep going so one bad file doesn't hide the rest
            print(f"\n{name}: could not read ({e})")
            continue
        profile(name, tables[name])
    if len(tables) > 1:
        joins(tables)
    return 0


if __name__ == "__main__":
    sys.exit(main())
