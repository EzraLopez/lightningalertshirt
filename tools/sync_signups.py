#!/usr/bin/env python3
"""Sync lightningalertshirt.com waitlist signups into our own database.

The database is data/signups.csv (local only — it contains real people's
email addresses and the GitHub repo is public, so data/ is gitignored).

Sources: signup notification emails in the foku.assistant@gmail.com inbox.
Both eras are covered because both used the same subject line:
  - Netlify Forms era:  from formresponses@netlify.com (body: "Name:\\nX\\nEmail:\\n...")
  - FormSubmit era:     from submissions@formsubmit.co (body: markdown table "| name | X |")

Test submissions are excluded: any signup whose name contains "test"
(case-insensitive) plus a small explicit list of known test message IDs.

Dedupe: by Gmail message ID (each notification = one signup), so re-running
is safe and idempotent.

Usage:
    python3 tools/sync_signups.py [--db data/signups.csv]
Prints a summary: rows added, total signups, shirts per size, deduped emails
count. Exits non-zero if the Gmail CLI fails.
"""

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

GMAIL_CLI = "/opt/hatch/bin/hatch_gws_cli"
QUERY = 'subject:"New waitlist signup — lightningalertshirt.com"'

# Known test notifications that don't contain "test" in the name field.
EXCLUDE_MESSAGE_IDS = {
    "1a13cd364aff6b9b",  # "Ezraaaaa" — the user's own deleted test, Oct 14
}

FIELDS = ["received_at_utc", "name", "email", "size", "quantity", "source", "message_id"]


def gmail_json(args):
    out = subprocess.run(
        [GMAIL_CLI, "gmail", *args],
        capture_output=True, text=True, timeout=120,
    )
    if out.returncode != 0:
        sys.exit(f"gmail CLI failed: {out.stderr.strip() or out.stdout.strip()}")
    return json.loads(out.stdout)


def parse_netlify(body):
    def grab(label):
        m = re.search(rf"^{re.escape(label)}:\s*\n\s*(.+?)\s*$", body, re.M | re.I)
        return m.group(1).strip() if m else ""
    return {
        "name": grab("Name"),
        "email": grab("Email"),
        "size": grab("Shirt size"),
        "quantity": grab("Quantity"),
    }


def parse_formsubmit(body):
    def grab(key):
        # Case-sensitive: data rows use lowercase keys; the "| Name | Value |"
        # header row must not match.
        m = re.search(rf"^\|\s*{key}\s*\|\s*(.+?)\s*\|", body, re.M)
        return m.group(1).strip() if m else ""
    return {
        "name": grab("name"),
        "email": grab("email"),
        "size": grab("size"),
        "quantity": grab("quantity"),
    }


def is_test(row, message_id):
    if message_id in EXCLUDE_MESSAGE_IDS:
        return True
    return "test" in row["name"].lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(Path(__file__).resolve().parent.parent / "data" / "signups.csv"))
    args = ap.parse_args()
    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    existing = []
    seen_ids = set()
    if db_path.exists():
        with db_path.open(newline="") as f:
            for row in csv.DictReader(f):
                existing.append(row)
                seen_ids.add(row["message_id"])

    listing = gmail_json(["+triage", "--query", QUERY, "--max", "200", "--format", "json"])
    added, skipped_test, skipped_dup = [], 0, 0
    for msg in listing.get("messages", []):
        mid = msg["id"]
        if mid in seen_ids:
            skipped_dup += 1
            continue
        full = gmail_json(["+read", "--id", mid, "--format", "json"])
        body = full.get("body_text", "")
        sender = (full.get("from") or {}).get("email", "")
        if sender == "submissions@formsubmit.co":
            row, source = parse_formsubmit(body), "formsubmit"
        else:
            row, source = parse_netlify(body), "netlify"
        if not row["email"] or not row["name"]:
            print(f"WARNING: could not parse message {mid}; skipped", file=sys.stderr)
            continue
        if is_test(row, mid):
            skipped_test += 1
            continue
        row["received_at_utc"] = (full.get("message_sent_at") or {}).get("utc", "")
        row["source"] = source
        row["message_id"] = mid
        row["email"] = row["email"].lower()
        added.append(row)

    rows = sorted(existing + added, key=lambda r: r["received_at_utc"])
    with db_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})

    sizes = {}
    total_qty = 0
    for r in rows:
        q = int(r["quantity"] or 1)
        sizes[r["size"]] = sizes.get(r["size"], 0) + q
        total_qty += q
    emails = {r["email"] for r in rows}

    print(f"Database: {db_path}")
    print(f"Added {len(added)} new signup(s); skipped {skipped_test} test(s), {skipped_dup} already-synced.")
    print(f"Total signups: {len(rows)} people, {total_qty} shirts, {len(emails)} unique emails")
    print("Shirts per size: " + ", ".join(f"{s} x{n}" for s, n in sorted(sizes.items())))
    for r in added:
        print(f"  + {r['name']} <{r['email']}> size {r['size']} x{r['quantity']} ({r['source']}, {r['received_at_utc'][:10]})")


if __name__ == "__main__":
    main()
