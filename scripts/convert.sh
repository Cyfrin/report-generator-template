#!/bin/bash

# This is called from parent directory by generate_report.py to CONVERT .md to .tex
# All paths are relative to ..

# pandoc with gfm flavored markdown seems to have issues regarding
# Skipping --from gfm here
pandoc --filter ./scripts/pandoc-minted.py --filter ./scripts/pandoc-image.py --from gfm ./working/lead_auditors.md -o ./working/lead_auditors.tex
pandoc --filter ./scripts/pandoc-minted.py --filter ./scripts/pandoc-image.py --from gfm ./working/assisting_auditors.md -o ./working/assisting_auditors.tex
pandoc --filter ./scripts/pandoc-minted.py --filter ./scripts/pandoc-image.py --from gfm ./source/about_cyfrin.md -o ./working/about_cyfrin.tex
pandoc --filter ./scripts/pandoc-minted.py --filter ./scripts/pandoc-image.py --from gfm ./source/disclaimer.md -o ./working/disclaimer.tex
pandoc --filter ./scripts/pandoc-minted.py --filter ./scripts/pandoc-image.py --from gfm ./source/protocol_summary.md -o ./working/protocol_summary.tex
pandoc --filter ./scripts/pandoc-minted.py --filter ./scripts/pandoc-image.py --from gfm ./source/audit_scope.md -o ./working/audit_scope.tex
# executive_summary.md uses --from markdown (not gfm) so pandoc honours the
# dash-ratio column widths in the invariants tables. Under --from gfm, all
# columns render as auto-width (l/c) and long Property cells push Status off
# the page; --from markdown emits p{width%} columns matching the dash ratios.
pandoc --filter ./scripts/pandoc-minted.py --filter ./scripts/pandoc-image.py --from markdown ./source/executive_summary.md -o ./working/executive_summary.tex
pandoc --filter ./scripts/pandoc-minted.py --filter ./scripts/pandoc-image.py --from gfm ./source/report.md -o ./working/report.tex
pandoc --filter ./scripts/pandoc-minted.py --filter ./scripts/pandoc-image.py --from gfm ./source/additional_comments.md -o ./working/additional_comments.tex
pandoc --filter ./scripts/pandoc-minted.py --filter ./scripts/pandoc-image.py --from gfm ./source/appendix.md -o ./working/append
cp -r ./templates/* ./working/

# A temporary work around to have page breaks.
# FIXME figure out a way to natively do this.
# On macOS and Linux
sed -i.bak 's/textbackslash clearpage/clearpage/g' ./working/report.tex
# On github CI, pandoc seems to be generating the following
sed -i.bak 's/textbackslash{}clearpage/clearpage/g' ./working/report.tex
rm ./working/report.tex.bak

# Adding Needspaces before subsections and subsubsections
# Maybe 6cm is not the perfect value here, but it works good enough
sed -i '' 's/\\subsubsection/\\Needspace{6cm}\\subsubsection/g' ./working/report.tex
sed -i '' 's/\\subsection/\\Needspace{8cm}\\subsection/g' ./working/report.tex

# Allow long code listings to break pages
python3 ./scripts/code_listings.py