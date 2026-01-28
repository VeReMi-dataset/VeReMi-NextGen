#!/bin/bash

# Konfiguration
SOURCE_DIR="."
RELEASE_TAG="v1.0.0"
RELEASE_TITLE="VeReMi-NextGen"
RELEASE_NOTES="First version of the VeReMi-NextGen Dataset for Evaluation of MBD Systems"

# Temporäres Verzeichnis für ZIP-Dateien (absoluter Pfad)
TEMP_DIR="$(pwd)/temp_zips"
mkdir -p "$TEMP_DIR"

echo "Zippe Unterordner der ersten Ebene..."

# Nur direkte Unterordner durchgehen und zippen
for dir in "$SOURCE_DIR"/*/; do
    if [ -d "$dir" ]; then
        dirname=$(basename "$dir")
        
        # temp_zips Ordner überspringen (falls er im SOURCE_DIR liegt)
        if [ "$dirname" = "temp_zips" ]; then
            continue
        fi
        
        zipfile="$TEMP_DIR/${dirname}.zip"
        
        echo "Erstelle ${dirname}.zip..."
        (cd "$SOURCE_DIR" && zip -r "$zipfile" "$dirname")
    fi
done

# Prüfen ob ZIP-Dateien erstellt wurden
if [ -z "$(ls -A $TEMP_DIR 2>/dev/null)" ]; then
    echo "Fehler: Keine ZIP-Dateien erstellt. Existieren Unterordner in $SOURCE_DIR?"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "Erstelle GitHub Release und lade ZIP-Dateien hoch..."

# Release erstellen und ZIP-Dateien hochladen
gh release create "$RELEASE_TAG" "$TEMP_DIR"/*.zip \
    --title "$RELEASE_TITLE" \
    --notes "$RELEASE_NOTES"

# Aufräumen
echo "Räume auf..."
rm -rf "$TEMP_DIR"

echo "Fertig! Release erstellt: $RELEASE_TAG"
