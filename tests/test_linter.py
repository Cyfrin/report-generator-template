"""Unit tests for scripts/linter.py — markdown link rewriting and validation."""
import pytest

from scripts import linter


class TestReplaceOrgInLink:
    def test_replaces_internal_org(self):
        line = "See https://github.com/InternalOrg/internal-repo/blob/x for details"
        out = linter.replace_org_in_link(
            line,
            internal_org="InternalOrg",
            internal_repo_name="internal-repo",
            source_org="SourceOrg",
            source_repo_name="source-repo",
        )
        assert out == "See https://github.com/SourceOrg/source-repo/blob/x for details"

    def test_same_repo_name_only_swaps_org(self):
        line = "https://github.com/InternalOrg/shared/tree/main"
        out = linter.replace_org_in_link(
            line, "InternalOrg", "shared", "SourceOrg", "shared"
        )
        assert out == "https://github.com/SourceOrg/shared/tree/main"

    def test_unrelated_link_untouched(self):
        line = "https://example.com/InternalOrg-lookalike"
        out = linter.replace_org_in_link(
            line, "NotPresentOrg", "repo", "SourceOrg", "repo"
        )
        assert out == line


class TestLint:
    def _args(self):
        # team_name, source_org, source_repo_name, internal_org, internal_repo_name
        return ("Acme", "SourceOrg", "source-repo", "InternalOrg", "internal-repo")

    def test_broken_wrapped_link_raises(self):
        report = ["### Some Finding", "Here is a link]("]
        with pytest.raises(ValueError) as exc:
            linter.lint(report, *self._args())
        assert "Broken markdown link" in str(exc.value)
        assert "Some Finding" in str(exc.value)

    def test_link_inside_code_fence_is_ignored(self):
        # `new Type[](size)` ends a line with "](" but is code, not a broken link.
        report = ["```solidity", "uint256[] memory a = new uint256[](", "5);", "```"]
        # Should not raise.
        out = linter.lint(report, *self._args())
        assert out is report

    def test_double_backslash_collapsed(self):
        report = ["a\\\\b"]
        out = linter.lint(report, *self._args())
        assert out[0] == "a\\b"

    def test_description_merged_onto_header_line(self):
        report = ["**Description:**", "", "The actual description text."]
        out = linter.lint(report, *self._args())
        assert out[0] == "**Description:** The actual description text."
        assert "The actual description text." not in out[1:]

    def test_description_followed_by_list_not_merged(self):
        report = ["**Impact:**", "", "- bullet item"]
        out = linter.lint(report, *self._args())
        assert out[0] == "**Impact:**"
        assert "- bullet item" in out
