"""Unit tests for the pure-logic helpers in scripts/helpers.py.

These cover the text/markdown/LaTeX transformations and the date math used
when generating a report. None of them touch the network, GitHub or pandoc.
"""
import pytest

from scripts import helpers


class TestGetIssueCount:
    def test_counts_present_label(self):
        d = {"Severity: High Risk": ["a", "b", "c"]}
        assert helpers.get_issue_count(d, "Severity: High Risk") == 3

    def test_missing_label_is_zero(self):
        assert helpers.get_issue_count({}, "Severity: Low Risk") == 0

    def test_empty_list_is_zero(self):
        assert helpers.get_issue_count({"x": []}, "x") == 0


class TestTitleToLink:
    def test_basic_slug(self):
        assert helpers.title_to_link("Hello World") == "[*Hello World*](#hello-world)"

    def test_strips_non_alphanumeric_and_keeps_title(self):
        # Backticks/parens are dropped from the anchor but kept in the visible title.
        result = helpers.title_to_link("Reentrancy in `withdraw()`")
        assert result == "[*Reentrancy in `withdraw()`*](#reentrancy-in-withdraw)"

    def test_multiple_spaces_and_symbols(self):
        assert helpers.title_to_link("A & B: C") == "[*A & B: C*](#a--b-c)"


class TestReplaceInternalLinks:
    def test_replaces_known_issue_number(self):
        issues = {"Severity: High Risk": ["This duplicates issue #12 entirely"]}
        issues_by_number = {12: "Some Other Bug"}
        out = helpers.replace_internal_links(issues, issues_by_number)
        assert out["Severity: High Risk"][0] == (
            "This duplicates issue " + helpers.title_to_link("Some Other Bug") + " entirely"
        )

    def test_unknown_issue_number_exits(self):
        issues = {"Severity: High Risk": ["see #99 here"]}
        with pytest.raises(SystemExit):
            helpers.replace_internal_links(issues, {})

    def test_no_reference_is_unchanged(self):
        issues = {"Severity: Low Risk": ["nothing to link here"]}
        out = helpers.replace_internal_links(issues, {})
        assert out["Severity: Low Risk"][0] == "nothing to link here"


class TestEscapeLatexSpecialChars:
    def test_escapes_all_specials(self):
        assert helpers.escape_latex_special_chars("100% & $5 #1") == "100\\% \\& \\$5 \\#1"

    def test_tilde_and_caret(self):
        assert helpers.escape_latex_special_chars("a~b^c") == "a\\textasciitilde{}b\\textasciicircum{}c"

    def test_plain_text_unchanged(self):
        assert helpers.escape_latex_special_chars("nothing special") == "nothing special"


class TestFormatInlineCode:
    def test_wraps_backticks_and_escapes_underscores(self):
        assert helpers.format_inline_code("call `my_func`") == "call \\texttt{my\\_func}"

    def test_text_without_backticks_unchanged(self):
        assert helpers.format_inline_code("no code here") == "no code here"

    def test_multiple_segments(self):
        assert helpers.format_inline_code("`a_b` and `c`") == "\\texttt{a\\_b} and \\texttt{c}"


class TestCalculatePeriod:
    def test_full_week_excludes_weekend(self):
        # Jan 1 2024 is a Monday; Jan 1-7 has 5 workdays (Mon-Fri).
        assert helpers.calculate_period("Jan 1st - Jan 7th, 2024") == 5

    def test_single_workday(self):
        assert helpers.calculate_period("Jan 1st - Jan 1st, 2024") == 1

    def test_year_boundary_rolls_start_back(self):
        # Dec 31 2024 > Jan 1 2024, so start rolls back to Dec 31 2023 (a Sunday).
        # Range Dec 31 2023 (Sun) -> Jan 1 2024 (Mon) has a single workday.
        assert helpers.calculate_period("Dec 31st - Jan 1st, 2024") == 1


class TestReplaceInFileContent:
    def test_replaces_only_placeholder_lines(self):
        content = ["__PLACEHOLDER__NAME goes here", "untouched line"]
        out = helpers.replace_in_file_content(content, [["__PLACEHOLDER__NAME", "Acme"]])
        assert out == ["Acme goes here", "untouched line"]

    def test_longest_placeholder_first(self):
        # Sorted by length desc so __PLACEHOLDER__FOO_BAR is replaced before __PLACEHOLDER__FOO.
        content = ["__PLACEHOLDER__FOO_BAR"]
        out = helpers.replace_in_file_content(
            content,
            [["__PLACEHOLDER__FOO", "short"], ["__PLACEHOLDER__FOO_BAR", "long"]],
        )
        assert out == ["long"]


class TestJoinWithAmpersand:
    def test_single(self):
        assert helpers.join_with_ampersand(["A"]) == "A"

    def test_two(self):
        assert helpers.join_with_ampersand(["A", "B"]) == "A \\& B"

    def test_three(self):
        assert helpers.join_with_ampersand(["A", "B", "C"]) == "A, B \\& C"


class TestBuildFindingsSentence:
    def _counts(self, **kw):
        base = {k: 0 for k in ("critical", "high", "medium", "low", "informational", "gas_optimization")}
        base.update(kw)
        return base

    def test_empty_returns_empty_string(self):
        assert helpers.build_findings_sentence(self._counts()) == ""

    def test_single_core_issue_singular_noun(self):
        s = helpers.build_findings_sentence(self._counts(high=1))
        assert s == " The findings consist of 1 High severity issue."

    def test_multiple_core_issues_plural(self):
        s = helpers.build_findings_sentence(self._counts(high=2, low=1))
        assert s == " The findings consist of 2 High \\& 1 Low severity issues."

    def test_core_with_info_and_gas_remainder(self):
        s = helpers.build_findings_sentence(self._counts(high=1, informational=2, gas_optimization=3))
        assert s.endswith("with the remainder being informational and gas optimizations.")

    def test_only_informational(self):
        s = helpers.build_findings_sentence(self._counts(informational=4))
        assert s == " The findings consist of 4 Informational."
