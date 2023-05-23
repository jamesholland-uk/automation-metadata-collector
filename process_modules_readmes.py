"""Process README.md files for each module and example
"""
import os
from pathlib import Path
from typing import NamedTuple

import argparse
import frontmatter


class NoFrontmatterError(Exception):
    """Raised when a README.md file does not contain a frontmatter section"""

    def __init__(self, message=None, filepath=None):
        message = message if message else "No frontmatter found in README.md file"
        super().__init__(message)
        self.message = message
        self.filepath = filepath

    def __str__(self):
        if self.filepath:
            return f"{self.message}: {self.filepath}"
        return self.message


class TFModule(NamedTuple):
    """Terraform Module (or Example)"""

    slug: str
    readme_contents: str
    # description: str
    # source: str
    # version: str


def read_and_parse_readme_file(readme_file: Path) -> TFModule:
    """Read and parse the README.md file

    Args:
        readme_file (Path): Path to the README.md file

    Raises:
        NoFrontmatterError: Raised when the README.md file does not contain a frontmatter section

    Returns:
        TFModule: TFModule instance
    """
    readme_contents = readme_file.read_text()
    readme_frontmatter = frontmatter.loads(readme_contents)
    if len(readme_frontmatter.keys()) == 0:
        raise NoFrontmatterError(filepath=readme_file)
    module_slug = (
        readme_frontmatter["slug"]
        if "slug" in readme_frontmatter
        else readme_file.parent.name
    )
    return TFModule(slug=module_slug, readme_contents=readme_contents)


def get_module_readme_files(module_directory: Path) -> list[TFModule]:
    """Get all README.md files and their contents from the source repository

    Args:
        source_repository (str): Path to the directory containing the source repository

    Returns:
        list: List of TFModule instances, one for each README.md file
    """
    result = []
    readme_files = module_directory.glob("*/README.md")
    for readme in readme_files:
        try:
            tf_module = read_and_parse_readme_file(readme)
        except NoFrontmatterError as e:
            print(e)
            continue
        result.append(tf_module)
    return result


def set_new_frontmatter(readme_contents: str) -> str:
    """Set new frontmatter for the README.md file

    Args:
        readme_contents (str): Contents of the README.md file

    Returns:
        str: New contents of the README.md file
    """
    readme_frontmatter = frontmatter.loads(readme_contents)
    readme_frontmatter["updated_by"] = "github_action"
    return frontmatter.dumps(readme_frontmatter)


def main(modules_directory, dest_directory):
    tf_modules = get_module_readme_files(Path(modules_directory))
    for module in tf_modules:
        new_readme_contents = set_new_frontmatter(module.readme_contents)
        dest_file = Path(dest_directory) / f"{module.slug}.md"
        dest_file.write_text(new_readme_contents)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process input arguments.")
    parser.add_argument("modules_directory", type=str, help="Modules directory")
    parser.add_argument("dest_directory", type=str, help="Destination directory")

    args = parser.parse_args()

    main(args.modules_directory, args.dest_directory)
