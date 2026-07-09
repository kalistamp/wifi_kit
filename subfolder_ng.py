#!/usr/bin/env python3
"""WiFi Recon Assessment Kit Setup.

Generates a standardized directory structure and a set of reference/manual
text files used to kick off a WiFi security assessment. Manual/reference
content lives in the `templates/` package next to this script and is loaded
at runtime via importlib.resources, so the manuals can be edited without
touching this file.

Disclaimer: This script is for educational purposes only.
Use only on networks you own or have explicit authorization to test.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import argparse
import importlib.resources as resources
import os
import sys

# =====================================================================
# Configuration
# =====================================================================

APP_VERSION = "3.5 (Externalized Templates + CLI --name)"
AUTHOR = "Kalistamp"
TEMPLATES_PACKAGE = "templates"

# Sub-directories created inside every new assessment folder.
# Key   -> top-level folder name
# Value -> list of nested child folders (empty list = no children)
DIR_STRUCTURE: Dict[str, List[str]] = {
    "sharkcaps": ["main"],  # Raw packet captures (.cap files)
    "word_li": ["combo"],   # Custom / cleaned wordlists
    "hashcat": [],          # Output files and .hc22000 (hashcat format) files
    "xtras": [],            # Miscellaneous notes, screenshots, etc.
}

# Console log prefixes, kept consistent across the script.
LOG_OK = " [+] "
LOG_WARN = " [!] "
LOG_SUB = "   |-- "


# =====================================================================
# CLI argument parsing
# =====================================================================

def parse_args(argv: List[str] = None) -> argparse.Namespace:
    """Parses command-line arguments.

    Supports non-interactive / scripted or CI-driven kit setup via --name.
    When --name is omitted, the script falls back to the interactive prompt.

    Example:
        python3 subfolder_ng.py --name "My-Assessment-v1"
    """
    parser = argparse.ArgumentParser(
        description="WiFi Recon Assessment Kit Setup",
    )
    parser.add_argument(
        "--name",
        dest="name",
        default=None,
        help=(
            "Assessment folder name. If omitted, you will be prompted "
            "interactively. Example: --name \"My-Assessment-v1\""
        ),
    )
    return parser.parse_args(argv)


# =====================================================================
# Console / UI helpers
# =====================================================================

def print_banner() -> None:
    """Prints the application banner and metadata."""
    ascii_banner = r"""
____ _  _ ___  ____ ____ _    ___  ____ ____  ___  _  _
[__  |  | |__] |___ |  | |    |  \ |___ |__/  |__]  \_/
___] |__| |__] |    |__| |___ |__/ |___ |  \ .|    |

        [ WiFi Recon Assessment Setup | Version {version} ]
        [ Defensive Blue Team Tooling ]
""".format(version=APP_VERSION)
    print(ascii_banner)
    print(f"Author: {AUTHOR}\n\n")


# =====================================================================
# Filesystem operations
# =====================================================================

def resolve_directory_name(cli_name: str = None) -> Path:
    """Determines the assessment folder name.

    Uses the --name CLI argument if provided; otherwise falls back to an
    interactive prompt with a date-stamped default.

    Args:
        cli_name: The value passed via --name, if any.

    Returns:
        Path: The (not-yet-created) base directory for this assessment.
    """
    if cli_name:
        return Path(cli_name.strip())

    default_name = datetime.now().strftime("%Y-%m-%d_WIFI_ASSESSMENT")
    print(f"Suggestion: {default_name}")

    entered_name = input("Enter Name/Date for Today's Work: ").strip()
    return Path(entered_name or default_name)


def create_directory_structure(base_dir: Path) -> None:
    """Creates the main assessment directory and its subdirectories.

    Args:
        base_dir: The root folder for this assessment.

    Exits:
        Terminates the program if base_dir already exists or cannot be
        created.
    """
    try:
        # 0o755 is the standard permission for directories (rwxr-xr-x).
        os.makedirs(base_dir, mode=0o755, exist_ok=False)
        print(f"{LOG_OK}Created main assessment directory: {base_dir}")

        for parent, children in DIR_STRUCTURE.items():
            parent_path = base_dir / parent
            os.makedirs(parent_path, mode=0o755, exist_ok=True)
            print(f"{LOG_SUB}Created folder: {parent_path}")

            for child in children:
                child_path = parent_path / child
                os.makedirs(child_path, mode=0o755, exist_ok=True)
                print(f"{LOG_SUB}Created folder: {child_path}")

    except FileExistsError:
        print(f"{LOG_WARN}Error: Directory '{base_dir}' already exists. "
              f"Please choose a new name.")
        sys.exit(1)
    except OSError as exc:
        print(f"{LOG_WARN}An error occurred during directory creation: {exc}")
        sys.exit(1)


# =====================================================================
# Template loading
# =====================================================================

def _load_template(filename: str) -> str:
    """Reads a documentation template's contents from the templates package.

    Args:
        filename: The template file name, e.g. "wifi_assessment_manual.txt".

    Returns:
        The file's text contents.

    Exits:
        Terminates the program if the template cannot be found or read,
        since a missing template means a generated file would be empty.
    """
    try:
        template_path = resources.files(TEMPLATES_PACKAGE).joinpath(filename)
        return template_path.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError) as exc:
        print(f"{LOG_WARN}Could not load template '{filename}': {exc}")
        sys.exit(1)


# =====================================================================
# File writer
# =====================================================================

def _documentation_manifest(base_dir: Path) -> List[Tuple[Path, str]]:
    """Builds the list of (destination path, file content) pairs to write.

    Content is pulled from the templates/ package at call time, keeping the
    "what to write" step separate from directory layout and I/O.
    """
    return [
        (base_dir / "README_RECON_NOTES.txt",
         _load_template("readme_recon_notes.txt")),
        (base_dir / "sharkcaps" / "main" / "NOTES.txt",
         _load_template("capture_notes.txt")),
        (base_dir / "word_li" / "combo" / "WORDLIST_UTILS.txt",
         _load_template("wordlist_utils.txt")),
        (base_dir / "TOOLS_RESOURCES.txt",
         _load_template("tools_resources.txt")),
        (base_dir / "WIFI_ASSESSMENT_MANUAL.txt",
         _load_template("wifi_assessment_manual.txt")),
    ]


def write_documentation_files(base_dir: Path) -> None:
    """Writes the predefined documentation content to their target files.

    Args:
        base_dir: The root assessment directory (already created).
    """
    for file_path, content in _documentation_manifest(base_dir):
        try:
            with open(file_path, "w", encoding="utf-8") as handle:
                handle.write(content)
        except OSError as exc:
            print(f"{LOG_WARN}Failed to write file {file_path}: {exc}")


# =====================================================================
# Entry point
# =====================================================================

def main() -> None:
    """Runs the assessment-kit setup workflow (interactive or via --name)."""
    args = parse_args()

    print_banner()

    base_dir = resolve_directory_name(args.name)
    print("\n")

    create_directory_structure(base_dir)
    write_documentation_files(base_dir)

    print(f"\n{LOG_OK}Assessment Kit and Manual Created Successfully.")


if __name__ == "__main__":
    main()
