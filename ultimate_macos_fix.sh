#!/bin/bash
# Ultimate macOS app fix script
# This will remove all quarantine and security restrictions

APP_PATH="dist/SMWC Downloader.app"

echo "🍎 Ultimate macOS App Fix"
echo "========================="

if [ ! -d "$APP_PATH" ]; then
    echo "❌ App not found: $APP_PATH"
    exit 1
fi

echo "🔧 Removing all quarantine attributes..."
xattr -cr "$APP_PATH" 2>/dev/null || true

echo "🔧 Setting all permissions..."
chmod -R 755 "$APP_PATH"
chmod +x "$APP_PATH/Contents/MacOS"/*

echo "🔧 Removing any existing signatures..."
codesign --remove-signature "$APP_PATH" 2>/dev/null || true

echo "🔧 Adding app to system allowlist..."
spctl --add "$APP_PATH" 2>/dev/null || true
spctl --enable "$APP_PATH" 2>/dev/null || true

echo "🔧 Bypassing Gatekeeper for this app..."
xattr -d com.apple.quarantine "$APP_PATH" 2>/dev/null || true
xattr -d com.apple.metadata:kMDItemWhereFroms "$APP_PATH" 2>/dev/null || true

echo "🔧 Re-signing with entitlements..."
codesign --force --deep --sign - --entitlements - "$APP_PATH" <<EOF 2>/dev/null || true
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.network.server</key>
    <true/>
</dict>
</plist>
EOF

echo "🔧 Final permission fix..."
chmod -R 755 "$APP_PATH"

echo "✅ Ultimate fix complete!"
echo ""
echo "🎯 Testing app launch..."
open "$APP_PATH" && echo "✅ App launched successfully!" || echo "❌ App launch failed"
