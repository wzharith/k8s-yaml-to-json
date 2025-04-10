import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Union
from jsonschema import validate
from yaml.parser import ParserError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Basic Kubernetes resource schema for validation
K8S_SCHEMA = {
    "type": "object",
    "required": ["apiVersion", "kind", "metadata"],
    "properties": {
        "apiVersion": {"type": "string"},
        "kind": {"type": "string"},
        "metadata": {"type": "object", "properties": {"name": {"type": "string"}}},
    },
}


class K8sParserError(Exception):
    """Custom exception for K8s parsing errors"""

    pass


def parse_k8s_yaml(yaml_content: str) -> Dict[str, Any]:
    """
    Parse Kubernetes YAML manifest and convert it to dictionary format.

    Args:
        yaml_content (str): YAML string containing Kubernetes resource definition

    Returns:
        Dict[str, Any]: Dictionary representation of the Kubernetes resource

    Raises:
        K8sParserError: If the YAML is invalid or doesn't conform to K8s resource format
    """
    try:
        logger.debug("Attempting to parse YAML content")
        k8s_dict = yaml.safe_load(yaml_content)

        if not isinstance(k8s_dict, dict):
            raise K8sParserError("Invalid YAML: must be a mapping")

        # Validate against basic K8s schema
        logger.debug("Validating against Kubernetes schema")
        validate(instance=k8s_dict, schema=K8S_SCHEMA)

        return k8s_dict

    except ParserError as e:
        logger.error(f"YAML parsing error: {str(e)}")
        raise K8sParserError(f"Invalid YAML format: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing Kubernetes resource: {str(e)}")
        raise K8sParserError(str(e))


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
        # Create output filename with .json extension
        output_file = output_dir / f"{input_file.stem}.json"

        # Convert YAML to JSON
        logger.info(f"Processing {input_file}")
        json_data = yaml_file_to_json(input_file)

        # Save JSON to file
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
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all YAML files in the directory
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


def yaml_file_to_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Convert a Kubernetes YAML file to a dictionary.

    Args:
        file_path (Union[str, pathlib.Path]): Path to the YAML file

    Returns:
        Dict[str, Any]: Dictionary representation of the Kubernetes resource

    Raises:
        K8sParserError: If the file cannot be read or the YAML is invalid
    """
    try:
        with open(file_path, "r") as f:
            yaml_content = f.read()
        return parse_k8s_yaml(yaml_content)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise K8sParserError(f"File not found: {file_path}")
    except PermissionError:
        logger.error(f"Permission denied when reading file: {file_path}")
        raise K8sParserError(f"Permission denied when reading file: {file_path}")
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise K8sParserError(f"Error reading file {file_path}: {str(e)}")


def save_json_to_file(
    json_data: Dict[str, Any],
    output_path: Union[str, Path],
    pretty: bool = True,
) -> None:
    """
    Save JSON data to a file.

    Args:
        json_data (Dict[str, Any]): Dictionary to save as JSON
        output_path (Union[str, pathlib.Path]): Path to save the JSON file
        pretty (bool): Whether to format JSON with indentation

    Raises:
        K8sParserError: If the file cannot be written
    """
    try:
        indent = 2 if pretty else None
        with open(output_path, "w") as f:
            json.dump(json_data, f, indent=indent)
        logger.info(f"JSON saved to {output_path}")
    except PermissionError:
        logger.error(f"Permission denied when writing to file: {output_path}")
        raise K8sParserError(f"Permission denied when writing to file: {output_path}")
    except Exception as e:
        logger.error(f"Error writing to file {output_path}: {str(e)}")
        raise K8sParserError(f"Error writing to file {output_path}: {str(e)}")
