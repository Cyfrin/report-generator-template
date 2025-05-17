import os
import requests
import re
from dotenv import load_dotenv
from github import Github
from .helpers import get_issues, get_summary_information


load_dotenv()

# Load github repo information and personal access token
REPO = get_summary_information()['private_github']
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
github = Github(GITHUB_TOKEN)

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
    filter_issue_column = summary_info.get('filter_issue_column', 'Report')

    # Parse the GitHub repository string to get owner and repo name
    repo_owner, repo_name = extract_github_owner_repo(REPO)

    if not repo_owner or not repo_name:
        print(f"Invalid repository format: {REPO}")
        print("Expected format: owner/repo or https://github.com/owner/repo")
        return 0

    print(f"Extracted owner: {repo_owner}, repo: {repo_name} from {REPO}")

    # Initialize combined issue ID list
    combined_issue_ids = [str(id) for id in filter_issue_id_list] if filter_issue_id_list else []

    # Filter by project column if specified
    project_number = summary_info.get('project_number')
    if filter_issue_column and project_number:
        # Validate project_number is not empty
        if not str(project_number).strip():
            print("Warning: project_number is empty in config. Skipping project column filtering.")
        else:
            try:
                # Convert to integer and handle potential errors
                project_number = int(project_number)

                print(f"Fetching issues from column '{filter_issue_column}' in project #{project_number}...")
                column_issue_numbers = get_issues_in_column(
                    repo_owner,
                    repo_name,
                    project_number,
                    filter_issue_column
                )

                if column_issue_numbers:
                    print(f"Found {len(column_issue_numbers)} issues in column '{filter_issue_column}'")

                    # If we already have issue IDs from the config, use both filters (intersection)
                    if combined_issue_ids:
                        # Convert both lists to sets of strings for intersection
                        config_ids_set = set(combined_issue_ids)
                        column_ids_set = set(str(num) for num in column_issue_numbers)
                        combined_issue_ids = list(config_ids_set.intersection(column_ids_set))
                        print(f"After combining with issue ID list: {len(combined_issue_ids)} issues")
                    else:
                        # Just use the column filter
                        combined_issue_ids = [str(num) for num in column_issue_numbers]
                else:
                    print(f"No issues found in column '{filter_issue_column}' or column not found in project")
                    # If we got zero issues from column filtering but had explicit issue IDs, keep those
                    if not combined_issue_ids:
                        print("Warning: No issues match the filter criteria. Will fetch all issues.")
            except ValueError:
                print(f"Warning: Invalid project number '{project_number}'. Must be an integer. Skipping project column filtering.")
            except Exception as e:
                print(f"Warning: Failed to filter by project column: {e}")
                print("Detailed error info: ", str(e))
                # Continue without column filtering

    # Prepare filter options for get_issues
    filter_options = {
        'issue_ids': combined_issue_ids if combined_issue_ids else None,
        'label': filter_issue_label if filter_issue_label else None
    }

    # Get all issues from the repo. This will create `report.md` and `severity_counts.conf`
    print(f"Fetching issues from repository {REPO} with filters...")
    issues_obtained = get_issues(REPO, github, filter_options)
    if(issues_obtained) > 0:
        print(f"Done. {issues_obtained} issues obtained.\n")
    else:
        print(f"Done. No issues obtained.\n")


# GitHub Project API Functions

def run_graphql_query(query, variables=None):
    """Run a GraphQL query against GitHub's API"""
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
    }
    
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    response = requests.post("https://api.github.com/graphql", json=payload, headers=headers)
    
    # Check for HTTP errors
    response.raise_for_status()
    
    # Parse the response
    response_data = response.json()
    
    # Check for GraphQL errors
    if "errors" in response_data:
        error_message = "; ".join([error.get("message", "Unknown error") for error in response_data["errors"]])
        raise Exception(f"GraphQL Error: {error_message}")
    
    return response_data

def get_organization_id(org_name):
    """Get organization node ID from organization name"""
    print(f"Looking up organization: {org_name}")
    query = """
    query($login: String!) {
        organization(login: $login) {
            id
        }
    }
    """
    variables = {"login": org_name}
    try:
        result = run_graphql_query(query, variables)
        
        # Check if organization data exists
        if not result.get("data") or not result["data"].get("organization"):
            raise Exception(f"Organization '{org_name}' not found. Check the repository owner name.")
            
        return result["data"]["organization"]["id"]
    except Exception as e:
        print(f"Could not find organization '{org_name}', trying as user instead: {str(e)}")
        # Try as a user instead
        return get_user_id(org_name)

def get_user_id(user_name):
    """Get user node ID from username"""
    print(f"Looking up user: {user_name}")
    query = """
    query($login: String!) {
        user(login: $login) {
            id
        }
    }
    """
    variables = {"login": user_name}
    result = run_graphql_query(query, variables)
    
    # Check if user data exists
    if not result.get("data") or not result["data"].get("user"):
        raise Exception(f"User '{user_name}' not found. Check the repository owner name.")
        
    return result["data"]["user"]["id"]

