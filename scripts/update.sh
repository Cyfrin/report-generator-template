#!/bin/bash

# This is run from the toplevel of the working tree.

git subtree pull --prefix cyfrin-report/report-generator-template https://github.com/Cyfrin/report-generator-template main --squash
cp cyfrin-report/report-generator-template/.github/workflows/main.yml .github/workflows/main.yml