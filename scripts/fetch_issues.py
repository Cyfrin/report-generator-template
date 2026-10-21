import os
import re
from dotenv import load_dotenv
from github import Auth, Github
from .helpers import get_issues, get_summary_information


load_dotenv()

# Load github repo information and personal access token
REPO = get_summary_information()['private_github'].rstrip('/')
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# Use the non-deprecated Auth.Token API when a token is available, otherwise
# fall back to an anonymous client (e.g. first clone before a token is set).
github = Github(auth=Auth.Token(GITHUB_TOKEN)) if GITHUB_TOKEN else Github()

def extract_github_owner_repo(repo_url):
    """
    Extract owner and repo name from a GitHub URL or owner/repo string
    
    Examples:
    - https://github.com/Cyfrin/audit-2025-05-untitled-bank → (Cyfrin, audit-2025-05-untitled-bank)
    - https://github.com/Cyfrin/audit-2025-05-untitled-bank.git → (Cyfrin, audit-2025-05-untitled-bank)
    - Cyfrin/audit-2025-05-untitled-bank → (Cyfrin, audit-2025-05-untitled-bank)
    """
    # First check if it's a URL
    url_pattern = r'https?://(?:www\.)?github\.com/([^/]+)/([^/\.]+)(?:\.git)?'
    url_match = re.match(url_pattern, repo_url)

    if url_match:
        return url_match.group(1), url_match.group(2)

    # If not a URL, check if it's in owner/repo format
    simple_pattern = r'^([^/]+)/([^/]+)$'
    simple_match = re.match(simple_pattern, repo_url)

    if simple_match:
        return simple_match.group(1), simple_match.group(2)

    # If we can't parse it, return None
    return None, None

def fetch_issues():
    # Get summary information for filters
    summary_info = get_summary_information()

    # Get filter options
    filter_issue_id_list = summary_info.get('filter_issue_id_list', [])
    filter_issue_label = summary_info.get('filter_issue_label', '')

    # Parse the GitHub repository string to get owner and repo name
    repo_owner, repo_name = extract_github_owner_repo(REPO)

    if not repo_owner or not repo_name:
        print(f"Invalid repository format: {REPO}")
        print("Expected format: owner/repo or https://github.com/owner/repo")
        return 0

    print(f"Extracted owner: {repo_owner}, repo: {repo_name} from {REPO}")

    # Prepare filter options for get_issues
    filter_options = {
        'issue_ids': [str(id) for id in filter_issue_id_list] if filter_issue_id_list else None,
        'label': filter_issue_label if filter_issue_label else None
    }

    # Get all issues from the repo. This will create `report.md` and `severity_counts.conf`
    print(f"Fetching issues from repository {REPO} with filters...")
    issues_obtained = get_issues(REPO, github, filter_options)
    if(issues_obtained) > 0:
        print(f"Done. {issues_obtained} issues obtained.\n")
    else:
        print(f"Done. No issues obtained.\n")

