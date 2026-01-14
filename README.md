<div align="center">

  <img src="working-demo.png" alt="Compress to AVIF Demo" width="800">

  # Compress to AVIF

  **Convert project images to AVIF format without resizing - Preserve quality, reduce file size**

  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

</div>

---

## About

Compress to AVIF is a simple Python script that converts your images to the modern AVIF format at quality 75 while preserving their original resolution. AVIF offers significantly better compression than traditional formats like JPEG and PNG, resulting in smaller file sizes without noticeable quality loss.

### Why AVIF?

- **50% smaller files** compared to JPEG at similar quality
- **Modern browser support** (Chrome, Firefox, Safari, Edge)
- **Royalty-free** format
- **Excellent quality** at lower bitrates

---

## Features

- Batch convert multiple images at once
- Configurable quality settings (1-100)
- Preserves original image dimensions
- Generates a mapping file for easy reference updates
- Dry-run mode to preview changes
- Handles EXIF orientation automatically
- Supports both absolute and relative paths

---

## Installation

### Requirements

- Python 3.8 or higher
- Pillow (PIL)
- pillow-avif-plugin

### Install Dependencies

```bash
python3 -m pip install pillow pillow-avif-plugin
```

---

## Usage

### 1. Create an Image List

Create an `image-files.json` file in your project root:

```json
{
  "images": [
    "public/images/hero.jpg",
    { "path": "src/assets/card.png" },
    { "file": "assets/banner.webp" }
  ]
}
```

### 2. Run the Script

```bash
python3 scripts/compress_images_to_avif.py \
  --images image-files.json \
  --output-dir assets/optimized \
  --quality 75
```

### Options

| Option | Alias | Description | Default |
|--------|-------|-------------|---------|
| `--images` | `--sizes` | Path to image list JSON | `image-files.json` |
| `--output-dir` | - | Output directory for .avif files | Same as input |
| `--quality` | - | AVIF quality (1-100) | `75` |
| `--root-dir` | - | Root directory for relative paths | Current directory |
| `--mapping-file` | - | Path for the mapping JSON output | `image-map.json` |
| `--dry-run` | - | Preview without writing files | `false` |

### 3. Use the Mapping File

The script generates an `image-map.json` file that maps original paths to new AVIF paths:

```json
{
  "generatedAt": "2025-01-14T12:00:00Z",
  "quality": 75,
  "items": [
    {
      "input": "public/images/hero.jpg",
      "output": "assets/optimized/hero.avif",
      "status": "converted",
      "sourceWidth": 1920,
      "sourceHeight": 1080
    }
  ]
}
```

Use this mapping to update references in your code or HTML:

```html
<picture>
  <source srcset="assets/optimized/hero.avif" type="image/avif">
  <img src="public/images/hero.jpg" alt="Hero image">
</picture>
```

---

## Example Output

```
Processed: 5, skipped: 0
Mapping written to: image-map.json
```

---

## Browser Support

AVIF is supported in all modern browsers:

| Browser | Version |
|---------|---------|
| Chrome | 85+ |
| Firefox | 93+ |
| Safari | 16+ |
| Edge | 85+ |

For older browsers, use the `<picture>` element with fallbacks as shown above.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## Author

Made with ❤️ by [Andac](https://github.com/andac)
