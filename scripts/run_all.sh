#!/bin/bash
# Full local rebuild from the saved raw files: both independent passes, comparison, analysis, charts, county PDF, PDF cell check,
# wiki, wiki number check, render checks, repo assembly. Publishes nothing. Any failed check stops the build (set -e) = HOLD.
set -e
cd /workspace/california-elections
python3 scripts/pass_a.py > /dev/null
python3 scripts/pass_b.py > /dev/null
python3 scripts/compare_passes.py
python3 scripts/analysis.py > /dev/null
python3 scripts/charts.py > /dev/null
python3 scripts/build_pdf.py
python3 scripts/check_pdf_cells.py
python3 scripts/build_wiki.py
python3 scripts/verify_wiki.py
python3 scripts/render_check.py verification/rendered/wiki mbenson8989/California-Election-Analysis wiki/Home.md wiki/Reverse-Math.md wiki/Locked-California-Formula.md wiki/Floor-and-Ceiling.md wiki/Graphs.md wiki/California-County-PDF-Information.md wiki/_Sidebar.md
python3 scripts/render_check.py verification/rendered/repo mbenson8989/California-Election-Analysis repo/README.md
# assemble repo folder
rm -rf repo/scripts repo/raw repo/verification repo/wiki
mkdir -p repo/scripts repo/verification repo/wiki
cp scripts/*.py scripts/*.sh repo/scripts/
cp -r raw repo/raw
cp -r verification/* repo/verification/
cp wiki/*.md repo/wiki/
echo "repo folder assembled: $(find repo -path repo/.git -prune -o -type f -print | wc -l) files"
