#!/usr/bin/env python3
"""Build the live manifest for the public Bridge student repository."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_MANIFEST = ROOT / "notebooks/STUDENT_NOTEBOOK_RELEASE_MANIFEST_07202026_v5.json"
JSON_OUTPUT = ROOT / "manifest_student_access.json"
MD_OUTPUT = ROOT / "MANIFEST_STUDENT_ACCESS.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_pages(path: Path) -> int:
    output = subprocess.check_output(["pdfinfo", str(path)], text=True, errors="replace")
    match = re.search(r"^Pages:\s+(\d+)$", output, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not determine page count for {path}")
    return int(match.group(1))


def category(name: str) -> str:
    if "WORKBOOK" in name and "KEY" in name:
        return "workbook_key"
    if "WORKBOOK" in name:
        return "workbook"
    if "QUIZ" in name and "KEY" in name:
        return "quiz_key"
    if "QUIZ" in name:
        return "quiz"
    return "support"


def build() -> dict:
    notebook_manifest = json.loads(NOTEBOOK_MANIFEST.read_text(encoding="utf-8"))
    active_pdfs = []
    for path in sorted(ROOT.glob("week*/day*/*.pdf")):
        active_pdfs.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
                "pages": pdf_pages(path),
                "category": category(path.name),
            }
        )
    archive_pdfs = []
    for path in sorted((ROOT / "archive").rglob("*.pdf")):
        archive_pdfs.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
                "category": category(path.name),
            }
        )
    notebooks = [
        {
            "lab_day": record["lab_day"],
            "path": record["path"],
            "sha256": record["sha256"],
            "activity_ids": record["activity_ids"],
        }
        for record in notebook_manifest["records"]
    ]
    counts = {key: 0 for key in ("workbook", "workbook_key", "quiz", "quiz_key", "support")}
    for record in active_pdfs:
        counts[record["category"]] += 1
    manifest = {
        "version": "2026-07-20-v5-construct-evidence-release",
        "status": "published_student_release",
        "active_pdf_count": len(active_pdfs),
        "active_pdf_counts": counts,
        "student_notebook_count": len(notebooks),
        "notebook_activity_count": sum(len(item["activity_ids"]) for item in notebooks),
        "archive_pdf_count": len(archive_pdfs),
        "exam_pdf_count": sum(
            "day09_exam1" in item["path"].lower()
            or "day17_exam2" in item["path"].lower()
            or "exam1_" in Path(item["path"]).name.lower()
            or "exam2_" in Path(item["path"]).name.lower()
            for item in active_pdfs + archive_pdfs
        ),
        "tex_source_count": len(list(ROOT.rglob("*.tex"))),
        "zip_source_count": len(list(ROOT.rglob("*.zip"))),
        "active_pdfs": active_pdfs,
        "notebooks": notebooks,
        "archive_pdfs": archive_pdfs,
    }
    JSON_OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    MD_OUTPUT.write_text(
        "\n".join(
            [
                "# Student Access Manifest",
                "",
                "Status: published student release with a clean active/archive split and scheduled delayed solutions.",
                "",
                "## Active collection",
                "",
                f"- Active PDFs: {manifest['active_pdf_count']}",
                f"- Current workbooks: {counts['workbook']}",
                f"- Released workbook keys: {counts['workbook_key']}",
                f"- Released student quizzes: {counts['quiz']}",
                f"- Released quiz keys: {counts['quiz_key']}",
                f"- Other current support PDFs: {counts['support']}",
                f"- Current student notebooks: {manifest['student_notebook_count']}",
                f"- Notebook activities: {manifest['notebook_activity_count']}",
                "",
                "## Archive and safety boundary",
                "",
                f"- Archived legacy PDFs: {manifest['archive_pdf_count']}",
                f"- Exam PDFs in the student repo: {manifest['exam_pdf_count']}",
                f"- TeX sources in the student repo: {manifest['tex_source_count']}",
                f"- ZIP/source packages in the student repo: {manifest['zip_source_count']}",
                "",
                "Exam 1 and Exam 2 materials and keys remain outside the student repository. Legacy answer-bearing PDFs are included only when they are intentionally released for completed daily work.",
                "",
                "## Navigation",
                "",
                "- [Current materials index](CURRENT_STUDENT_MATERIALS_INDEX_07202026_v5.md)",
                "- [Release status](release_schedule/CURRENT_RELEASE_STATUS.md)",
                "- [Legacy archive](archive/README.md)",
                "- [Machine-readable manifest](manifest_student_access.json)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return manifest


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
