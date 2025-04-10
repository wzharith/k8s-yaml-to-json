#!/usr/bin/env python3

import sys
import os
import argparse
import uvicorn

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    Start the FastAPI server

    Args:
        host (str): Host to bind to
        port (int): Port to bind to
        reload (bool): Whether to enable auto-reload
    """
    uvicorn.run("k8s_converter.api.app:app", host=host, port=port, reload=reload)


def add_api_parser(subparsers: argparse._SubParsersAction) -> None:
    api_parser = subparsers.add_parser("api", help="Start the API server")
    api_parser.add_argument(
        "--host", help="Host to bind to (default: 0.0.0.0)", default="0.0.0.0"
    )
    api_parser.add_argument(
        "--port", help="Port to bind to (default: 8000)", type=int, default=8000
    )
    api_parser.add_argument(
        "--reload", help="Enable auto-reload for development", action="store_true"
    )


def add_cli_parser(subparsers: argparse._SubParsersAction) -> None:
    cli_parser = subparsers.add_parser("cli", help="Run the CLI bulk converter")
    cli_parser.add_argument(
        "input", help="Input YAML file or directory containing YAML files"
    )
    cli_parser.add_argument(
        "-o",
        "--output",
        help="Output directory for JSON files (default: ./output)",
        default="./output",
    )
    cli_parser.add_argument(
        "-r",
        "--recursive",
        help="Recursively process subdirectories",
        action="store_true",
    )
    cli_parser.add_argument(
        "--no-pretty",
        help="Output minified JSON without indentation",
        action="store_true",
    )
    cli_parser.add_argument(
        "-v", "--verbose", help="Enable verbose logging", action="store_true"
    )


def main():
    """
    Main entry point for the k8s_converter package.
    Dispatches to the appropriate subcommand.
    """
    parser = argparse.ArgumentParser(
        description="Kubernetes YAML to JSON Converter", prog="k8s_converter"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    add_api_parser(subparsers)
    add_cli_parser(subparsers)

    args = parser.parse_args()

    if args.command == "api":
        start_server(host=args.host, port=args.port, reload=args.reload)
    elif args.command == "cli":
        # Import and run CLI
        print("Starting CLI...")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
