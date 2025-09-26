#!/usr/bin/env python3
# scripts/generate_docs_index.py
"""
Generates:
 - docs/index.md (main index page linking to weekly reports)
 - docs/weekly-reports/index.md (list of weekly reports sorted by date)
Ensures docs/.nojekyll exists to bypass Jekyll processing.

File naming supported:
 - weekly-2025-09-01_to_2025-09-07.md
 - 2025-09-01-2025-09-07.md
 - before-15-sept-2025.md
If no valid date is parsed, the file's modification date is used.
"""

import os, re
from datetime import datetime
from dateutil import parser as dparser  # pip install python-dateutil

DOCS = "docs"
WEEKLY_DIR = os.path.join(DOCS, "weekly-reports")
os.makedirs(WEEKLY_DIR, exist_ok=True)

# collect .md files (ignore index.md itself)
files = [f for f in os.listdir(WEEKLY_DIR) if f.lower().endswith(".md") and f != "index.md"]

date_regex_iso = re.compile(r"(\d{4}-\d{2}-\d{2})")
# also support things like 15-sept-2025, sept-15-2025, 15_sept_2025
date_like = re.compile(r"(\d{1,2}[-_ ]?[A-Za-z]{3,}[-_ ]?\d{4})|([A-Za-z]{3,}[-_ ]?\d{1,2}[-_ ]?\d{4})")

def extract_date_from_name(fname):
    # 1) strict ISO format
    m = date_regex_iso.search(fname)
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y-%m-%d").date()
        except Exception:
            pass
    # 2) partial patterns like 15-sept-2025
    m2 = date_like.search(fname)
    if m2:
        try:
            return dparser.parse(m2.group(0), dayfirst=True, fuzzy=True).date()
        except Exception:
            pass
    # 3) fuzzy parse whole filename
    try:
        return dparser.parse(fname, dayfirst=True, fuzzy=True).date()
    except Exception:
        return None

def file_mtime_date(path):
    ts = os.path.getmtime(path)
    return datetime.fromtimestamp(ts).date()

# build list (filename, parsed_date)
pairs = []
for f in files:
    path = os.path.join(WEEKLY_DIR, f)
    d = extract_date_from_name(f)
    if d is None:
        d = file_mtime_date(path)
    pairs.append((f, d))

# sort newest first
pairs.sort(key=lambda x: (x[1] is None, x[1]), reverse=True)

# ensure .nojekyll exists
open(os.path.join(DOCS, ".nojekyll"), "a").close()

# generate docs/weekly-reports/index.md
lines = ["# Weekly Reports Index\n\n",
         "_This page lists all available weekly reports._\n\n"]
if not pairs:
    lines.append("No reports yet.\n")
else:
    for fname, dt in pairs:
        display = fname
        if dt:
            display = f"{dt.isoformat()} — {fname}"
        lines.append(f"- [{display}]({fname})\n")

weekly_index_path = os.path.join(WEEKLY_DIR, "index.md")
with open(weekly_index_path, "w", encoding="utf-8") as fh:
    fh.writelines(lines)

# generate docs/index.md (main page)
main_lines = ["# Thesis Diary — Weekly Reports\n\n",
              f"_Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}_\n\n",
              "## Browse\n\n",
              "- [Weekly Reports](/weekly-reports/)\n\n",
              "---\n\nClick above to see individual weekly reports.\n"]

with open(os.path.join(DOCS, "index.md"), "w", encoding="utf-8") as fh:
    fh.writelines(main_lines)

print("Generated:", weekly_index_path, "and", os.path.join(DOCS, "index.md"))

