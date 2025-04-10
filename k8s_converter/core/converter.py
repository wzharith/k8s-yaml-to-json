#!/usr/bin/env python3

import yaml
import logging
from typing import Dict, Any
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
