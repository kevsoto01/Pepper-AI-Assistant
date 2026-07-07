from pathlib import Path


def count_python_lines(directory):
    directory = Path(directory)

    total_lines = 0
    file_counts = {}

    for file_path in directory.rglob("*.py"):
        line_count = 0

        with file_path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip() and not line.strip().startswith("#"):
                    line_count += 1

        file_counts[str(file_path)] = line_count
        total_lines += line_count

    return total_lines, file_counts

def count_comment_lines_per_file(directory):
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory}")

    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    total_comment_lines = 0
    file_counts = {}

    for file_path in directory.rglob("*.py"):
        comment_count = 0

        with file_path.open("r", encoding="utf-8") as file:
            for line in file:
                stripped_line = line.strip()

                if stripped_line.startswith("#"):
                    comment_count += 1

        file_counts[str(file_path)] = comment_count
        total_comment_lines += comment_count

    return total_comment_lines, file_counts

total, files = count_python_lines(r"C:\Users\kevso\Downloads\pepper_v2_app\app")

print("\nTotal lines:", total)

for file_path, line_count in files.items():
    print(file_path, line_count)
    
    
total_comments, comment_files = count_comment_lines_per_file(
    r"C:\Users\kevso\Downloads\pepper_v2_app"
)

print("\n\nTotal comment-only lines:", total_comments)

for file_path, comment_count in comment_files.items():
    print(file_path, comment_count)