def get_project_id(owner_id, project_number):
    """Get project ID from owner ID and project number"""
    print(f"Looking up project #{project_number} for owner ID: {owner_id}")
    query = """
    query($ownerId: ID!, $number: Int!) {
        node(id: $ownerId) {
            ... on Organization {
                projectV2(number: $number) {
                    id
                }
            }
            ... on User {
                projectV2(number: $number) {
                    id
                }
            }
        }
    }
    """
    variables = {"ownerId": owner_id, "number": project_number}
    result = run_graphql_query(query, variables)
    
    # Check if node data exists
    if not result.get("data") or not result["data"].get("node"):
        raise Exception(f"Node with ID '{owner_id}' not found")
    
    # Check if owner has a project with the given number
    node_data = result["data"]["node"]
    if not node_data.get("projectV2"):
        raise Exception(f"Project #{project_number} not found for the given owner. Check your project_number in the config.")
    
    return node_data["projectV2"]["id"]

def get_issues_in_column(repo_owner, repo_name, project_number, column_name):
    """
    Get issues that are in a specific column of a GitHub project
    
    Args:
        repo_owner: GitHub username or organization name
        repo_name: Repository name
        project_number: Project number (from URL)
        column_name: Column name to filter by (e.g., "Report")
        
    Returns:
        List of issue numbers in the specified column
    """
    try:
        # First get the organization ID
        print(f"Looking up owner ID for '{repo_owner}'...")
        org_id = get_organization_id(repo_owner)
        
        # Get the project ID
        print(f"Looking up project ID for project #{project_number}...")
        project_id = get_project_id(org_id, project_number)
        
        # Get the field ID for the Status field
        print(f"Looking for column '{column_name}' in project...")
        query = """
        query($projectId: ID!) {
            node(id: $projectId) {
                ... on ProjectV2 {
                    fields(first: 20) {
                        nodes {
                            ... on ProjectV2SingleSelectField {
                                id
                                name
                                options {
                                    id
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        variables = {"projectId": project_id}
        result = run_graphql_query(query, variables)
        
        # Check if node data exists and has fields
        if (not result.get("data") or 
            not result["data"].get("node") or 
            not result["data"]["node"].get("fields") or 
            not result["data"]["node"]["fields"].get("nodes")):
            raise Exception("Failed to get project fields")
        
        status_field = None
        column_option_id = None
        
        # List available fields and options for debugging
        print("Available fields in project:")
        
        for field in result["data"]["node"]["fields"]["nodes"]:
            if field and "name" in field:
                print(f"  - Field: {field.get('name', 'Unnamed')}")
                
                if "options" in field:
                    print(f"    Options: {', '.join([opt.get('name', 'Unnamed') for opt in field['options']])}")
                    
                    for option in field["options"]:
                        if option["name"] == column_name:
                            status_field = field["id"]
                            column_option_id = option["id"]
                            print(f"    Found column '{column_name}' in field '{field.get('name', 'Unnamed')}'")
                            break
                if status_field:
                    break
        
        if not status_field or not column_option_id:
            print(f"Column '{column_name}' not found in any project field")
            return []
        
        # Get all items in the project that are in the specified column
        print("Fetching issues in the specified column...")
        query = """
        query($projectId: ID!) {
            node(id: $projectId) {
                ... on ProjectV2 {
                    items(first: 100) {
                        nodes {
                            id
                            fieldValues(first: 100) {
                                nodes {
                                    ... on ProjectV2ItemFieldSingleSelectValue {
                                        name
                                        optionId
                                        field {
                                            ... on ProjectV2FieldCommon {
                                                id
                                                name
                                            }
                                        }
                                    }
                                }
                            }
                            content {
                                ... on Issue {
                                    number
                                    repository {
                                        name
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        variables = {
            "projectId": project_id
        }
        
        result = run_graphql_query(query, variables)
        
        # Check if we got valid items data
        if (not result.get("data") or 
            not result["data"].get("node") or 
            not result["data"]["node"].get("items") or 
            not result["data"]["node"]["items"].get("nodes")):
            raise Exception("Failed to get project items")
        
        # Filter items that are in the specified column and match the repository
        issue_numbers = []
        items = result["data"]["node"]["items"]["nodes"]
        
        for item in items:
            # Check if the item is in the specified column
            in_column = False
            if item.get("fieldValues", {}).get("nodes"):
                for field_value in item["fieldValues"]["nodes"]:
                    if (field_value and 
                        field_value.get("field", {}).get("id") == status_field and 
                        field_value.get("optionId") == column_option_id):
                        in_column = True
                        break
            
            # Check if the item is from the specified repository and is an issue
            if in_column and item.get("content") and "number" in item["content"]:
                if item["content"].get("repository", {}).get("name") == repo_name:
                    issue_numbers.append(item["content"]["number"])
        
        return issue_numbers
    except Exception as e:
        print(f"Error in get_issues_in_column: {str(e)}")
        raise
