#!/usr/bin/env python3
"""Release one scheduled Bridge solution or quiz package into the student repo.

This script deliberately does not commit or push.  It copies only files named in
the checked-in schedule, verifies every source hash, updates the release ledger,
and regenerates the public status, manifest, and archive index.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SCHEDULE_PATH = ROOT / "release_schedule/bridge_student_release_schedule_20260720_20260728.json"
LEDGER_PATH = ROOT / "release_schedule/release_ledger.json"
STATUS_PATH = ROOT / "release_schedule/CURRENT_RELEASE_STATUS.md"
ARCHIVE_INDEX = ROOT / "archive/legacy_daily_materials_through_20260717/INDEX.md"
DOWNLOADS_PATH = ROOT / "DOWNLOAD_CURRENT_STUDENT_PDFS.md"
TIMEZONE = ZoneInfo("America/Chicago")
PHASES = {"workbook-key", "quiz-package"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def instructor_root(override: str | None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    return ROOT.parent / "ESBP_Bridge_Instructor_Materials"


def selected_release(schedule: dict, release_date: str, phase: str) -> dict:
    matches = [
        item
        for item in schedule["releases"]
        if item["release_date"] == release_date and phase in item["phases"]
    ]
    if not matches:
        raise SystemExit(f"No {phase} release is scheduled for {release_date}.")
    if len(matches) != 1:
        raise SystemExit(f"Schedule is ambiguous for {release_date} / {phase}.")
    return matches[0]


def assert_safe_destination(relative: str) -> None:
    lowered = relative.lower()
    filename = Path(relative).name.lower()
    if (
        "day09_exam1" in lowered
        or "day17_exam2" in lowered
        or filename.startswith(("exam1_", "exam2_"))
        or "_exam1_" in filename
        or "_exam2_" in filename
    ):
        raise RuntimeError(f"Exam-boundary file is not releasable: {relative}")
    if relative.endswith((".tex", ".zip")):
        raise RuntimeError(f"Source/build file is not releasable: {relative}")


def copy_phase(
    release: dict,
    phase: str,
    source_root: Path,
    *,
    dry_run: bool,
) -> list[str]:
    changed: list[str] = []
    for record in release["phases"][phase]["files"]:
        source = source_root / record["source"]
        destination = ROOT / record["destination"]
        assert_safe_destination(record["destination"])
        if not source.is_file():
            raise FileNotFoundError(f"Scheduled source is missing: {source}")
        actual = sha256(source)
        if actual != record["sha256"]:
            raise RuntimeError(
                f"Scheduled source hash drift: {record['source']}\n"
                f"expected {record['sha256']}\nactual   {actual}"
            )
        if destination.exists():
            if sha256(destination) != actual:
                raise RuntimeError(f"Destination exists with different content: {destination}")
            continue
        changed.append(record["destination"])
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    return changed


def scheduled_datetime(item: dict, phase: str) -> datetime:
    """Return the authoritative Central-Time boundary for one release phase."""
    phase_clock = time.fromisoformat(item["phases"][phase]["time_ct"])
    return datetime.combine(
        datetime.fromisoformat(item["release_date"]).date(),
        phase_clock,
        tzinfo=TIMEZONE,
    )


def release_status(item: dict, phase: str, completed: set[str], now: datetime) -> str:
    release_id = f"day{item['day']:02d}:{phase}"
    if release_id in completed:
        return "Available"
    if now >= scheduled_datetime(item, phase):
        return "Overdue - pending release"
    return "Scheduled"


def write_status(schedule: dict, ledger: dict, *, now: datetime | None = None) -> None:
    now = now or datetime.now(TIMEZONE)
    completed = set(ledger.get("completed_release_ids", []))
    rows = []
    for item in schedule["releases"]:
        for phase in ("workbook-key", "quiz-package"):
            phase_data = item["phases"][phase]
            status = release_status(item, phase, completed, now)
            label = "Workbook key" if phase == "workbook-key" else "Quiz + quiz key"
            rows.append(
                f"| Day {item['day']} | {label} | {item['release_date']} | "
                f"{phase_data['time_ct']} CT | {status} |"
            )
    STATUS_PATH.write_text(
        "\n".join(
            [
                "# Bridge Student Release Status",
                "",
                "This is the authoritative public status for delayed workbook-key and quiz-package releases.",
                "Times are America/Chicago (Central Time). Exam 1 and Exam 2 files and keys are not part of this schedule.",
                "",
                "Days 1-8 v5 workbook keys, student quizzes, and quiz keys are already available in their current day folders.",
                "The schedule below releases current v5 files; matching v4 keys are retained only in the [archive](../archive/README.md) for work completed before the correction.",
                "Available means the files are present and recorded in the release ledger. Overdue means the stated boundary has passed but the controlled release has not completed.",
                "",
                "| Class day | Release | Date | Time | Status |",
                "|---|---|---|---:|---|",
                *rows,
                "",
                "If a scheduled item is not visible after the stated time, tell the instructor; do not substitute an exam file or an unreleased instructor artifact.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_archive_index() -> None:
    base = ARCHIVE_INDEX.parent
    lines = [
        "# Legacy Daily Materials Index",
        "",
        "These files are superseded versions kept for reference. Use the current day folders for assigned work.",
        "Keys appear here only after their scheduled student-release time. TeX sources, autograders, and exam keys are never copied here.",
        "",
    ]
    for day_dir in sorted(base.glob("day[0-9][0-9]")):
        files = sorted(path for path in day_dir.iterdir() if path.is_file())
        if not files:
            continue
        lines.extend([f"## Day {int(day_dir.name[-2:])}", ""])
        for path in files:
            rel = path.relative_to(base)
            kind = "key" if "KEY" in path.name else "student material"
            lines.append(f"- [{path.name}]({rel.as_posix()}) — legacy {kind}")
        lines.append("")
    notebook_dir = base / "notebooks_07172026_v3"
    if notebook_dir.is_dir():
        lines.extend(
            [
                "## Earlier notebook release",
                "",
                "The July 17 v3 notebooks are retained here; use the July 19 v4 notebooks in the active `notebooks/` folder.",
                "",
                *[
                    f"- [{path.name}]({path.relative_to(base).as_posix()})"
                    for path in sorted(notebook_dir.iterdir())
                    if path.is_file()
                ],
                "",
            ]
        )
    ARCHIVE_INDEX.write_text("\n".join(lines), encoding="utf-8")


def write_downloads_page() -> None:
    lines = [
        "# Current Student PDF Downloads",
        "",
        "This page lists active PDFs only. Superseded versions are in the [legacy archive](archive/README.md).",
        "Scheduled files appear here after the release automation copies and validates them.",
        "",
    ]
    for directory in sorted(ROOT.glob("week*/day*")):
        pdfs = sorted(directory.glob("*.pdf"))
        if not pdfs:
            continue
        readme = directory / "README.md"
        title = directory.name
        if readme.is_file():
            first = readme.read_text(encoding="utf-8").splitlines()[0]
            title = first.removeprefix("# ")
        lines.extend([f"## {title}", ""])
        for path in pdfs:
            relative = path.relative_to(ROOT).as_posix()
            lines.append(f"- [{path.name}]({relative})")
        lines.append("")
    DOWNLOADS_PATH.write_text("\n".join(lines), encoding="utf-8")


def regenerate_public_reports() -> None:
    subprocess.run(["python3", str(ROOT / "scripts/build_student_access_manifest.py")], check=True)
    subprocess.run(["python3", str(ROOT / "scripts/validate_student_repository.py")], check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=sorted(PHASES))
    parser.add_argument("--date", help="Release date in YYYY-MM-DD; defaults to today in Central Time")
    parser.add_argument("--instructor-repo")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--status-only",
        action="store_true",
        help="Refresh the public status from the schedule, ledger, and current Central Time without releasing files.",
    )
    args = parser.parse_args()

    now = datetime.now(TIMEZONE)
    schedule = load_json(SCHEDULE_PATH)
    if args.status_only:
        if args.phase or args.date or args.dry_run:
            parser.error("--status-only cannot be combined with --phase, --date, or --dry-run")
        ledger = load_json(LEDGER_PATH)
        write_status(schedule, ledger, now=now)
        print(json.dumps({"status": "STATUS_REFRESHED", "refreshed_at": now.isoformat(timespec="seconds")}, indent=2))
        return 0
    if not args.phase:
        parser.error("--phase is required unless --status-only is used")

    release_date = args.date or now.date().isoformat()
    release = selected_release(schedule, release_date, args.phase)
    scheduled_at = scheduled_datetime(release, args.phase)
    if not args.dry_run and now < scheduled_at:
        raise SystemExit(
            f"Release boundary is still closed until {scheduled_at.isoformat(timespec='minutes')}."
        )
    source_root = instructor_root(args.instructor_repo)
    changed = copy_phase(release, args.phase, source_root, dry_run=args.dry_run)

    result = {
        "status": "DRY_RUN" if args.dry_run else "RELEASED",
        "day": release["day"],
        "phase": args.phase,
        "release_date": release_date,
        "changed_paths": changed,
    }
    if args.dry_run:
        print(json.dumps(result, indent=2))
        return 0

    ledger = load_json(LEDGER_PATH)
    release_id = f"day{release['day']:02d}:{args.phase}"
    completed = ledger.setdefault("completed_release_ids", [])
    if release_id not in completed:
        completed.append(release_id)
        completed.sort()
    ledger.setdefault("events", []).append(
        {
            "release_id": release_id,
            "scheduled_date": release_date,
            "scheduled_time_ct": release["phases"][args.phase]["time_ct"],
            "released_at": now.isoformat(timespec="seconds"),
            "changed_paths": changed,
        }
    )
    write_json(LEDGER_PATH, ledger)
    write_status(schedule, ledger)
    write_archive_index()
    write_downloads_page()
    regenerate_public_reports()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
