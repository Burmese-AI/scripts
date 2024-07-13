import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def run_command(command: str) -> tuple[str, str]:
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError(
            e.returncode, e.cmd, output=e.stdout, stderr=e.stderr
        ) from e


def get_repo_name(repo_url: str) -> str:
    parsed_url = urlparse(repo_url)
    path = parsed_url.path.strip("/")
    repo_name = path.split("/")[-1]
    return repo_name.removesuffix(".git")


def main(repo_url: str) -> None:
    try:
        repo_name = get_repo_name(repo_url)
        repo_path = Path(repo_name)

        # Clone the repository if it does not exist
        if not repo_path.exists():
            run_command(f"git clone {repo_url}")

        # Change directory to the cloned repository
        os.chdir(repo_path)

        # Copy the pyproject.toml file from the parent directory
        Path("../pyproject.toml").copy("pyproject.toml")

        # Stage, commit, and push changes
        run_command("git add pyproject.toml")
        run_command('git commit -m "Add ruff configuration"')
        run_command("git push origin main")

        print("Automation complete!")
    except subprocess.CalledProcessError as e:
        print(f"Command '{e.cmd}' failed with return code {e.returncode}")
        print(f"Output: {e.output}")
        print(f"Error: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python automate.py <repo_url>")
        sys.exit(1)

    main(sys.argv[1])
