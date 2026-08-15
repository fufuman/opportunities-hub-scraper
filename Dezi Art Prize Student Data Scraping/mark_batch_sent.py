"""
Stamp sent_to_nitya with today's date on every row that build_nitya_batch.py
would currently include in a new batch (non-blank email, blank sent_to_nitya).

Run this ONLY after confirming the batch file was actually sent to Nitya -
it's a deliberate second step, separate from generating the batch, so a
batch that was generated but not yet sent doesn't get silently marked as
delivered. If you run build_nitya_batch.py again after this, it will
correctly report "nothing new" until more emails are added.
"""
import argparse
import csv
from datetime import date

from build_master_workbook import SOURCES

NO_EMAIL_VALUES = {"", "not found"}
FIELDNAMES = ["name", "email", "major", "graduation_year", "portfolio_url",
              "college", "notes", "sent_to_nitya"]


def has_email(row):
    email = (row.get("email") or "").strip().lower()
    return email not in NO_EMAIL_VALUES


def is_unsent(row):
    return not (row.get("sent_to_nitya") or "").strip()


def main():
    parser = argparse.ArgumentParser(
        description="Mark all currently-unsent emails as sent to Nitya as of today"
    )
    parser.add_argument("--date", default=date.today().isoformat(),
                         help="sent date to stamp (default: today, YYYY-MM-DD)")
    parser.add_argument("--yes", action="store_true",
                         help="skip the confirmation prompt")
    args = parser.parse_args()

    # dry run first so the user sees exactly what will be stamped
    to_mark = []
    for sheet_title, csv_path, college_name in SOURCES:
        try:
            with open(csv_path, "r", newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
        except FileNotFoundError:
            continue
        count = sum(1 for r in rows if has_email(r) and is_unsent(r))
        if count:
            to_mark.append((sheet_title, csv_path, count))

    if not to_mark:
        print("Nothing to mark - no unsent emails found.")
        return

    print(f"About to stamp sent_to_nitya = {args.date} on:")
    total = 0
    for sheet_title, _, count in to_mark:
        print(f"  {sheet_title}: {count} rows")
        total += count
    print(f"Total: {total} rows")

    if not args.yes:
        confirm = input("\nProceed? (y/N): ").strip().lower()
        if confirm != "y":
            print("Aborted, no changes made.")
            return

    for sheet_title, csv_path, _ in to_mark:
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            if has_email(row) and is_unsent(row):
                row["sent_to_nitya"] = args.date
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in FIELDNAMES})

    print(f"\nMarked {total} rows as sent_to_nitya = {args.date}.")


if __name__ == "__main__":
    main()
