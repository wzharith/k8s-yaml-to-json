import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from k8s_converter.cli.bulk_converter import process_directory, process_file
from k8s_converter.core.converter import K8sParserError


class TestBulkConverter:
    """Test cases for the bulk converter functionality"""

    @pytest.fixture
    def sample_yaml_content(self):
        """Sample YAML content for testing"""
        return """
        apiVersion: v1
        kind: Pod
        metadata:
          name: test-pod
        spec:
          containers:
          - name: nginx
            image: nginx:latest
        """

    def test_process_file_error_handling(self, tmp_path):
        """Test process_file error handling for invalid YAML"""
        # Create a temporary YAML file with invalid content
        input_file = tmp_path / "invalid.yaml"
        input_file.write_text("invalid: yaml: content: - [")

        # Create a temporary output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Process the file - should return False due to error
        result = process_file(input_file, output_dir)
        assert result is False

    @patch("k8s_converter.cli.bulk_converter.yaml_file_to_json")
    def test_process_file_unexpected_error(self, mock_yaml_to_json, tmp_path):
        """Test process_file handling of unexpected errors"""
        # Mock yaml_file_to_json to raise an unexpected exception
        mock_yaml_to_json.side_effect = Exception("Unexpected error")

        # Create a temporary YAML file
        input_file = tmp_path / "test.yaml"
        input_file.write_text("apiVersion: v1\nkind: Pod")

        # Create a temporary output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Process the file - should return False due to unexpected error
        result = process_file(input_file, output_dir)
        assert result is False

    @patch("k8s_converter.cli.bulk_converter.process_file")
    def test_process_directory_recursive(self, mock_process_file, tmp_path):
        """Test process_directory with recursive option"""
        # Create directory structure
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        subdir = input_dir / "subdir"
        subdir.mkdir()

        # Create test files
        yaml_file1 = input_dir / "test1.yaml"
        yaml_file1.write_text("dummy content")
        yaml_file2 = subdir / "test2.yaml"
        yaml_file2.write_text("dummy content")

        # Mock process_file to return True
        mock_process_file.return_value = True

        # Create output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Process directory with recursive=True
        successful, total = process_directory(input_dir, output_dir, recursive=True)

        # Verify results
        assert successful == 2
        assert total == 2
        assert mock_process_file.call_count == 2
