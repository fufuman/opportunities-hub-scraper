"""
Generate a small batch workbook of only the student rows Nitya hasn't
received yet: any row with a non-blank email where sent_to_nitya is blank.

This does NOT mark anything as sent - that's a separate, explicit step
(mark_batch_sent.py), run only after the batch has actually been shared.
Regenerating this script is always safe; it never mutates the CSVs.
"""
import argparse
from datetime import date

from openpyxl import Workbook

from build_master_workbook import SOURCES, read_csv_rows, write_sheet

NO_EMAIL_VALUES = {"", "not found"}


def has_email(row):
    email = (row.get("email") or "").strip().lower()
    return email not in NO_EMAIL_VALUES


def is_unsent(row):
    return not (row.get("sent_to_nitya") or "").strip()


def main():
    parser = argparse.ArgumentParser(
        description="Build a batch workbook of new-since-last-batch student emails for Nitya"
    )
    parser.add_argument(
        "--out",
        default=f"nitya_batch_{date.today().isoformat()}.xlsx",
        help="output path (default: nitya_batch_<today>.xlsx)",
    )
    args = parser.parse_args()

    wb = Workbook()
    wb.remove(wb.active)

    total_new = 0
    for sheet_title, csv_path, college_name in SOURCES:
        try:
            rows = read_csv_rows(csv_path)
        except FileNotFoundError:
            continue

        new_rows = [r for r in rows if has_email(r) and is_unsent(r)]
        if not new_rows:
            continue

        write_sheet(wb, sheet_title, new_rows, college_name)
        print(f"{sheet_title}: {len(new_rows)} new")
        total_new += len(new_rows)

    if total_new == 0:
        print("\nNo new emails since the last batch - nothing to send.")
        return

    wb.save(args.out)
    print(f"\nTotal new rows in this batch: {total_new}")
    print(f"Saved -> {args.out}")
    print("\nNext steps:")
    print(f"  1. Review {args.out} and send it to Nitya.")
    print(f"  2. Once confirmed sent, run: ../.venv_crawl4ai/Scripts/python.exe mark_batch_sent.py")


if __name__ == "__main__":
    main()
