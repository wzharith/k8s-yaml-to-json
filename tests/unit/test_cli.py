from pathlib import Path
from unittest.mock import patch, MagicMock

from k8s_converter.cli.args import add_common_cli_args, create_cli_parser
from k8s_converter.cli.bulk_converter import run_cli


class TestCliBasic:
    """Basic test cases for the CLI functionality"""

    def test_add_common_cli_args(self):
        """Test adding common CLI arguments to a parser"""
        parser = MagicMock()
        add_common_cli_args(parser)

        # Verify that add_argument was called for each expected argument
        assert parser.add_argument.call_count >= 5

        # Check that the input argument was added
        parser.add_argument.assert_any_call(
            "input", help="Input YAML file or directory containing YAML files"
        )

    def test_create_cli_parser(self):
        """Test creating a CLI parser"""
        parser = create_cli_parser()
        assert parser is not None

        # Test parsing arguments
        args = parser.parse_args(["test_input", "-o", "test_output"])
        assert args.input == "test_input"
        assert args.output == "test_output"

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.mkdir")
    @patch("k8s_converter.cli.bulk_converter.process_file")
    def test_run_cli_file(
        self, mock_process_file, mock_mkdir, mock_is_dir, mock_is_file, mock_exists
    ):
        """Test running the CLI with a file input"""
        # Mock the path checks
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_is_dir.return_value = False

        # Mock the process_file function to return success
        mock_process_file.return_value = True

        # Create mock args
        args = MagicMock()
        args.input = "test.yaml"
        args.output = "output_dir"
        args.verbose = False
        args.no_pretty = False
        args.recursive = False

        # Run the CLI
        exit_code = run_cli(args)

        # Verify the result
        assert exit_code == 0
        mock_process_file.assert_called_once()
        mock_mkdir.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.mkdir")
    @patch("k8s_converter.cli.bulk_converter.process_directory")
    def test_run_cli_directory(
        self, mock_process_directory, mock_mkdir, mock_is_dir, mock_is_file, mock_exists
    ):
        """Test running the CLI with a directory input"""
        # Mock the path checks
        mock_exists.return_value = True
        mock_is_file.return_value = False
        mock_is_dir.return_value = True

        # Mock the process_directory function to return success
        mock_process_directory.return_value = (3, 3)

        # Create mock args
        args = MagicMock()
        args.input = "test_dir"
        args.output = "output_dir"
        args.verbose = True
        args.no_pretty = True
        args.recursive = True

        # Run the CLI
        exit_code = run_cli(args)

        # Verify the result
        assert exit_code == 0
        mock_process_directory.assert_called_once()
        # Note: mkdir is not called directly in this code path as it's handled within process_directory

        # Verify that process_directory was called with the correct paths
        # The first two positional arguments should be Path objects
        args, kwargs = mock_process_directory.call_args
        assert len(args) >= 2
        assert isinstance(args[0], Path)  # input_dir
        assert isinstance(args[1], Path)  # output_dir

        # Check if recursive was passed correctly (might be positional or keyword)
        if "recursive" in kwargs:
            assert kwargs["recursive"] is True

    @patch("pathlib.Path.exists")
    def test_run_cli_nonexistent_path(self, mock_exists):
        """Test running the CLI with a nonexistent path"""
        # Mock the path check to return False
        mock_exists.return_value = False

        # Create mock args
        args = MagicMock()
        args.input = "nonexistent_path"
        args.output = "output_dir"
        args.verbose = False
        args.no_pretty = False
        args.recursive = False

        # Run the CLI
        exit_code = run_cli(args)

        # Verify the result
        assert exit_code == 1  # Should return error code
