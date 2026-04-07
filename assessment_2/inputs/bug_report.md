# Bug Report: Duplicate Tasks on Last Page of Paginated Results

## Title
Duplicate tasks appearing on last page of paginated `/api/tasks` endpoint

## Severity
**High** — Data integrity issue affecting API consumers

## Environment
- **Language/Runtime**: Python 3.12
- **Framework**: Flask 3.0.x
- **Database**: SQLite3
- **OS**: Windows 11 / Linux (reproduced on both)
- **Endpoint**: `GET /api/tasks?page=N&per_page=M`

## Description
When requesting the last page of paginated task results, the API returns duplicate items that also appear on the previous page. This occurs specifically when the total number of tasks is **not evenly divisible** by the `per_page` parameter.

## Expected Behavior
- `GET /api/tasks?page=5&per_page=7` (with 30 total tasks) should return **2 items**: tasks with IDs 29 and 30.
- Each task should appear on exactly **one** page across all paginated responses.
- Iterating through all pages should yield exactly 30 unique tasks.

## Actual Behavior
- `GET /api/tasks?page=5&per_page=7` returns **7 items** instead of 2.
- The returned items are tasks 24-30, which **overlap** with page 4's results (tasks 22-28).
- Tasks 24-28 appear on **both** page 4 and page 5.
- Total items across all pages = 35 (instead of 30), with 5 duplicates.

## Steps to Reproduce
1. Ensure the database has 30 tasks (default seed data).
2. Request tasks with `per_page=7`:
   ```
   GET /api/tasks?page=1&per_page=7  → 7 items (IDs 1-7)   ✓
   GET /api/tasks?page=2&per_page=7  → 7 items (IDs 8-14)  ✓
   GET /api/tasks?page=3&per_page=7  → 7 items (IDs 15-21) ✓
   GET /api/tasks?page=4&per_page=7  → 7 items (IDs 22-28) ✓
   GET /api/tasks?page=5&per_page=7  → 7 items (IDs 24-30) ✗ WRONG
   ```
3. Notice page 5 starts from ID 24 instead of ID 29.
4. Items 24-28 are duplicated across pages 4 and 5.

## Reproduction Hints
- The issue does NOT occur when `total % per_page == 0` (e.g., 30 tasks with per_page=10 works correctly).
- The bug is in the pagination utility function, not in the database query.
- Check the `paginate_results()` function in `utils.py` — specifically the offset calculation for the last page.

## Impact
- Frontend components displaying paginated data show duplicate entries.
- API consumers iterating through pages get incorrect total counts.
- Data export features produce files with duplicate rows.
- Affects customer trust in data accuracy.

## Reporter
QA Team — Automated regression test flagged this on 2026-04-05
