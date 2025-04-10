import logging
import sys
from pathlib import Path

from k8s_converter.core.converter import (
    yaml_file_to_json,
    save_json_to_file,
    K8sParserError,
)

from k8s_converter.core.logger import logger
from k8s_converter.cli.args import create_cli_parser


def process_file(input_file: Path, output_dir: Path, pretty: bool = True) -> bool:
    """
    Process a single YAML file and convert it to JSON.

    Args:
        input_file (Path): Path to the input YAML file
        output_dir (Path): Directory to save the output JSON file
        pretty (bool): Whether to format JSON with indentation

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        output_file = output_dir / f"{input_file.stem}.json"

        logger.info(f"Processing {input_file}")
        json_data = yaml_file_to_json(input_file)

        save_json_to_file(json_data, output_file, pretty)
        logger.info(f"Successfully converted {input_file} to {output_file}")
        return True
    except K8sParserError as e:
        logger.error(f"Failed to convert {input_file}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error processing {input_file}: {str(e)}")
        return False


def process_directory(
    input_dir: Path, output_dir: Path, pretty: bool = True, recursive: bool = False
) -> tuple[int, int]:
    """
    Process all YAML files in a directory and convert them to JSON.

    Args:
        input_dir (Path): Directory containing input YAML files
        output_dir (Path): Directory to save the output JSON files
        pretty (bool): Whether to format JSON with indentation
        recursive (bool): Whether to recursively process subdirectories

    Returns:
        tuple[int, int]: (number of successful conversions, total number of files processed)
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    pattern = "**/*.y*ml" if recursive else "*.y*ml"
    yaml_files = list(input_dir.glob(pattern))

    successful = 0
    total = len(yaml_files)

    for yaml_file in yaml_files:
        # For recursive processing, maintain directory structure
        if recursive and yaml_file.parent != input_dir:
            relative_path = yaml_file.parent.relative_to(input_dir)
            file_output_dir = output_dir / relative_path
            file_output_dir.mkdir(parents=True, exist_ok=True)
        else:
            file_output_dir = output_dir

        if process_file(yaml_file, file_output_dir, pretty):
            successful += 1

    return successful, total


def run_cli(args=None):
    """
    Run the CLI bulk converter with the provided arguments.

    Args:
        args: The parsed command-line arguments. If None, arguments will be parsed.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    if args is None:
        parser = create_cli_parser()
        args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    input_path = Path(args.input)
    output_path = Path(args.output)
    pretty = not args.no_pretty

    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        return 1

    # Process input
    if input_path.is_file():
        # Process a single file
        output_path.mkdir(parents=True, exist_ok=True)
        success = process_file(input_path, output_path, pretty)
        return 0 if success else 1
    else:
        # Process a directory
        successful, total = process_directory(
            input_path, output_path, pretty, args.recursive
        )
        logger.info(f"Processed {total} files, {successful} successful conversions")
        return 0 if successful == total else 1


def main():
    """Main entry point for the bulk converter when run directly."""
    sys.exit(run_cli())


if __name__ == "__main__":
    main()
