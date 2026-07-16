#!/usr/bin/env python3
"""Validate the consolidated public student-materials repository."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
ACCESS_MANIFEST = ROOT / "manifest_student_access_07162026_v8.json"
NOTEBOOK_MANIFEST = ROOT / "notebooks/STUDENT_NOTEBOOK_RELEASE_MANIFEST_07162026_v1.json"
JSON_REPORT = ROOT / "REPOSITORY_HYGIENE_07162026_v1.json"
MD_REPORT = ROOT / "REPOSITORY_HYGIENE_07162026_v1.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_text(cell: dict) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else str(source)


def markdown_links(path: Path) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8"))


def validate() -> dict:
    failures: list[str] = []
    access = json.loads(ACCESS_MANIFEST.read_text(encoding="utf-8"))
    notebooks = json.loads(NOTEBOOK_MANIFEST.read_text(encoding="utf-8"))
    if access.get("status") != "current" or access.get("student_pdf_count") != 18:
        failures.append("combined access manifest does not declare 18 current PDFs")
    if access.get("aligned_workbook_count") != 10:
        failures.append("combined access manifest does not declare 10 aligned workbooks")
    if access.get("student_notebook_count") != 7 or access.get("notebook_activity_count") != 32:
        failures.append("combined access manifest does not declare 7 notebooks and 32 activities")
    if notebooks.get("status") != "PASS" or notebooks.get("submission_type") != "single_ipynb":
        failures.append("student notebook release manifest is not PASS/single-ipynb")

    for record in access.get("pdfs", []):
        path = ROOT / record["path"]
        if not path.is_file() or sha256(path) != record["sha256"]:
            failures.append(f"PDF missing or hash drift: {record['path']}")
    for record in notebooks.get("records", []):
        path = ROOT / record["path"]
        if not path.is_file() or sha256(path) != record["sha256"]:
            failures.append(f"notebook missing or hash drift: {record['path']}")
            continue
        notebook = json.loads(path.read_text(encoding="utf-8"))
        if notebook["metadata"].get("seas_vip_status") != "student_release":
            failures.append(f"notebook lacks student-release status: {record['path']}")
        if notebook["metadata"].get("gradescope_submission_type") != "single_ipynb":
            failures.append(f"notebook lacks single-ipynb metadata: {record['path']}")
        code_cells = [cell for cell in notebook["cells"] if cell.get("cell_type") == "code"]
        code = "\n".join(source_text(cell) for cell in code_cells)
        for forbidden in ["%%writefile", "zipfile", "shutil.make_archive", "load_student_module"]:
            if forbidden.lower() in code.lower():
                failures.append(f"obsolete notebook interface remains in {record['path']}: {forbidden}")
        if any(cell.get("outputs") or cell.get("execution_count") is not None for cell in code_cells):
            failures.append(f"saved code output remains in {record['path']}")

    leaked = [
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and (
            path.suffix.lower() in {".tex", ".zip"}
            or "instructor_key" in path.name.lower()
            or "answer_key" in path.name.lower()
        )
    ]
    if leaked:
        failures.append(f"instructor/source artifacts leaked into public repository: {leaked}")

    active_markdown = [
        ROOT / "README.md",
        ROOT / "START_HERE_STUDENTS.md",
        ROOT / "CURRENT_STUDENT_MATERIALS_INDEX_07152026_v2.md",
        ROOT / "DOWNLOAD_CURRENT_STUDENT_PDFS.md",
        ROOT / "DOWNLOAD_CURRENT_STUDENT_NOTEBOOKS.md",
        ROOT / "NOTEBOOKS_AND_PRACTICE_PATH_07162026_v2.md",
        ROOT / "STUDENT_COLLECTION_SCOPE_07162026_v2.md",
        ROOT / "notebooks/README.md",
        *sorted(ROOT.glob("week*/day*/README.md")),
    ]
    broken_links: list[str] = []
    for document in active_markdown:
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
    if broken_links:
        failures.extend(f"broken active Markdown link: {value}" for value in broken_links)

    active_text = "\n".join(path.read_text(encoding="utf-8") for path in active_markdown)
    for obsolete in [
        "Notebook practice is not bundled",
        "Approved notebook practice remains in the companion notebook repository",
        "Only student-facing learning PDFs are published",
    ]:
        if obsolete in active_text:
            failures.append(f"obsolete current guidance remains: {obsolete}")

    return {
        "status": "PASS" if not failures else "FAIL",
        "student_pdf_count": access.get("student_pdf_count"),
        "aligned_workbook_count": access.get("aligned_workbook_count"),
        "student_notebook_count": access.get("student_notebook_count"),
        "notebook_activity_count": access.get("notebook_activity_count"),
        "key_tex_zip_leak_count": len(leaked),
        "broken_active_link_count": len(broken_links),
        "failures": failures,
    }


def write_reports(result: dict) -> None:
    JSON_REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Student Repository Hygiene Validation",
        "",
        "Date: 2026-07-16",
        f"Disposition: **{result['status']}**",
        "",
        f"- Student PDFs: {result['student_pdf_count']}",
        f"- Lab-aligned workbooks: {result['aligned_workbook_count']}",
        f"- Student notebooks: {result['student_notebook_count']}",
        f"- Notebook activities: {result['notebook_activity_count']}",
        f"- Key/TeX/ZIP leaks: {result['key_tex_zip_leak_count']}",
        f"- Broken active links: {result['broken_active_link_count']}",
        "",
        "The validation checks manifest hashes, clean notebook metadata and saved state, removal of the obsolete ZIP-based notebook interface, public/private artifact boundaries, and current navigation links.",
        "",
    ]
    if result["failures"]:
        lines.extend(["## Failures", "", *[f"- {failure}" for failure in result["failures"]], ""])
    MD_REPORT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    result = validate()
    write_reports(result)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
