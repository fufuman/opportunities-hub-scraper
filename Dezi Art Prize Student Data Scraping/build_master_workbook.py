import argparse
import csv
import os

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

UNIFIED_COLUMNS = [
    "name",
    "email",
    "major",
    "graduation_year",
    "portfolio_url",
    "college",
    "contacted",
    "response",
    "notes",
]

RESPONSE_OPTIONS = "No response,Interested,Not interested,Bounced,Follow-up needed"

# One citation per school: where its data was publicly listed, so outreach can
# credibly point to the exact source. Update this whenever a school's scraper
# is added or changes source pages. List multiple sources semicolon-separated
# if a school's data was aggregated from more than one page (e.g. MCAD).
SOURCE_CITATIONS = {
    "RIT": {
        "name": "RIT Creativity Portal",
        "url": "https://creativity.cad.rit.edu/",
        "accessed": "2026-07-31",
    },
    "MCAD": {
        "name": "MCAD Spring 2022 Commencement Page; MCAD Spring 2023 Commencement Ceremony Page",
        "url": "https://www.mcad.edu/events/spring-2022-commencement; "
               "https://www.mcad.edu/events/spring-2023-commencement-ceremony",
        "accessed": "2026-07-31",
    },
    "Cranbrook": {
        "name": "Cranbrook Academy of Art Alumni Directory — 2026 only, filtered to "
                "Painting/Photography/Fiber/Sculpture/Ceramics/Graphic Design/2D/3D/4D "
                "Design (Print Media, Metalsmithing, Architecture, Industrial Design "
                "excluded per user request)",
        "url": "https://cranbrookart.edu/alumni/directory/",
        "accessed": "2026-07-31",
    },
    "RISD": {
        "name": "RISD Grad Show 2026 Student Index",
        "url": "https://publications.risd.edu/grad-show-2026/student-index",
        "accessed": "2026-07-31",
    },
    "Otis": {
        "name": "Otis College 2026 Annual Exhibition — All Students",
        "url": "https://www.otis.edu/about/our-work/annual-exhibition/2026/all-students.html",
        "accessed": "2026-07-31",
    },
    "Parsons": {
        "name": "Parsons Fine Arts Thesis pages — 2025 BFA Thesis, 2025 MFA Thesis, "
                "2026 MFA Thesis",
        "url": "https://amt.parsons.edu/finearts/2025-bfa-thesis/; "
               "https://amt.parsons.edu/finearts/2025-mfa-thesis/; "
               "https://amt.parsons.edu/finearts/2026-mfa-thesis/",
        "accessed": "2026-08-01",
    },
    "Temple/Tyler": {
        "name": "Temple University Tyler School of Art — 2025 MFA Thesis Exhibitions page "
                "(names only, from exhibition schedule text — no email/major/portfolio "
                "published on source page)",
        "url": "https://tyler.temple.edu/2025-mfa-thesis-exhibitions-rewoven-collective-stories",
        "accessed": "2026-08-01",
    },
    "VCU": {
        "name": "VCU ICA (Institute for Contemporary Art) 2025 MFA Thesis Exhibition page "
                "(names only, from artwork photo caption credits — likely incomplete vs. "
                "full graduating cohort)",
        "url": "https://icavcu.org/exhibitions/2025-mfa-thesis/",
        "accessed": "2026-08-01",
    },
    "Yale": {
        "name": "Yale School of Art exhibition pages — Painting/Printmaking, Sculpture, "
                "Photography, and Graphic Design MFA Thesis, 2025 and 2026 (names only, "
                "from exhibition 'Featuring' text — no email/portfolio published)",
        "url": "https://art.yale.edu/exhibitions/spring-2025-painting-thesis (and 7 "
               "corresponding spring-{2025,2026}-{painting,sculpture,photography,"
               "graphic-design}-thesis pages)",
        "accessed": "2026-08-01",
    },
    "CMU": {
        "name": "Carnegie Mellon School of Art — MFA Students directory + per-student "
                "profile pages",
        "url": "https://art.cmu.edu/mfa/students/",
        "accessed": "2026-08-01",
    },
    "UW-Madison": {
        "name": "UW-Madison Department of Art — Graduate Students directory",
        "url": "https://art.wisc.edu/people/graduate-students/",
        "accessed": "2026-08-01",
    },
    "Ohio State": {
        "name": "Ohio State Department of Art — 2025 'Desire Lines' MFA Thesis Exhibition "
                "page (clean list) and 2026 'Waiting for the Light to Change' MFA Thesis "
                "Exhibition page (names UNVERIFIED — source lists them as ambiguous "
                "run-on text, reconstructed best-effort, see notes column)",
        "url": "https://art.osu.edu/events/mfa-thesis-exhibition-desire-lines; "
               "https://uas.osu.edu/events/waiting-light-change",
        "accessed": "2026-08-01",
    },
}


