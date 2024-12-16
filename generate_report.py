import re
import subprocess
import scripts.helpers as helpers
import scripts.linter as linter
from scripts.fetch_issues import fetch_issues

# Get issues
fetch_issues()

# Get static info from conf files
summary_data = helpers.get_summary_information()
severity_count_data = helpers.get_severity_counts()

# Project name taken from summary_information.conf, inserted in Title section -> title.tex file
REPLACE_TITLE = [["__PLACEHOLDER__PROJECT_NAME", summary_data['project_name']],
                 ["__PLACEHOLDER__REPORT_VERSION", summary_data['report_version']]]

pattern = r'/(?P<org_name>[^/]+)/([^/]+?)(?=/(?:src|branch)|\.git|$)'
source_org, source_repo_name = re.search(pattern, summary_data['project_github']).groups()
source_org, source_repo_name_2 = re.search(pattern, summary_data['project_github_2']).groups()
source_org, source_repo_name_3 = re.search(pattern, summary_data['project_github_3']).groups()
internal_org, internal_repo_name = re.search(pattern, summary_data['private_github']).groups()

# Information from summary_information.conf, inserted in Summary section -> summary.tex file
REPLACE_SUMMARY = [["__PLACEHOLDER__REVIEW_LENGTH", str(helpers.calculate_period(summary_data['review_timeline']))],
                   ["__PLACEHOLDER__TEAM_NAME", summary_data['team_name']],
                   ["__PLACEHOLDER__TEAM_WEBSITE", summary_data['team_website']],
                   ["__PLACEHOLDER__PROJECT_NAME", summary_data['project_name']],
                   ["__PLACEHOLDER__REPO_LINK_3", summary_data['project_github_3']],
                   ["__PLACEHOLDER__REPO_NAME_3", source_repo_name_3],
                   ["__PLACEHOLDER__COMMIT_HASH_3_LINK", re.sub(r'(\.git)?$', '', summary_data['project_github_3']) + "/blob/" + summary_data['commit_hash_3']],
                   ["__PLACEHOLDER__COMMIT_HASH_3", summary_data['commit_hash_3']],
                   ["__PLACEHOLDER__REPO_LINK_2", summary_data['project_github_2']],
                   ["__PLACEHOLDER__REPO_NAME_2", source_repo_name_2],
                   ["__PLACEHOLDER__COMMIT_HASH_2_LINK", re.sub(r'(\.git)?$', '', summary_data['project_github_2']) + "/blob/" + summary_data['commit_hash_2']],
                   ["__PLACEHOLDER__COMMIT_HASH_2", summary_data['commit_hash_2']],
                   ["__PLACEHOLDER__REPO_LINK", summary_data['project_github']],
                   ["__PLACEHOLDER__REPO_NAME", source_repo_name],
                   ["__PLACEHOLDER__COMMIT_HASH_LINK", re.sub(r'(\.git)?$', '', summary_data['project_github']) + "/blob/" + summary_data['commit_hash']],
                   ["__PLACEHOLDER__COMMIT_HASH", summary_data['commit_hash']],
                   ["__PLACEHOLDER__FIX_COMMIT_HASH_LINK", re.sub(r'(\.git)?$', '', summary_data['project_github']) + "/blob/" + summary_data['fix_commit_hash'] if summary_data['fix_commit_hash'] else ""],
                   ["__PLACEHOLDER__FIX_COMMIT_HASH", summary_data['fix_commit_hash'] or ""],
                   ["__PLACEHOLDER__FIX_COMMIT_HASH_LINK_2", re.sub(r'(\.git)?$', '', summary_data['project_github_2']) + "/blob/" + summary_data['fix_commit_hash_2'] if summary_data['fix_commit_hash_2'] else ""],
                   ["__PLACEHOLDER__FIX_COMMIT_HASH_2", summary_data['fix_commit_hash_2'] or ""],
                   ["__PLACEHOLDER__FIX_COMMIT_HASH_LINK_3", re.sub(r'(\.git)?$', '', summary_data['project_github_3']) + "/blob/" + summary_data['fix_commit_hash_3'] if summary_data['fix_commit_hash_3'] else ""],
                   ["__PLACEHOLDER__FIX_COMMIT_HASH_3", summary_data['fix_commit_hash_3'] or ""],
                   ["__PLACEHOLDER__AUDIT_TIMELINE", summary_data['review_timeline']],
                   ["__PLACEHOLDER__AUDIT_METHODS", summary_data['review_methods']]]


# Severities count taken from severity_count.conf, inserted in Total Issues section -> summary.tex file
REPLACE_SEVERITIES = [["__PLACEHOLDER__ISSUE_CRITICAL_COUNT", severity_count_data['critical']],
                      ["__PLACEHOLDER__ISSUE_HIGH_COUNT", severity_count_data['high']],
                      ["__PLACEHOLDER__ISSUE_MEDIUM_COUNT", severity_count_data['medium']],
                      ["__PLACEHOLDER__ISSUE_LOW_COUNT", severity_count_data['low']],
                      ["__PLACEHOLDER__ISSUE_INFORMATIONAL_COUNT" ,severity_count_data['informational']],
                      ["__PLACEHOLDER__ISSUE_GAS_OPTIMIZATION_COUNT", severity_count_data['gas_optimization']],
                      ["__PLACEHOLDER__ISSUE_TOTAL_COUNT", severity_count_data['total']]]



# Lint the report.md
print("Linting the report.md file ...")
report = helpers.get_file_contents(helpers.SOURCE_REPORT)
report = linter.lint(report, summary_data['team_name'], source_org, source_repo_name, internal_org, internal_repo_name)
helpers.save_file_contents(helpers.SOURCE_REPORT, report)
print(f"Done.\n")

# Convert all .md to .tex and save to working dir
print("Converting Markdown files to LaTeX ...")
with open("./working/conversion.log", "w") as log:
    subprocess.call("./scripts/convert.sh", stdout=log, stderr=log)
print(f"Done.\n")

# Process for title.tex: Get the file and replace placeholders.
print("Replacing information in title.tex ...")
title = helpers.get_file_contents("./templates/title.tex")
title = helpers.replace_in_file_content(title, REPLACE_TITLE)
helpers.save_file_contents("./working/title.tex", title)
print(f"Done.\n")

# Process for summary.tex: Get the file and replace placeholders.
print("Replacing information in summary.tex ...")
summary = helpers.get_file_contents("./templates/summary.tex")
summary = helpers.replace_in_file_content(summary, REPLACE_SUMMARY)
summary = helpers.replace_in_file_content(summary, REPLACE_SEVERITIES)
helpers.save_file_contents("./working/summary.tex", summary)
print(f"Done.\n")

# Generate PDF in output folder
print("Generating report PDF file ...")
with open("./working/generation.log", "w") as log:
    # This is actually repeated by the GitHub Action, but it's useful to have it here for running locally
    subprocess.call("./scripts/generate.sh", stdout=log, stderr=log)
# Edit the report markdown for Solodit, after everything else is complete
helpers.edit_report_md()
print(f"\nAll tasks completed. Report should be in the 'output' folder.")
print(f"If it wasn't generated, check 'working/conversion.log' and 'working/generation.log'.")
