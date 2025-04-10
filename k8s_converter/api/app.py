from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body, Query
from k8s_converter.core.converter import parse_k8s_yaml, K8sParserError
from k8s_converter.api.schemas import ConversionResponse
from k8s_converter.core.logger import logger

import sys
import os
import uvicorn

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


app = FastAPI(
    title="Kubernetes YAML to JSON Converter API",
    description="API for converting Kubernetes YAML manifests to JSON",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Kubernetes YAML to JSON Converter API",
        "version": "1.0.0",
        "endpoints": [
            {
                "path": "/convert/file",
                "method": "POST",
                "description": "Convert YAML file to JSON",
            },
            {
                "path": "/convert/raw",
                "method": "POST",
                "description": "Convert raw YAML text to JSON",
            },
        ],
    }


@app.post("/convert/raw", response_model=ConversionResponse)
async def convert_raw_yaml(yaml_content: str = Body(..., media_type="text/plain")):
    """
    Convert raw YAML text to JSON. This endpoint accepts plain text YAML content
    without requiring JSON encoding, making it easier to send multi-line YAML.

    Args:
        yaml_content (str): Raw YAML content as plain text

    Returns:
        ConversionResponse: JSON content and status message
    """
    try:
        # Parse YAML content
        k8s_dict = parse_k8s_yaml(yaml_content)

        # Return JSON response
        return ConversionResponse(
            json_content=k8s_dict, message="YAML converted successfully"
        )
    except K8sParserError as e:
        logger.error(f"YAML parsing error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/convert/file", response_model=ConversionResponse)
async def convert_yaml_file(file: UploadFile = File(...)):
    """
    Convert uploaded YAML file to JSON

    Args:
        file (UploadFile): YAML file to convert

    Returns:
        ConversionResponse: JSON content and status message
    """
    try:
        # Read file content
        content = await file.read()
        yaml_content = content.decode("utf-8")

        # Parse YAML content
        k8s_dict = parse_k8s_yaml(yaml_content)

        # Return JSON response
        return ConversionResponse(
            json_content=k8s_dict,
            message=f"File '{file.filename}' converted successfully",
        )
    except K8sParserError as e:
        logger.error(f"YAML parsing error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except UnicodeDecodeError:
        logger.error("File encoding error")
        raise HTTPException(
            status_code=400, detail="File encoding error: file must be UTF-8 encoded"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    Start the FastAPI server

    Args:
        host (str): Host to bind to
        port (int): Port to bind to
        reload (bool): Whether to enable auto-reload
    """
    uvicorn.run("k8s_converter.api.app:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    # Start the server when script is run directly
    start_server(reload=True)
