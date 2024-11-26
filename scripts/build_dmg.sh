#!/bin/bash

# Configuration
APP_NAME="Octavia"
VERSION="3.0.0"
DMG_NAME="${APP_NAME}-${VERSION}.dmg"
APP_PATH="dist/${APP_NAME}.app"
DMG_PATH="dist/${DMG_NAME}"
VOLUME_NAME="${APP_NAME} ${VERSION}"

# Ensure the app exists
if [ ! -d "$APP_PATH" ]; then
    echo "Error: $APP_PATH not found!"
    exit 1
fi

# Code sign the app
echo "Code signing ${APP_NAME}.app..."
codesign --force --deep --sign "Developer ID Application" "$APP_PATH"

# Create DMG
echo "Creating DMG..."
# Create temporary DMG
hdiutil create -srcfolder "$APP_PATH" -volname "$VOLUME_NAME" -fs HFS+ \
        -fsargs "-c c=64,a=16,e=16" -format UDRW -size 200m "dist/temp.dmg"

# Mount the temporary DMG
MOUNT_DIR="/Volumes/$VOLUME_NAME"
DEV_NAME=$(hdiutil attach -readwrite -noverify -noautoopen "dist/temp.dmg" | \
         egrep '^/dev/' | sed 1q | awk '{print $1}')

# Wait for the mount
sleep 2

# Set volume icon position
echo '
   tell application "Finder"
     tell disk "'${VOLUME_NAME}'"
           open
           set current view of container window to icon view
           set toolbar visible of container window to false
           set statusbar visible of container window to false
           set the bounds of container window to {400, 100, 885, 430}
           set theViewOptions to the icon view options of container window
           set arrangement of theViewOptions to not arranged
           set icon size of theViewOptions to 72
           set position of item "'${APP_NAME}.app'" of container window to {100, 100}
           close
           open
           update without registering applications
           delay 2
           close
     end tell
   end tell
' | osascript

# Convert and compress
echo "Converting DMG..."
hdiutil detach "${DEV_NAME}"
hdiutil convert "dist/temp.dmg" -format UDZO -imagekey zlib-level=9 -o "$DMG_PATH"
rm -f "dist/temp.dmg"

# Sign the DMG
echo "Signing DMG..."
codesign --sign "Developer ID Application" "$DMG_PATH"

echo "Done! Created ${DMG_PATH}"
