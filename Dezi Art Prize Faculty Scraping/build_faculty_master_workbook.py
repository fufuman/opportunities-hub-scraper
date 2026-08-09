import argparse
import csv
import os

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

UNIFIED_COLUMNS = [
    "school_name",
    "faculty_name",
    "title",
    "department",
    "medium",
    "email",
    "email_type",
    "source_url",
    "date_extracted",
]

# One citation per school: where its faculty data was publicly listed, and any
# notable caveats about how medium/department was determined. Update this
# whenever a school's scraper is added or its source pages change.
SOURCE_CITATIONS = {
    "Temple/Tyler": {
        "name": "Temple University Tyler School of Art and Architecture - full "
                "directory (Staff/Faculty/Adjunct Faculty filter), 10 pages "
                "(source brief overclaimed 16 pages; page controls confirm 10). "
                "JS-rendered - required crawl4ai, not a plain fetch.",
        "url": "https://tyler.temple.edu/directory?profile-type%5Bstaff%5D=staff&"
               "profile-type%5Bfaculty%5D=faculty&profile-type%5Badjunct_faculty%5D="
               "adjunct_faculty&page=0 (through page=9)",
        "accessed": "2026-08-08",
        "country": "United States",
        "city": "Philadelphia, PA",
    },
    "Ohio State": {
        "name": "Ohio State University Department of Art - /people directory "
                "(Chair/Faculty/Associated Faculty/Emeritus Faculty categories only, "
                "Staff and Graduate Students excluded) cross-referenced with each "
                "person's individual profile page bio text for medium/discipline, "
                "since the directory listing itself has no per-person area label "
                "(contrary to the research brief) and the /areas/<medium> pages have "
                "no faculty roster at all (descriptive copy only).",
        "url": "https://art.osu.edu/people (plus 61 individual /people/<id> profile pages)",
        "accessed": "2026-08-08",
        "country": "United States",
        "city": "Columbus, OH",
    },
    "UGA": {
        "name": "University of Georgia, Lamar Dodd School of Art - full directory, "
                "10 pages, medium classified from the 'Academic Area' field shown "
                "directly on each person's card.",
        "url": "https://art.uga.edu/directory/ (page/2/ through page/10/)",
        "accessed": "2026-08-09",
        "country": "United States",
        "city": "Athens, GA",
    },
    "University of Iowa": {
        "name": "University of Iowa, School of Art, Art History and Design - "
                "/people/faculty directory, 2 pages, medium classified from the "
                "Title/Position field(s) shown directly on each person's card "
                "(e.g. 'Professor of Sculpture & Intermedia').",
        "url": "https://art.uiowa.edu/people/faculty (and ?page=1)",
        "accessed": "2026-08-09",
        "country": "United States",
        "city": "Iowa City, IA",
    },
    "UT Austin": {
        "name": "University of Texas at Austin, Department of Art and Art History - "
                "/about/who-we-are/people directory (Faculty, Staff & Students "
                "combined listing), 5 pages, medium classified from the "
                "'Designation' field (e.g. 'Studio Art (Painting & Drawing)'). "
                "Emails were NOT obfuscated with spaces as the research brief "
                "claimed - they render plainly, only wrapped with <wbr> tags for "
                "line-breaking, which were stripped.",
        "url": "https://art.utexas.edu/about/who-we-are/people (and ?page=1 through ?page=4)",
        "accessed": "2026-08-09",
        "country": "United States",
        "city": "Austin, TX",
    },
}


def read_csv_rows(csv_path):
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_sheet(wb, sheet_title, rows, school_label):
    ws = wb.create_sheet(title=sheet_title[:31])

    citation = SOURCE_CITATIONS.get(school_label)
    header_row_offset = 0
    if citation:
        ws.append([f"Country: {citation['country']}"])
        ws.append([f"City: {citation['city']}"])
        ws.append([f"Source: {citation['name']}"])
        ws.append([f"URL: {citation['url']}"])
        ws.append([f"Accessed: {citation['accessed']}"])
        for r in range(1, 6):
            ws.cell(row=r, column=1).font = Font(italic=True, size=9, color="666666")
        ws.append([])
        header_row_offset = 6

    header_row_num = header_row_offset + 1
    ws.append(UNIFIED_COLUMNS)
    for cell in ws[header_row_num]:
        cell.font = Font(bold=True)

    for row in rows:
        ws.append([row.get(col, "") for col in UNIFIED_COLUMNS])

    last_row = ws.max_row
    if last_row <= header_row_num:
        last_row = header_row_num + 1
    first_data_row = header_row_num + 1

    ws.freeze_panes = f"A{first_data_row}"
    ws.auto_filter.ref = f"A{header_row_num}:{get_column_letter(len(UNIFIED_COLUMNS))}{last_row}"

    widths = {"school_name": 34, "faculty_name": 22, "title": 30, "department": 22,
              "medium": 20, "email": 30, "email_type": 14, "source_url": 40,
              "date_extracted": 16}
    for i, col in enumerate(UNIFIED_COLUMNS, start=1):
        ws.column_dimensions[get_column_letter(i)].width = widths.get(col, 18)

    return ws


def main():
    parser = argparse.ArgumentParser(description="Build/update the master faculty outreach workbook")
    parser.add_argument("--out", default="master_faculty.xlsx")
    parser.add_argument("--temple-csv", default="temple_faculty.csv")
    parser.add_argument("--ohio-state-csv", default="ohio_state_faculty.csv")
    parser.add_argument("--uga-csv", default="uga_faculty.csv")
    parser.add_argument("--iowa-csv", default="iowa_faculty.csv")
    parser.add_argument("--ut-austin-csv", default="ut_austin_faculty.csv")
    args = parser.parse_args()

    wb = Workbook()
    wb.remove(wb.active)

    # (sheet title, csv path, school label). Add a new tuple here for each
    # additional school scraped; the CSV just needs the unified columns.
    sources = [
        ("Temple-Tyler", args.temple_csv, "Temple/Tyler"),
        ("Ohio State", args.ohio_state_csv, "Ohio State"),
        ("UGA", args.uga_csv, "UGA"),
        ("Iowa", args.iowa_csv, "University of Iowa"),
        ("UT Austin", args.ut_austin_csv, "UT Austin"),
    ]

    for sheet_title, csv_path, school_label in sources:
        if not os.path.exists(csv_path):
            print(f"Skipping {sheet_title}: {csv_path} not found")
            continue
        rows = read_csv_rows(csv_path)
        write_sheet(wb, sheet_title, rows, school_label)
        print(f"{sheet_title}: {len(rows)} faculty -> sheet '{sheet_title[:31]}'")

    wb.save(args.out)
    print(f"\nSaved master faculty workbook -> {args.out}")


if __name__ == "__main__":
    main()
