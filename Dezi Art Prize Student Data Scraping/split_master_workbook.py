import argparse

from openpyxl import Workbook

from build_master_workbook import SOURCE_CITATIONS, read_csv_rows, write_sheet

# Same (sheet title, csv path, college label) list as build_master_workbook.py.
SOURCES = [
    ("RIT", "rit_students.csv", "RIT"),
    ("MCAD", "mcad_students.csv", "MCAD"),
    ("Cranbrook", "cranbrook_students.csv", "Cranbrook"),
    ("RISD", "risd_students.csv", "RISD"),
    ("Otis", "otis_students.csv", "Otis"),
    ("Parsons", "parsons_students.csv", "Parsons"),
    ("Temple-Tyler", "temple_students.csv", "Temple/Tyler"),
    ("VCU", "vcu_students.csv", "VCU"),
    ("Yale", "yale_students.csv", "Yale"),
    ("CMU", "cmu_students.csv", "CMU"),
    ("UW-Madison", "uw_madison_students.csv", "UW-Madison"),
    ("Ohio State", "ohio_state_students.csv", "Ohio State"),
    ("Pratt", "pratt_students.csv", "Pratt"),
    ("BU", "bu_students.csv", "BU"),
    ("SVA", "sva_students.csv", "SVA"),
    ("MICA", "mica_students.csv", "MICA"),
    ("CCA", "cca_students.csv", "CCA"),
    ("MassArt", "massart_students.csv", "MassArt"),
    ("U Michigan Stamps", "umich_students.csv", "U Michigan Stamps"),
    ("CalArts", "calarts_students.csv", "CalArts"),
    ("UCLA", "ucla_students.csv", "UCLA"),
    ("Columbia College Chicago", "columbia_students.csv", "Columbia College Chicago"),
    ("Iowa", "iowa_students.csv", "University of Iowa"),
    ("UW Art", "uw_art_students.csv", "University of Washington"),
    ("BGSU", "bgsu_students.csv", "BGSU"),
]

NO_EMAIL_VALUES = {"", "not found"}


def has_email(row):
    email = (row.get("email") or "").strip().lower()
    return email not in NO_EMAIL_VALUES


def main():
    parser = argparse.ArgumentParser(
        description="Split master_students.xlsx into with-email and no-email workbooks"
    )
    parser.add_argument("--with-email-out", default="master_students_with_email.xlsx")
    parser.add_argument("--no-email-out", default="master_students_no_email.xlsx")
    args = parser.parse_args()

    wb_with = Workbook()
    wb_with.remove(wb_with.active)
    wb_without = Workbook()
    wb_without.remove(wb_without.active)

    for sheet_title, csv_path, college_name in SOURCES:
        try:
            rows = read_csv_rows(csv_path)
        except FileNotFoundError:
            print(f"Skipping {sheet_title}: {csv_path} not found")
            continue

        with_email_rows = [r for r in rows if has_email(r)]
        no_email_rows = [r for r in rows if not has_email(r)]

        write_sheet(wb_with, sheet_title, with_email_rows, college_name)
        write_sheet(wb_without, sheet_title, no_email_rows, college_name)

        print(f"{sheet_title}: {len(with_email_rows)} with email, {len(no_email_rows)} without")

    wb_with.save(args.with_email_out)
    wb_without.save(args.no_email_out)

    print(f"\nSaved -> {args.with_email_out}")
    print(f"Saved -> {args.no_email_out}")


if __name__ == "__main__":
    main()
