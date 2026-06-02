"""Smoke tests that the upgraded third-party dependencies import and behave as
the code expects. These guard against breaking changes from dependency bumps
(notably the PyGithub 1.x -> 2.x upgrade).
"""
import importlib


def test_core_libraries_import():
    for mod in ("requests", "dateutil.parser", "dotenv", "pandocfilters", "github"):
        importlib.import_module(mod)


def test_pygithub_client_constructs_with_auth_token():
    # fetch_issues builds `Github(auth=Auth.Token(...))`; ensure the
    # non-deprecated Auth API is present and usable on the installed PyGithub.
    from github import Auth, Github

    client = Github(auth=Auth.Token("dummy-token-not-used"))
    assert client is not None


def test_pygithub_anonymous_client_constructs():
    # fetch_issues falls back to an anonymous client when no token is set.
    from github import Github

    assert Github() is not None


def test_dateutil_parse_used_by_calculate_period():
    from dateutil.parser import parse
    from datetime import datetime

    parsed = parse("Apr 25th", default=datetime(2026, 1, 1))
    assert parsed.year == 2026 and parsed.month == 4 and parsed.day == 25


def test_fetch_issues_module_imports():
    # Importing this module runs top-level code that reads source config and
    # constructs a Github client — a good end-to-end check that the upgraded
    # PyGithub/requests/dotenv stack still wires together.
    import scripts.fetch_issues as fetch_issues

    assert hasattr(fetch_issues, "fetch_issues")
    assert hasattr(fetch_issues, "extract_github_owner_repo")


def test_extract_github_owner_repo_variants():
    from scripts.fetch_issues import extract_github_owner_repo

    assert extract_github_owner_repo("https://github.com/Cyfrin/audit-repo") == ("Cyfrin", "audit-repo")
    assert extract_github_owner_repo("https://github.com/Cyfrin/audit-repo.git") == ("Cyfrin", "audit-repo")
    assert extract_github_owner_repo("Cyfrin/audit-repo") == ("Cyfrin", "audit-repo")
    assert extract_github_owner_repo("not a repo") == (None, None)
