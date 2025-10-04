# Icon and Assets Guide

## App Icon

The app icon is located at `assets/icons/icon.svg`.

### To Replace Icon:

1. **Create/Edit Icon**
   - Recommended size: 512x512 pixels
   - Format: PNG or SVG
   - Design should be simple and recognizable

2. **Update in Godot**
   - Place icon in `assets/icons/`
   - Open Project Settings → Application → Config
   - Set Icon path to your icon file

3. **For Android**
   - Android requires multiple icon sizes
   - Godot will auto-generate from your base icon
   - Or manually create: 48x48, 72x72, 96x96, 144x144, 192x192

### Icon Design Tips

- Use school/education theme
- Keep it simple (looks good small)
- High contrast colors
- Avoid text (hard to read at small sizes)
- Test at different sizes

## Other Assets

### Fonts
- Place custom fonts in `assets/fonts/`
- Recommended: Open-source fonts (Google Fonts)
- Common formats: TTF, OTF

### Sounds
- Place audio files in `assets/sounds/`
- Recommended formats: OGG (best for Godot), WAV, MP3
- Keep file sizes small for mobile

### UI Graphics
- Place UI elements in `assets/icons/`
- Use PNG with transparency for overlays
- SVG for scalable graphics

## Asset Resources

**Free Icon Sites:**
- https://www.flaticon.com
- https://icons8.com
- https://fontawesome.com

**Free Font Sites:**
- https://fonts.google.com
- https://www.fontsquirrel.com

**Free Sound Sites:**
- https://freesound.org
- https://www.zapsplat.com

## License Compliance

- Always check license before using assets
- Prefer CC0, MIT, or Apache licensed assets
- Credit creators when required
- Keep license file in assets folder
