---
name: compress-to-avif
description: Convert project images to AVIF at quality 75 without resizing. Use when migrating assets to AVIF while preserving original resolution.
---

# Compress To Avif

## Overview

Convert images to AVIF (quality 75) without changing their resolution.

## Workflow

1. Collect the image paths.
2. Create an image list JSON.
3. Run the compression script.
4. Update references.

## 1) Collect the image paths

- List every image you want to convert to AVIF.
- Use project-relative paths when possible.

## 2) Create the image list

Create `image-files.json` in the project root:

```json
{
  "images": [
    "public/images/hero.jpg",
    { "path": "src/assets/card.png" }
  ]
}
```

Notes:

- Only the path is required. Width/height are ignored.

## 3) Compress + convert to AVIF

Install the dependencies in the project root:

```bash
python3 -m pip install pillow pillow-avif-plugin
```

Run the script:

```bash
python3 /Users/m4macmini/.codex/skills/public/resize-and-compress-avif/scripts/compress_images_to_avif.py \
  --images image-files.json \
  --output-dir assets/optimized \
  --quality 75
```

Options:

- `--images` to set the image list JSON path (alias `--sizes`).
- `--output-dir` to choose where AVIF outputs are written.
- `--quality` to control AVIF quality (1-100).
- `--root-dir` to control relative path mapping for outputs.
- `--mapping-file` to write the JSON mapping file.
- `--dry-run` to preview without writing files.

## 4) Update references

Use `image-map.json` to replace old paths with the new `.avif` paths (or add `<picture>` with an AVIF source).

## Scripts

- `scripts/compress_images_to_avif.py`: Convert based on an image list, compress to AVIF quality 75, and emit a mapping file.
