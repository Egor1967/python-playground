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


def iter_files(folder: Path, recursive: bool):
    if recursive:
        yield from sorted(path for path in folder.rglob("*") if path.is_file())
    else:
        yield from sorted(path for path in folder.iterdir() if path.is_file())


def collect_renames(
    folder: Path,
    extension: str | None,
    recursive: bool,
) -> list[tuple[Path, Path]]:
    planned = []

    for item in iter_files(folder, recursive):
        if extension is not None and item.suffix.lower() != extension:
            continue

        new_name = build_new_name(item.name)
        new_path = item.with_name(new_name)

        if new_name != item.name:
            planned.append((item, new_path))

    return planned


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
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process files in subfolders recursively",
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

    planned = collect_renames(folder, extension, args.recursive)

    if not planned:
        print("No files need renaming.")
        return

    if not args.apply:
        print("Preview mode. No files were renamed.\n")
        for old_path, new_path in planned:
            print(f"{old_path.relative_to(folder)} -> {new_path.relative_to(folder)}")
        return

    print("Apply mode. Renaming files...\n")

    for old_path, new_path in planned:
        if new_path.exists():
            print(f"Skip: target already exists: {new_path.relative_to(folder)}")
            continue

        old_path.rename(new_path)
        print(f"Renamed: {old_path.relative_to(folder)} -> {new_path.relative_to(folder)}")


if __name__ == "__main__":
    main()
