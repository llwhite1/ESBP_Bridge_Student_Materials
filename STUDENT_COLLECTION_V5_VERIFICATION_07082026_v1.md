# Student Collection v5 Verification

Version: 07082026 v1
Repository: ESBP_Bridge_Student_Materials

## Scope

This verification covers the v5 student learning collection pass after the public/org-publication sanitization update.

The v5 collection keeps the repo calendar-first, adds a student-first navigation layer, removes daily quiz PDFs and exam/assessment PDFs from the current collection, and keeps only non-assessment student-facing learning/support surfaces.

Notebook practice remains linked through the companion notebook repository rather than copied into this PDF collection.

## License check

- Conservative license file present: `LICENSE.md`
- License selected: `CC BY-NC-ND 4.0`
- README includes license/use section: PASS.

## Current collection checks

- Manifest version: `07082026_v5_student_learning_collection_no_quizzes_no_exams`
- Manifest records checked: `54`
- Unique manifest records: `54`
- Current PDF count: `19`
- Manifest PDF count: `19`
- Quiz PDF count in current repo: `0`
- Exam/assessment PDF count in current repo: `0`
- Day README count: `20`
- Markdown file count checked: `36`

## Day README structure checks

Every day-folder README was checked for these student-first sections:

1. `Start here for this day`
2. `Current student-facing files`
3. `What you are learning today`
4. `Before class / during class / after class`
5. `If you get stuck`
6. `How this connects to ENGR 102`
7. `Related collection pages`

Result: PASS.

- Missing section results: `[]`

## Link and manifest checks

- Broken local Markdown links: `[]`
- Missing manifest files: `[]`
- Duplicate manifest records: `[]`
- Byte-size mismatches: `[]`
- SHA-256 mismatches: `[]`
- Current PDF set matched manifest PDF set: PASS.

## Student-surface safety checks

- Instructor-only/answer-bearing marker hits: `[]`
- Process/source marker hits: `[]`
- Quiz PDFs remaining in current folders: `[]`
- Exam/assessment PDFs remaining in current folders: `[]`

## PDF render/text checks

All 19 current PDFs opened successfully and had at least one page.

First-page visual QA from the pre-exam-removal v5 pass showed the workbooklet/support/reflection surfaces readable and student-facing. After this sanitization update, the removed files are assessment/exam-related; the remaining PDF set is a subset of the already rendered workbooklet/support/reflection surfaces.

## Status

PASS. The current student repo is now a richer non-quiz, non-exam student learning collection with:

- root start-here guidance;
- a current materials index;
- competency-based collections;
- notebook/practice path guidance;
- root-level [Quick Glossary](ENGR102_BRIDGE_QUICK_GLOSSARY.md);
- all 20 day-folder READMEs upgraded to student-first guidance;
- 19 current non-quiz/non-exam PDFs;
- conservative CC BY-NC-ND 4.0 license;
- v5 Markdown and JSON manifests.
