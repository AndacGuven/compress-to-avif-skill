#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime, timezone


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compress images to AVIF without resizing."
    )
    parser.add_argument(
        "--images",
        "--sizes",
        dest="images",
        default="image-files.json",
        help="Path to image list JSON (default: image-files.json)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for .avif files (optional)",
    )
    parser.add_argument(
        "--root-dir",
        default=None,
        help="Root directory for relative paths (default: cwd)",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=75,
        help="AVIF quality 1-100 (default: 75)",
    )
    parser.add_argument(
        "--mapping-file",
        default=None,
        help="Write mapping JSON to this path",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without writing files",
    )
    return parser.parse_args()


def load_pillow(require_avif: bool):
    try:
        from PIL import Image, ImageOps  # type: ignore
    except ModuleNotFoundError:
        print("Pillow is not installed. Run: python3 -m pip install pillow")
        raise SystemExit(1)

    try:
        import pillow_avif  # noqa: F401
    except ModuleNotFoundError:
        pass

    if require_avif:
        extensions = Image.registered_extensions()
        if ".avif" not in extensions:
            print(
                "AVIF support is not available. "
                "Install pillow-avif-plugin or a Pillow build with AVIF support."
            )
            raise SystemExit(1)

    return Image, ImageOps


def normalize_entries(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("images"), list):
        return data["images"]
    return []


def resolve_input_path(root_dir, input_path):
    if not input_path:
        return None
    if os.path.isabs(input_path):
        return os.path.normpath(input_path)
    return os.path.abspath(os.path.join(root_dir, input_path))


def build_output_path(root_dir, output_dir, absolute_input):
    relative_input = os.path.relpath(absolute_input, root_dir)
    if relative_input == os.pardir or relative_input.startswith(os.pardir + os.sep):
        safe_relative = os.path.basename(absolute_input)
    else:
        safe_relative = relative_input

    base_name = os.path.splitext(os.path.basename(safe_relative))[0]
    relative_dir = os.path.dirname(safe_relative)
    if output_dir:
        return os.path.join(output_dir, relative_dir, f"{base_name}.avif")
    return os.path.join(os.path.dirname(absolute_input), f"{base_name}.avif")


def normalize_entry(entry):
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        return entry.get("path") or entry.get("file") or entry.get("input")
    return None


def main() -> None:
    args = parse_args()

    if args.quality < 1 or args.quality > 100:
        print("Quality must be an integer between 1 and 100.")
        raise SystemExit(1)

    root_dir = os.path.abspath(args.root_dir or os.getcwd())
    images_path = os.path.abspath(os.path.join(root_dir, args.images))
    output_dir = (
        os.path.abspath(os.path.join(root_dir, args.output_dir))
        if args.output_dir
        else None
    )
    mapping_rel_path = (
        args.mapping_file
        if args.mapping_file
        else os.path.join(args.output_dir, "image-map.json")
        if args.output_dir
        else "image-map.json"
    )
    mapping_file = os.path.abspath(os.path.join(root_dir, mapping_rel_path))

    if not os.path.exists(images_path):
        print(f"Image list not found: {images_path}")
        raise SystemExit(1)

    with open(images_path, "r", encoding="utf-8") as handle:
        try:
            data = json.load(handle)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {images_path}")
            raise SystemExit(1)

    entries = normalize_entries(data)
    if not entries:
        print("No image entries found in image list.")
        raise SystemExit(1)

    Image, ImageOps = load_pillow(require_avif=not args.dry_run)

    if output_dir and not args.dry_run:
        os.makedirs(output_dir, exist_ok=True)

    results = []
    processed = 0
    skipped = 0

    for entry in entries:
        input_path = normalize_entry(entry)
        if not input_path:
            results.append(
                {
                    "input": None,
                    "status": "skipped",
                    "reason": "missing_path",
                }
            )
            skipped += 1
            continue

        absolute_input = resolve_input_path(root_dir, input_path)
        if not absolute_input or not os.path.exists(absolute_input):
            results.append(
                {
                    "input": input_path,
                    "status": "skipped",
                    "reason": "file_not_found",
                }
            )
            skipped += 1
            continue

        try:
            with Image.open(absolute_input) as image:
                image = ImageOps.exif_transpose(image)
                source_width, source_height = image.size

                output_path = build_output_path(root_dir, output_dir, absolute_input)
                if os.path.abspath(output_path) == os.path.abspath(absolute_input):
                    base_name = os.path.splitext(os.path.basename(output_path))[0]
                    output_path = os.path.join(
                        os.path.dirname(output_path), f"{base_name}-compressed.avif"
                    )

                if not args.dry_run:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    image.save(output_path, format="AVIF", quality=args.quality)

        except Exception:
            results.append(
                {
                    "input": input_path,
                    "status": "skipped",
                    "reason": "read_failed",
                }
            )
            skipped += 1
            continue

        relative_input = os.path.relpath(absolute_input, root_dir)
        relative_output = os.path.relpath(output_path, root_dir)
        results.append(
            {
                "input": relative_input,
                "output": relative_output,
                "status": "dry-run" if args.dry_run else "converted",
                "sourceWidth": source_width,
                "sourceHeight": source_height,
                "quality": args.quality,
            }
        )
        processed += 1

    mapping = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "rootDir": root_dir,
        "outputDir": os.path.relpath(output_dir, root_dir) if output_dir else None,
        "quality": args.quality,
        "items": results,
    }

    if not args.dry_run:
        os.makedirs(os.path.dirname(mapping_file), exist_ok=True)
        with open(mapping_file, "w", encoding="utf-8") as handle:
            json.dump(mapping, handle, indent=2)
            handle.write("\n")

    print(f"Processed: {processed}, skipped: {skipped}")
    if args.dry_run:
        print("Dry run: no files were written.")
    else:
        print(f"Mapping written to: {mapping_file}")


if __name__ == "__main__":
    main()
