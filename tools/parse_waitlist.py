#!/usr/bin/env python3
"""Parse a waitlist CSV export into production + outreach numbers.

Usage:
    python3 parse_waitlist.py waitlist-export.csv [--out-dir out]

Input: a CSV exported from the form host (Netlify Forms export works
as-is). Expected columns (case-insensitive, extra columns ignored):
    name, email, size, quantity   (+ optional created_at / date)

Outputs (printed, and written when --out-dir is given):
    * Total signups and total shirts requested
    * Shirts needed per size (XS..3XL, in size order) — the print-run table
    * Signups per size (people, regardless of quantity)
    * emails.txt  — deduplicated, lowercased emails, one per line,
      ready to paste/import for the Shopify launch email
    * summary.csv — the per-size totals as a spreadsheet-friendly file

No third-party dependencies; stdlib only.
"""
import argparse
import csv
import os
import sys
from collections import Counter, OrderedDict

SIZES = ["XS", "S", "M", "L", "XL", "2XL", "3XL"]


def _norm_size(raw):
    s = (raw or "").strip().upper().replace(" ", "")
    aliases = {"XXL": "2XL", "XXXL": "3XL", "2X": "2XL", "3X": "3XL"}
    return aliases.get(s, s)


def _find(row, *names):
    lower = {k.strip().lower(): v for k, v in row.items() if k}
    for n in names:
        if n in lower and str(lower[n]).strip():
            return str(lower[n]).strip()
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--out-dir", default="")
    args = ap.parse_args()

    shirts_per_size = OrderedDict((s, 0) for s in SIZES)
    people_per_size = Counter()
    unknown_sizes = Counter()
    emails = []
    seen = set()
    rows = valid = skipped = 0

    with open(args.csv_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rows += 1
            # Honeypot: a filled "website" field means a bot — drop the row.
            if _find(row, "website"):
                skipped += 1
                continue
            email = _find(row, "email", "email address").lower()
            size = _norm_size(_find(row, "size", "shirt size"))
            try:
                qty = int(float(_find(row, "quantity", "qty") or 1))
            except ValueError:
                qty = 1
            qty = max(qty, 0)
            if email and email not in seen:
                seen.add(email)
                emails.append(email)
            if size in shirts_per_size:
                shirts_per_size[size] += qty
                people_per_size[size] += 1
                valid += 1
            elif size:
                unknown_sizes[size] += qty

    total_shirts = sum(shirts_per_size.values()) + sum(unknown_sizes.values())
    print(f"Rows read:            {rows}  (bot/honeypot skipped: {skipped})")
    print(f"Unique emails:        {len(emails)}")
    print(f"Total shirts wanted:  {total_shirts}")
    print("\nShirts needed per size (print run):")
    for s in SIZES:
        print(f"  {s:<4} {shirts_per_size[s]:>4} shirts   ({people_per_size[s]} people)")
    for s, n in unknown_sizes.items():
        print(f"  {s:<4} {n:>4} shirts   (unrecognized size label)")

    if args.out_dir:
        os.makedirs(args.out_dir, exist_ok=True)
        with open(os.path.join(args.out_dir, "emails.txt"), "w") as f:
            f.write("\n".join(emails) + "\n")
        with open(os.path.join(args.out_dir, "summary.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["size", "shirts", "people"])
            for s in SIZES:
                w.writerow([s, shirts_per_size[s], people_per_size[s]])
            w.writerow(["TOTAL", total_shirts, valid])
        print(f"\nWrote {args.out_dir}/emails.txt and {args.out_dir}/summary.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
