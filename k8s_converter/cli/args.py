"""
Command-line argument definitions for the k8s-yaml-to-json converter.
This module centralizes CLI argument definitions to avoid duplication.
"""

import argparse


def add_common_cli_args(parser: argparse.ArgumentParser) -> None:
    """
    Add common CLI arguments to a parser.

    Args:
        parser: The argument parser to add arguments to
    """
    parser.add_argument(
        "input", help="Input YAML file or directory containing YAML files"
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output directory for JSON files (default: ./output)",
        default="./output",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        help="Recursively process subdirectories",
        action="store_true",
    )
    parser.add_argument(
        "--no-pretty",
        help="Output minified JSON without indentation",
        action="store_true",
    )
    parser.add_argument(
        "-v", "--verbose", help="Enable verbose logging", action="store_true"
    )


def create_cli_parser() -> argparse.ArgumentParser:
    """
    Create a standalone CLI parser for the bulk converter.

    Returns:
        argparse.ArgumentParser: Configured parser
    """
    parser = argparse.ArgumentParser(
        description="Bulk convert Kubernetes YAML files to JSON"
    )
    add_common_cli_args(parser)
    return parser
