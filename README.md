# A Markdown based template for writing audit reports
Forked from [Spearbit](https://github.com/spearbit-audits/report-generator-template).

## Introduction

This repository is meant to be a single-step solution to:

- Fetch all issues from a given repository
- Sort them by severity according to their labels
- Generate a single Markdown file with all issues sorted by descending severity
- Integrate that Markdown file into a LaTeX template
- Generate a PDF report with all the issues and other relevant information

## Directory structure

There are five directories:

- `source`: Contains the source Markdown files with all information needed for the report.
- `scripts`: Contains various scripts needed to convert files and generate the PDF.
- `templates`: The LaTeX files used as template for the final report.
- `output`: Output directory where the final report will be saved. All files can be safely erased.
- `working`: A directory where the temporary files will be stored. All files can be safely erased.

## Usage

### Pre-requisites
1. [Pandoc](https://pandoc.org/)
2. [LaTeX](https://www.latex-project.org/get/).

### Install from source

Clone this repository and install dependencies:
```bash
https://github.com/Cyfrin/report-generator-template.git
cd report-generator-template
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Fetching issues

By default, the script will attempt to fetch issues from the repository given by the `private_github` configuration variable specified in `source/summary_information.conf`. If this is not desired, for now simply comment-out [this line](https://github.com/Cyfrin/report-generator-template/blob/a7345b98278bcd4634049a74d41d5d02f3831f7d/generate_report.py#L8) in `generate_report.py` and replace with your own method for generating `report.md`, either with another tool (such as [`trello_to_audit_report`](https://github.com/Cyfrin/trello_to_audit_report/tree/main)) or creating the file manually.

### GitHub Personal Access Token

To fetch the issues from a repository, a [GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) is required. The `.github/workflows/main.yml` GitHub Action is configured to use the default GitHub secret `GITHUB_TOKEN` but if planning to run this tool locally, please follow the docs to generate a personal access token and then set it as an environment variable if this functionality is desired:

```bash
export GITHUB_TOKEN=your-github-token
```

### Edit contents

Check contents and **manually update** the following files in `source/`:

- `about_cyfrin.md`: Cyfrin description.
- `additional_comments.md`: For extra information at the end of the report. It is commented by DEFAULT, please change if required.
- `appendix.md`: For extra information at the end of the report. It is commented by DEFAULT, please change if required.
- `assisting_auditors.md`: List of lead auditors who participated during the engagement.
- `audit_scope.md`: Information about the audit scope, including relevant files, commit hashes and pull requests.
- `disclaimer.md`: Information about the audit review process.
- `executive_summary.md`: Information about the audit findings and other executive comments.
- `lead_auditors.md`: List of lead auditors who participated during the engagement.
- `protocol_summary.md`: Information about the protocol.
- `summary_information.conf`: Information to be replaced in the title page and the summary.

All `.md` files can be formatted and will be converted to LaTeX by the scripts located in `scripts/`.

The `.conf` files store text-only information and are replaced verbatim in the final report. This means all
formatting should be removed, as the template already contains formatting.

### Generate report

Once all information is filled in, the creation
of the `report.pdf` file in `output` is achieved by running:

```bash
python generate_report.py
```

The `report.md` and `severity_counts.conf` files will be automatically
generated from the issues in the repository. Temporary files will be created in `working`, and they can be safely
deleted after the report is generated.

By default, there are `.gitignore` rules in place to avoid tracking the following:

- Any file in `working` (except its own `.gitignore`)
- Any file in `output` (except its own `.gitignore`)
- `source/report.md` and `source/severity_counts.conf` as they are automatically generated

### Additional notes

This tool can be used stand-alone but is primarily intended to be used alongside [`audit-repo-cloner`](https://github.com/Cyfrin/audit-repo-cloner), another tool that will take a repository for audit and create a private copy prepared for Cyfrin audit. This repo is installed as a subtree of the cloned audit repo and makes use of GitHub Actions to automatically generate the report.

If intending to use this tool on its own, be sure to consider the public visibility of this repository and the security implications if the final report will contain sensitive information. If this is the case, it is recommended to create a private copy of this repository as forks are public by default.

Additionally, given source and output files will need to be overwritten when generating multiple reports, it is recommended to create a new branch for each report and merge the final `.pdf` file into `main` when the report is complete.

### Known issues
- Issue titles with special characters may cause the LaTeX compilation to fail or freeze forever. If this happens, please edit the issue title to remove the special characters. (especially '&')
- If the issue title is too long, it may cause the LaTeX compilation to fail. If this happens, please edit the issue title to make it shorter.
