import fileinput
from pathlib import Path


def remove_lines_from_file(file_path: Path, patterns_to_remove: list[str]) -> None:
    with fileinput.input(files=[file_path], inplace=True) as f:
        for line in f:
            if not any(pattern in line for pattern in patterns_to_remove):
                print(line, end="")
