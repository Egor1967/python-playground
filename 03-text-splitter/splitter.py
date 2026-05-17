# splitter.py — разбивает текстовый файл на блоки по разделителю

import sys
from pathlib import Path

SPLIT_DELIMITER = "-" * 66


def build_output_path(source: Path, block_number: int) -> Path:
    """Возвращает свободное имя выходного файла для одного блока.

    Базовый формат: <stem>_block_<NN>.txt
    Если файл уже существует, добавляет суффикс _v2, _v3, …
    """
    stem = source.stem
    base = source.parent / f"{stem}_block_{block_number:02d}.txt"
    if not base.exists():
        return base
    version = 2
    while True:
        candidate = source.parent / f"{stem}_block_{block_number:02d}_v{version}.txt"
        if not candidate.exists():
            return candidate
        version += 1


def main():
    if len(sys.argv) != 2:
        print("Использование: python3 splitter.py <путь_к_файлу.txt>")
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if filepath.suffix != ".txt":
        print(f"Ошибка: файл '{filepath}' должен иметь расширение .txt")
        sys.exit(1)

    if not filepath.exists():
        print(f"Ошибка: файл '{filepath}' не найден")
        sys.exit(1)

    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError as e:
        print(f"Ошибка чтения файла '{filepath}': {e}")
        sys.exit(1)

    blocks = [block.strip() for block in text.split(SPLIT_DELIMITER) if block.strip()]

    if not blocks:
        print("Ошибка: в файле не найдено ни одного непустого блока")
        sys.exit(1)

    output_paths = [build_output_path(filepath, i + 1) for i, _ in enumerate(blocks)]

    created = []
    for block, path in zip(blocks, output_paths):
        try:
            path.write_text(block, encoding="utf-8")
            created.append(path)
        except OSError as e:
            print(f"Ошибка записи файла '{path}': {e}")
            sys.exit(1)

    print(f"Создано файлов: {len(created)}")
    for path in created:
        print(f"  {path.name}")


if __name__ == "__main__":
    main()
