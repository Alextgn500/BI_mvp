from pathlib import Path


def print_tree(directory, prefix="", exclude=None):
    """Красиво выводит дерево директорий"""
    if exclude is None:
        exclude = {
            "venv",
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            ".vscode",
            "logs",
        }

    directory = Path(directory)
    contents = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))

    for i, path in enumerate(contents):
        if path.name in exclude or path.name.startswith("."):
            continue

        is_last = i == len(contents) - 1
        current_prefix = " " if is_last else " "
        print(f"{prefix}{current_prefix}{path.name}")

        if path.is_dir():
            extension = "    " if is_last else "   "
            print_tree(path, prefix + extension, exclude)


if __name__ == "__main__":
    print("fastapi_ml/")
    print_tree("fastapi_ml")
