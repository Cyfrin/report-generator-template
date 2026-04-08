# Combined Multi-Phase Audit Report Guide

When a client has multiple audits (e.g. initial review, follow-up PRs, new modules) and requests a single unified report, you can combine them by creating a modified copy of the report-generator-template that fetches issues from multiple repos and presents all phases in one PDF.

This was first done for the Myriad audits (March-April 2026), combining 3 audit phases (CLOB, Realitio Oracle, PR145) into a single report.

## When to use this

- Same client across multiple audits
- Same source repo (or closely related repos)
- Client wants a single deliverable PDF covering all engagements

## Setup

1. Copy the standard `report-generator-template/` to a new directory (e.g. `combined-report/`)
2. Modify the files listed below
3. Run `python3 generate_report.py` locally (no GitHub Actions needed — just needs `GITHUB_ACCESS_TOKEN` environment variable set)

## Files to modify

### 1. `source/summary_information.conf`

Add `[phase_N]` sections below the standard `[summary]` section. Each phase has its own repo, commits, timeline, and project number:

```ini
[summary]
project_name = Client Name
report_version = 2.0
team_name = Client Name
team_website = https://example.com
# Keep these for compatibility but leave empty — per-phase data goes below
private_github = https://github.com/Cyfrin/audit-YYYY-MM-client-phase1.git
project_github = https://github.com/ClientOrg/client-repo
commit_hash =
fix_commit_hash =
project_github_2 =
commit_hash_2 =
fix_commit_hash_2 =
project_github_3 =
commit_hash_3 =
fix_commit_hash_3 =
review_timeline = <overall start> - <overall end>
review_methods = Manual Review
project_number =
filter_issue_id_list =
filter_issue_label =
filter_issue_column =

[phase_1]
name = Phase 1 Name
private_github = https://github.com/Cyfrin/audit-YYYY-MM-client-phase1.git
project_github = https://github.com/ClientOrg/client-repo
commit_hash = <initial commit hash>
fix_commit_hash = <fix commit hash>
review_timeline = <start> - <end>
project_number = <GitHub project number>

[phase_2]
name = Phase 2 Name
private_github = https://github.com/Cyfrin/audit-YYYY-MM-client-phase2.git
project_github = https://github.com/ClientOrg/client-repo
commit_hash = <initial commit hash>
fix_commit_hash = <fix commit hash>
review_timeline = <start> - <end>
project_number = <GitHub project number>

# Add more [phase_N] sections as needed (up to 9 supported)
```

### 2. `scripts/helpers.py`

Add these functions:

- **`get_phase_information()`** — reads `[phase_N]` sections from the config and returns a list of phase dictionaries
- **`calculate_combined_period(phases)`** — sums workdays across all phases
- **`merge_issue_dicts(all_issue_dicts)`** — merges issue dictionaries from multiple repos by severity label
- **`merge_summary_findings(all_summary_findings)`** — merges summary findings tables
- **`write_report_and_counts(issue_dict, summary_of_findings)`** — extracted from the old `get_issues()` to write `report.md`, `severity_counts.conf`, and the summary findings table after merging

Refactor **`get_issues()`** to return data structures `(issue_dict, issues_by_number, summary_of_findings, count_by_severity)` instead of writing files directly. This allows fetching from each repo independently and merging before writing.

### 3. `scripts/fetch_issues.py`

Replace the single-repo `fetch_issues()` with a loop over phases:

```python
def fetch_issues():
    phases = get_phase_information()
    all_issue_dicts = []
    all_summary_findings = []

    for phase in phases:
        issue_dict, _, summary_of_findings, _ = fetch_issues_for_phase(phase)
        all_issue_dicts.append(issue_dict)
        all_summary_findings.append(summary_of_findings)

    merged_issues = merge_issue_dicts(all_issue_dicts)
    merged_findings = merge_summary_findings(all_summary_findings)
    total = write_report_and_counts(merged_issues, merged_findings)
```

Each phase's issues are fetched and have internal `#xx` links resolved independently (within their own repo's issue numbers), then all results are merged by severity.

### 4. `templates/summary.tex`

Replace the single-audit summary table with two tables:

- **Summary** table: project name, repo, overall timeline, methods
- **Audit Phases** table: columns for each phase showing initial commit, fix commit, and timeline

Use placeholders like `__PLACEHOLDER__PHASE_1_NAME`, `__PLACEHOLDER__PHASE_1_COMMIT`, `__PLACEHOLDER__PHASE_1_FIX`, `__PLACEHOLDER__PHASE_1_TIMELINE`, etc.

Example LaTeX for the phases table:

```latex
\begin{table}[H]
  \centering
  \caption*{\textbf{Audit Phases}}
  \begin{tabular}{|p{2.8cm}|p{3.6cm}|p{3.6cm}|p{3.6cm}|}
    \hline
    & \textbf{__PLACEHOLDER__PHASE_1_NAME} & \textbf{__PLACEHOLDER__PHASE_2_NAME} & \textbf{__PLACEHOLDER__PHASE_3_NAME} \\
    \hline
    Initial Commit & \href{...}{\truncatehash{...}} & ... & ... \\
    \hline
    Fix Commit & \href{...}{\truncatehash{...}} & ... & ... \\
    \hline
    Timeline & __PLACEHOLDER__PHASE_1_TIMELINE & ... & ... \\
    \hline
  \end{tabular}
\end{table}
```

For more than 3 phases, the table would need to wrap or use a different layout.

### 5. `generate_report.py`

- Use `calculate_combined_period(phases)` for review length instead of `calculate_period()`
- Build per-phase placeholder replacements in a loop
- Lint `report.md` against each phase's internal org/repo (so links from all 3 repos get replaced)

### 6. Source content files (manual merge)

- **`protocol_summary.md`** — Write a unified description covering all phases. Incorporate new contracts/features from later phases into the base description rather than having separate sections.
- **`audit_scope.md`** — Subsection per phase listing the files/PRs in scope for that phase.
- **`executive_summary.md`** — Subsection per phase summarizing findings.
- **`lead_auditors.md`** — Union of all auditors across phases.

## Running locally

```bash
cd combined-report/

# Ensure GITHUB_ACCESS_TOKEN is set in your environment
# (e.g. in your shell profile — no .env file needed)

# Install dependencies (one-time)
pip3 install -r requirements.txt

# Generate
python3 generate_report.py
# PDF appears at output/report.pdf
```

Prerequisites: Python 3, Pandoc, pdflatex (TeX Live / MacTeX).

## Notes

- The `GITHUB_ACCESS_TOKEN` needs `repo` scope to access private Cyfrin repos. The `read:org` scope is also helpful for project column filtering but not required — without it, the script falls back to fetching all open issues.
- Issues from different repos may have overlapping issue numbers (`#1`, `#2`, etc.). Internal `#xx` link replacement is done per-repo before merging, so there are no collisions.
- The summary findings table entries (`[H-1]`, `[L-2]`, etc.) are numbered sequentially across all phases — they don't indicate which phase a finding came from. The TOC does show this grouping though.
- If the number of phases exceeds 3, the Audit Phases table layout will need adjustment (narrower columns or multiple rows).
