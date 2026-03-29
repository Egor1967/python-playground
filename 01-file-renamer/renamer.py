from __future__ import annotations

import argparse
from pathlib import Path


def build_new_name(filename: str) -> str:
    return filename.replace(" ", "_").lower()


def collect_renames(folder: Path) -> list[tuple[Path, Path]]:
    planned = []

    for item in sorted(folder.iterdir()):
        if not item.is_file():
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    folder = Path(args.folder).expanduser().resolve()

    if not folder.exists():
        print(f"Error: folder does not exist: {folder}")
        raise SystemExit(1)

    if not folder.is_dir():
        print(f"Error: path is not a folder: {folder}")
        raise SystemExit(1)

    planned = collect_renames(folder)

    if not planned:
        print("No files need renaming.")
        return

    if not args.apply:
        print("Preview mode. No files were renamed.\n")
        for old_path, new_path in planned:
            print(f"{old_path.name} -> {new_path.name}")
        return

    print("Apply mode. Renaming files...\n")

    for old_path, new_path in planned:
        if new_path.exists():
            print(f"Skip: target already exists: {new_path.name}")
            continue

        old_path.rename(new_path)
        print(f"Renamed: {old_path.name} -> {new_path.name}")


if __name__ == "__main__":
    main()
