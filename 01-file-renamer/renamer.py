from __future__ import annotations

import argparse
from pathlib import Path


def normalize_extension(ext: str | None) -> str | None:
    if ext is None:
        return None

    ext = ext.strip().lower()
    if not ext:
        return None

    if not ext.startswith("."):
        ext = f".{ext}"

    return ext


def build_new_name(filename: str) -> str:
    return filename.replace(" ", "_").lower()


def collect_renames(folder: Path, extension: str | None) -> tuple[list[tuple[Path, Path]], int]:
    planned = []
    scanned_files = 0

    for item in sorted(folder.iterdir()):
        if not item.is_file():
            continue

        scanned_files += 1

        if extension is not None and item.suffix.lower() != extension:
            continue

        new_name = build_new_name(item.name)
        new_path = item.with_name(new_name)

        if new_name != item.name:
            planned.append((item, new_path))

    return planned, scanned_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview or apply safe file renaming in a single folder."
    )
    parser.add_argument("folder", help="Path to the target folder")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually rename files instead of previewing changes",
    )
    parser.add_argument(
        "--ext",
        help="Only process files with this extension, for example: txt or .txt",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    folder = Path(args.folder).expanduser().resolve()
    extension = normalize_extension(args.ext)

    if not folder.exists():
        print(f"Error: folder does not exist: {folder}")
        raise SystemExit(1)

    if not folder.is_dir():
        print(f"Error: path is not a folder: {folder}")
        raise SystemExit(1)

    planned, scanned_files = collect_renames(folder, extension)

    unchanged_count = scanned_files - len(planned)

    if not args.apply:
        print("Preview mode. No files were renamed.\n")

        if planned:
            for old_path, new_path in planned:
                print(f"{old_path.name} -> {new_path.name}")
        else:
            print("No files need renaming.")

        print("\nSummary:")
        print(f"- Scanned files: {scanned_files}")
        print(f"- Files to rename: {len(planned)}")
        print(f"- Unchanged files: {unchanged_count}")
        return

    if not planned:
        print("Apply mode. No files need renaming.\n")
        print("Summary:")
        print(f"- Scanned files: {scanned_files}")
        print("- Renamed files: 0")
        print(f"- Unchanged files: {unchanged_count}")
        return

    print("Apply mode. Renaming files...\n")

    renamed_count = 0
    skipped_count = 0

    for old_path, new_path in planned:
        if new_path.exists():
            print(f"Skip: target already exists: {new_path.name}")
            skipped_count += 1
            continue

        old_path.rename(new_path)
        print(f"Renamed: {old_path.name} -> {new_path.name}")
        renamed_count += 1

    print("\nSummary:")
    print(f"- Scanned files: {scanned_files}")
    print(f"- Planned renames: {len(planned)}")
    print(f"- Renamed files: {renamed_count}")
    print(f"- Skipped files: {skipped_count}")
    print(f"- Unchanged files: {unchanged_count}")


if __name__ == "__main__":
    main()
