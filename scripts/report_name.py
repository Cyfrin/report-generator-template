"""Prints the report file name derived from source/summary_information.conf.

Used by the GitHub workflow to name the generated artifacts. Run from the
generator root as a module: python3 -m scripts.report_name
"""
import scripts.helpers as helpers

if __name__ == '__main__':
    print(helpers.get_report_name(helpers.get_summary_information()))