def read_csv_rows(csv_path):
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_sheet(wb, sheet_title, rows, college_name):
    ws = wb.create_sheet(title=sheet_title[:31])

    citation = SOURCE_CITATIONS.get(college_name)
    header_row_offset = 0
    if citation:
        ws.append([f"Source: {citation['name']}"])
        ws.append([f"URL: {citation['url']}"])
        ws.append([f"Accessed: {citation['accessed']}"])
        for r in range(1, 4):
            ws.cell(row=r, column=1).font = Font(italic=True, size=9, color="666666")
        ws.append([])
        header_row_offset = 4

    header_row_num = header_row_offset + 1
    ws.append(UNIFIED_COLUMNS)
    for cell in ws[header_row_num]:
        cell.font = Font(bold=True)

    for row in rows:
        ws.append([
            row.get("name", ""),
            row.get("email", ""),
            row.get("major", ""),
            row.get("graduation_year", ""),
            row.get("portfolio_url", ""),
            row.get("college", college_name),
            row.get("contacted", "No") or "No",
            row.get("response", ""),
            row.get("notes", ""),
        ])

    last_row = ws.max_row
    if last_row <= header_row_num:
        last_row = header_row_num + 1
    first_data_row = header_row_num + 1

    contacted_col = UNIFIED_COLUMNS.index("contacted") + 1
    contacted_dv = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True, showDropDown=False)
    contacted_dv.add(f"{get_column_letter(contacted_col)}{first_data_row}:{get_column_letter(contacted_col)}{last_row}")
    ws.add_data_validation(contacted_dv)

    response_col = UNIFIED_COLUMNS.index("response") + 1
    response_dv = DataValidation(type="list", formula1=f'"{RESPONSE_OPTIONS}"', allow_blank=True, showDropDown=False)
    response_dv.add(f"{get_column_letter(response_col)}{first_data_row}:{get_column_letter(response_col)}{last_row}")
    ws.add_data_validation(response_dv)

    ws.freeze_panes = f"A{first_data_row}"
    ws.auto_filter.ref = f"A{header_row_num}:{get_column_letter(len(UNIFIED_COLUMNS))}{last_row}"

    widths = {"name": 24, "email": 28, "major": 26, "graduation_year": 16,
              "portfolio_url": 36, "college": 14, "contacted": 12, "response": 18, "notes": 40}
    for i, col in enumerate(UNIFIED_COLUMNS, start=1):
        ws.column_dimensions[get_column_letter(i)].width = widths.get(col, 18)

    return ws


def main():
    parser = argparse.ArgumentParser(description="Build/update the master student outreach workbook")
    parser.add_argument("--out", default="master_students.xlsx")
    parser.add_argument("--rit-csv", default="rit_students.csv")
    parser.add_argument("--mcad-csv", default="mcad_students.csv")
    parser.add_argument("--cranbrook-csv", default="cranbrook_students.csv")
    parser.add_argument("--risd-csv", default="risd_students.csv")
    parser.add_argument("--otis-csv", default="otis_students.csv")
    parser.add_argument("--parsons-csv", default="parsons_students.csv")
    parser.add_argument("--temple-csv", default="temple_students.csv")
    parser.add_argument("--vcu-csv", default="vcu_students.csv")
    parser.add_argument("--yale-csv", default="yale_students.csv")
    parser.add_argument("--cmu-csv", default="cmu_students.csv")
    parser.add_argument("--uw-madison-csv", default="uw_madison_students.csv")
    parser.add_argument("--ohio-state-csv", default="ohio_state_students.csv")
    args = parser.parse_args()

    wb = Workbook()
    wb.remove(wb.active)

    # (sheet title, csv path, college label). Add a new tuple here for each
    # additional school scraped; the CSV just needs the unified columns.
    sources = [
        ("RIT", args.rit_csv, "RIT"),
        ("MCAD", args.mcad_csv, "MCAD"),
        ("Cranbrook", args.cranbrook_csv, "Cranbrook"),
        ("RISD", args.risd_csv, "RISD"),
        ("Otis", args.otis_csv, "Otis"),
        ("Parsons", args.parsons_csv, "Parsons"),
        ("Temple-Tyler", args.temple_csv, "Temple/Tyler"),
        ("VCU", args.vcu_csv, "VCU"),
        ("Yale", args.yale_csv, "Yale"),
        ("CMU", args.cmu_csv, "CMU"),
        ("UW-Madison", args.uw_madison_csv, "UW-Madison"),
        ("Ohio State", args.ohio_state_csv, "Ohio State"),
    ]

    for sheet_title, csv_path, college_name in sources:
        if not os.path.exists(csv_path):
            print(f"Skipping {sheet_title}: {csv_path} not found")
            continue
        rows = read_csv_rows(csv_path)
        write_sheet(wb, sheet_title, rows, college_name)
        print(f"{sheet_title}: {len(rows)} students -> sheet '{sheet_title[:31]}'")

    wb.save(args.out)
    print(f"\nSaved master workbook -> {args.out}")


if __name__ == "__main__":
    main()
