#!/bin/bash

# This is called from parent directory by generate_report.py
# All paths are relative to ..

cd working

# First pass - generates .aux files
pdflatex -shell-escape -interaction nonstopmode main.tex

# Second pass - updates references and TOC
pdflatex -shell-escape -interaction nonstopmode main.tex

# Third pass - finalizes page numbers in TOC
pdflatex -shell-escape -interaction nonstopmode main.tex

cp main.pdf ../output/report.pdf