from pathlib import Path
import subprocess
import sys


def install_requirements(requirements_file: str = "requirements.txt"):
    requirements_path = Path(requirements_file)

    if not requirements_path.exists():
        print(f"Could not find: {requirements_path}")
        return False

    if requirements_path.stat().st_size == 0:
        print(f"{requirements_path} is empty. Nothing to install.")
        return True

    print(f"Installing packages from: {requirements_path}")
    print("-" * 50)

    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        str(requirements_path)
    ]

    try:
        subprocess.check_call(command)
        print("-" * 50)
        print("All requirements installed successfully.")
        return True

    except subprocess.CalledProcessError as error:
        print("-" * 50)
        print("Installation failed.")
        print(f"Exit code: {error.returncode}")
        return False


def main():
    requirements_file = "requirements.txt"

    if len(sys.argv) > 1:
        requirements_file = sys.argv[1]

    install_requirements(requirements_file)


if __name__ == "__main__":
    main()