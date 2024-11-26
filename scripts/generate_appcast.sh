#!/bin/bash

# Configuration
APP_NAME="Octavia"
VERSION="3.0.0"
DMG_NAME="${APP_NAME}-${VERSION}.dmg"
DMG_PATH="dist/${DMG_NAME}"

# Generate Sparkle signature
echo "Generating Sparkle signature for ${DMG_NAME}..."
SIGNATURE=$(/usr/local/bin/generate_appcast dist/)

# Extract the signature
ED_SIGNATURE=$(echo "$SIGNATURE" | grep "sparkle:edSignature=" | cut -d'"' -f2)

# Update the appcast.xml with the new signature
sed -i '' "s/sparkle:edSignature=\"\"/sparkle:edSignature=\"$ED_SIGNATURE\"/" appcast.xml

echo "Updated appcast.xml with new signature"
