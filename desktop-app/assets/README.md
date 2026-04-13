# Desktop App Assets

## Icons

Place your application icons here:

- `icon.png` - 1024x1024 PNG (used for Linux AppImage)
- `icon.icns` - macOS icon bundle (use `png2icns` or iconutil)
- `icon.ico` - Windows icon (multi-resolution: 16x16, 32x32, 48x48, 256x256)

## Creating Icons

### From a PNG source image (1024x1024):

**macOS (.icns):**
```bash
mkdir icon.iconset
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset
```

**Windows (.ico):**
```bash
# Use online converter or ImageMagick
convert icon.png -define icon:auto-resize=256,64,48,32,16 icon.ico
```

## Placeholder Icons

For development, a simple blue square with "SaaS" text works:

```svg
<svg width="1024" height="1024" xmlns="http://www.w3.org/2000/svg">
  <rect width="1024" height="1024" fill="#4A90E2"/>
  <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="260" font-weight="bold" fill="white" text-anchor="middle" dominant-baseline="middle">SaaS</text>
</svg>
```

Save as SVG and convert to required formats.

## App Icon Design Tips

- **Simple & Bold**: Icon should be recognizable at small sizes (16x16)
- **No Text**: Text becomes unreadable at small sizes
- **Flat Design**: Modern, clean look
- **Contrast**: Ensure visibility on light and dark backgrounds
- **Consistent**: Use brand colors from main app

## Current Placeholder

A temporary 1024x1024 PNG is included for development. Replace with production icon before release.
