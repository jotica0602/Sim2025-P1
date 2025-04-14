#!/bin/bash

# Ruta del archivo LaTeX
DIR="report"
FILE="report"
PDF="$FILE.pdf"

# Función para compilar y limpiar
build_report() {
    echo "🔨 Compilando $FILE.tex..."
    cd "$DIR" || exit

    pdflatex "$FILE.tex" > /dev/null

    if grep -q "\\bibliography" "$FILE.tex"; then
        echo "📚 Procesando bibliografía..."
        bibtex "$FILE" > /dev/null
    fi

    pdflatex "$FILE.tex" > /dev/null
    pdflatex "$FILE.tex" > /dev/null

    echo "🧹 Eliminando archivos temporales..."
    find . -type f ! -name "$FILE.tex" ! -name "$PDF" -delete

    cd - > /dev/null
    echo "✅ Reporte generado: $DIR/$PDF"
}

# Función para abrir el PDF
open_report() {
    PDF_PATH="$DIR/$PDF"
    if [ -f "$PDF_PATH" ]; then
        echo "📖 Abriendo $PDF_PATH..."
        xdg-open "$PDF_PATH" > /dev/null 2>&1 &
    else
        echo "❌ El archivo $PDF_PATH no existe. Primero compilalo."
    fi
}

# Menú interactivo
while true; do
    echo ""
    echo "=== Gestor de Reporte ==="
    echo "1) Compilar y limpiar"
    echo "2) Abrir PDF"
    echo "3) Salir"
    read -rp "Selecciona una opción [1-3]: " option

    case $option in
        1) build_report ;;
        2) open_report ;;
        3) echo "👋 Saliendo..."; break ;;
        *) clear && echo "❗ Opción inválida. Intenta de nuevo." ;;
    esac
done
