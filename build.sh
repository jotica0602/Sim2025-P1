#!/bin/bash
py src/sim.py &&

TEX_FILE="report/informe.tex"
PDF_FILE="report/informe.pdf"

# Compiling
echo "Compilando $TEX_FILE..."
latexmk -pdf -output-directory=report "$TEX_FILE"

# Verifying
if [ -f "$PDF_FILE" ]; then
    echo "✔ Build successful: $PDF_FILE"
else
    echo "❌ Build error"
    exit 1
fi

echo "Cleaning temps..."
latexmk -c -output-directory=report "$TEX_FILE"

echo "Showing report..."
xdg-open "$PDF_FILE" >/dev/null 2>&1 &
