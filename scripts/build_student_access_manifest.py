#!/usr/bin/env python3
"""Build the current combined PDF and notebook student-access manifest."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_MANIFEST = ROOT / "notebooks/STUDENT_NOTEBOOK_RELEASE_MANIFEST_07172026_v2.json"
JSON_OUTPUT = ROOT / "manifest_student_access_07172026_v9.json"
MD_OUTPUT = ROOT / "MANIFEST_STUDENT_ACCESS_07172026_v9.md"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_pages(path: Path) -> int:
    output = subprocess.check_output(["pdfinfo", str(path)], text=True, errors="replace")
    match = re.search(r"^Pages:\s+(\d+)$", output, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not determine page count for {path}")
    return int(match.group(1))


def build() -> dict[str, Any]:
    notebook_manifest = read_json(NOTEBOOK_MANIFEST)
    pdf_records = []
    for path in sorted(ROOT.glob("week*/day*/*.pdf")):
        if (
            "LAB_ALIGNED_WORKBOOK_STUDENT" in path.name
            and not path.name.endswith("_07172026_v2.pdf")
        ):
            continue
        if path.name == "DAY18_SYNTHESIS_WORKBOOKLET_STUDENT_07012026_v1.pdf":
            continue
        pdf_records.append(
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
                "pages": pdf_pages(path),
                "lab_aligned_workbook": "LAB_ALIGNED_WORKBOOK_STUDENT" in path.name,
            }
        )
    notebook_records = [
        {
            "lab_day": record["lab_day"],
            "path": record["path"],
            "sha256": record["sha256"],
            "activity_ids": record["activity_ids"],
            "cold_cell_ids": record.get("cold_cell_ids", []),
            "scoring_model": record.get("scoring_model"),
        }
        for record in notebook_manifest["records"]
    ]
    manifest = {
        "version": "07172026_v9_cold_checkpoint_workbooks_and_notebooks",
        "status": "current_student_release",
        "workbook_contract_sha256": notebook_manifest["source_contract_sha256"],
        "notebook_release_set_sha256": notebook_manifest["release_set_sha256"],
        "student_pdf_count": len(pdf_records),
        "aligned_workbook_count": sum(record["lab_aligned_workbook"] for record in pdf_records),
        "student_notebook_count": len(notebook_records),
        "notebook_activity_count": sum(len(record["activity_ids"]) for record in notebook_records),
        "quiz_pdf_count": 0,
        "exam_pdf_count": 0,
        "instructor_key_count": 0,
        "tex_source_count": 0,
        "pdfs": pdf_records,
        "notebooks": notebook_records,
    }
    JSON_OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    MD_OUTPUT.write_text(
        "\n".join(
            [
                "# Student Access Manifest 07172026 v9",
                "",
                "Version: `07172026_v9_cold_checkpoint_workbooks_and_notebooks`",
                "",
                "Status: current published student release.",
                "",
                "## Collection rule",
                "",
                "Publish only current student-facing workbooks, support PDFs, and clean notebook releases. Quizzes, exams, answer keys, TeX sources, contracts, build logs, and autograder internals remain excluded.",
                "",
                "## July 17 release",
                "",
                "- Uses eleven contract-controlled lab-aligned workbook successors for Bridge Days 6-8, 10-16, and 18.",
                "- Includes seven current VIP Module 18 notebooks covering Activities 18.1-18.32.",
                "- Lab Days 5-7 keep sample/transfer cells formative and score only the five cold checkpoint cells at the end.",
                "- Students submit one completed `.ipynb`; they do not use `%%writefile`, exported `.py` files, or ZIP packaging.",
                "- Day 16 remains loop/list Exam 2 preparation; functions begin in the Day 18 post-exam handoff.",
                "- The former notebook-only repository is not the current student release authority.",
                "",
                "## Counts",
                "",
                f"- Current student PDFs: {manifest['student_pdf_count']}",
                f"- Current lab-aligned workbooks: {manifest['aligned_workbook_count']}",
                f"- Current student notebooks: {manifest['student_notebook_count']}",
                f"- Notebook activities: {manifest['notebook_activity_count']}",
                "- Quiz PDFs: 0",
                "- Exam PDFs: 0",
                "- Instructor-key files: 0",
                "- TeX source files: 0",
                "",
                "## Current navigation",
                "",
                "- [Root README](README.md)",
                "- [Current PDF index](CURRENT_STUDENT_MATERIALS_INDEX_07152026_v2.md)",
                "- [Current notebook index](notebooks/README.md)",
                "- [Direct notebook downloads](DOWNLOAD_CURRENT_STUDENT_NOTEBOOKS.md)",
                "- [Machine-readable manifest](manifest_student_access_07172026_v9.json)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return manifest


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
