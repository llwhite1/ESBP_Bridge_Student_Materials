#!/usr/bin/env python3
"""Validate the public/private boundary and live release state of the student repo."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest_student_access.json"
NOTEBOOK_MANIFEST = ROOT / "notebooks/STUDENT_NOTEBOOK_RELEASE_MANIFEST_07202026_v5.json"
SCHEDULE = ROOT / "release_schedule/bridge_student_release_schedule_20260720_20260728.json"
LEDGER = ROOT / "release_schedule/release_ledger.json"
JSON_REPORT = ROOT / "REPOSITORY_HYGIENE.json"
MD_REPORT = ROOT / "REPOSITORY_HYGIENE.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def markdown_links(path: Path) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8"))


def source_text(cell: dict) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else str(source)


def validate() -> dict:
    failures: list[str] = []
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    notebooks = json.loads(NOTEBOOK_MANIFEST.read_text(encoding="utf-8"))
    schedule = json.loads(SCHEDULE.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    completed = set(ledger.get("completed_release_ids", []))

    forbidden_sources = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in {".tex", ".zip"}
    ]
    if forbidden_sources:
        failures.append(f"TeX/ZIP source artifacts are public: {forbidden_sources}")

    exam_files = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file()
        and (
            "exam1" in path.name.lower()
            or "exam2" in path.name.lower()
            or "day09_exam1" in path.relative_to(ROOT).as_posix().lower()
            and path.name != "README.md"
            or "day17_exam2" in path.relative_to(ROOT).as_posix().lower()
            and path.name != "README.md"
        )
    ]
    if exam_files:
        failures.append(f"Exam-boundary artifacts are public: {exam_files}")

    if notebooks.get("status") != "PASS" or notebooks.get("submission_type") != "single_ipynb":
        failures.append("notebook release manifest is not PASS/single-ipynb")
    for record in notebooks.get("records", []):
        path = ROOT / record["path"]
        if not path.is_file() or sha256(path) != record["sha256"]:
            failures.append(f"Notebook missing or hash drift: {record['path']}")
            continue
        notebook = json.loads(path.read_text(encoding="utf-8"))
        code_cells = [cell for cell in notebook.get("cells", []) if cell.get("cell_type") == "code"]
        code = "\n".join(source_text(cell) for cell in code_cells).lower()
        for forbidden in ("%%writefile", "shutil.make_archive", "load_student_module"):
            if forbidden.lower() in code:
                failures.append(f"Obsolete submission interface in {record['path']}: {forbidden}")
        if any(cell.get("outputs") or cell.get("execution_count") is not None for cell in code_cells):
            failures.append(f"Saved code output remains in {record['path']}")

    for record in manifest.get("active_pdfs", []) + manifest.get("archive_pdfs", []):
        path = ROOT / record["path"]
        if not path.is_file() or sha256(path) != record["sha256"]:
            failures.append(f"Manifest PDF missing or hash drift: {record['path']}")

    scheduled_destinations: set[str] = set()
    for release in schedule["releases"]:
        for phase in ("workbook-key", "quiz-package"):
            release_id = f"day{release['day']:02d}:{phase}"
            is_complete = release_id in completed
            for record in release["phases"][phase]["files"]:
                scheduled_destinations.add(record["destination"])
                destination = ROOT / record["destination"]
                if is_complete:
                    if not destination.is_file() or sha256(destination) != record["sha256"]:
                        failures.append(f"Released file missing or changed: {record['destination']}")
                elif destination.exists():
                    failures.append(f"Embargoed scheduled file is present early: {record['destination']}")

    for day in range(1, 9):
        day_dirs = list(ROOT.glob(f"week*/day{day:02d}_*"))
        if len(day_dirs) != 1:
            failures.append(f"Could not resolve completed Day {day} directory")
            continue
        required = {
            f"DAY{day:02d}_LAB_ALIGNED_WORKBOOK_STUDENT_07202026_v5.pdf",
            f"DAY{day:02d}_LAB_ALIGNED_WORKBOOK_INSTRUCTOR_KEY_07202026_v5.pdf",
            f"DAY{day:02d}_INDEPENDENCE_RAMP_QUIZ_STUDENT_07202026_v5.pdf",
            f"DAY{day:02d}_INDEPENDENCE_RAMP_QUIZ_INSTRUCTOR_KEY_07202026_v5.pdf",
        }
        missing = sorted(name for name in required if not (day_dirs[0] / name).is_file())
        if missing:
            failures.append(f"Completed Day {day} release is incomplete: {missing}")

    active_markdown = [
        ROOT / "README.md",
        ROOT / "START_HERE_STUDENTS.md",
        ROOT / "CURRENT_STUDENT_MATERIALS_INDEX_07202026_v5.md",
        ROOT / "DOWNLOAD_CURRENT_STUDENT_PDFS.md",
        ROOT / "DOWNLOAD_CURRENT_STUDENT_NOTEBOOKS.md",
        ROOT / "notebooks/README.md",
        ROOT / "archive/README.md",
        ROOT / "archive/legacy_daily_materials_through_20260717/INDEX.md",
        ROOT / "release_schedule/CURRENT_RELEASE_STATUS.md",
        *sorted(ROOT.glob("week*/day*/README.md")),
    ]
    broken_links: list[str] = []
    for document in active_markdown:
        if not document.is_file():
            failures.append(f"Required navigation file is missing: {document.relative_to(ROOT)}")
            continue
        for target in markdown_links(document):
            clean = target.split("#", 1)[0]
            if not clean or re.match(r"^(?:https?|mailto):", clean):
                continue
            destination = (document.parent / unquote(clean)).resolve()
            try:
                destination.relative_to(ROOT)
            except ValueError:
                broken_links.append(f"{document.relative_to(ROOT)} -> outside: {target}")
                continue
            if not destination.exists():
                broken_links.append(f"{document.relative_to(ROOT)} -> {target}")
    failures.extend(f"Broken active Markdown link: {value}" for value in broken_links)

    result = {
        "status": "PASS" if not failures else "FAIL",
        "active_pdf_count": manifest.get("active_pdf_count"),
        "archive_pdf_count": manifest.get("archive_pdf_count"),
        "student_notebook_count": manifest.get("student_notebook_count"),
        "completed_scheduled_release_count": len(completed),
        "scheduled_destination_count": len(scheduled_destinations),
        "tex_zip_count": len(forbidden_sources),
        "exam_artifact_count": len(exam_files),
        "broken_active_link_count": len(broken_links),
        "failures": failures,
    }
    return result


def write_reports(result: dict) -> None:
    JSON_REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Student Repository Hygiene Validation",
        "",
        f"Disposition: **{result['status']}**",
        "",
        f"- Active PDFs: {result['active_pdf_count']}",
        f"- Archived legacy PDFs: {result['archive_pdf_count']}",
        f"- Current notebooks: {result['student_notebook_count']}",
        f"- Completed scheduled phases: {result['completed_scheduled_release_count']}",
        f"- Scheduled destinations: {result['scheduled_destination_count']}",
        f"- TeX/ZIP artifacts: {result['tex_zip_count']}",
        f"- Exam artifacts: {result['exam_artifact_count']}",
        f"- Broken active links: {result['broken_active_link_count']}",
        "",
        "This check validates current and archived hashes, notebook cleanliness, release embargoes, the exam boundary, and public navigation.",
        "",
    ]
    if result["failures"]:
        lines.extend(["## Failures", "", *[f"- {item}" for item in result["failures"]], ""])
    MD_REPORT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    result = validate()
    write_reports(result)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
