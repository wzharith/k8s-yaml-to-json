# Kubernetes YAML to JSON Converter

A Python utility for converting Kubernetes YAML manifests to JSON format with validation.

## Features

- Convert Kubernetes YAML manifests to JSON
- Validate basic Kubernetes resource structure
- Provides detailed error handling and logging
- Two separate functionalities:
  - **API Server**: On-demand conversion via REST API
  - **CLI Tool**: Bulk conversion of files and directories

## Installation

### From Source

1. Clone the repository
2. Create a virtual environment Python 3.12 (venv/conda):

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### API Server

Start the API server for on-demand conversion:

```bash
# Start the API server on default port 8000
python k8s_converter api

# Specify host and port
python k8s_converter api --host 127.0.0.1 --port 8080

# Enable auto-reload for development
python k8s_converter api --reload
```

#### API Endpoints

- `GET /`: API information
- `POST /convert/raw`: Convert raw YAML text to JSON
  - Content-Type: `text/plain`
  - Request body: Raw YAML content with actual newlines
- `POST /convert/file`: Convert uploaded YAML file to JSON
  - Form data: `file` (file upload)
- `POST /convert/batch`: Convert multiple YAML files to JSON
  - Form data: `files` (multiple file uploads)
  - Returns results for each file with success/failure status

#### Example API Usage

Using curl to convert raw YAML text (plain text format):

```bash
curl -X 'POST' 'http://localhost:8000/convert/raw' \
  -H 'Content-Type: text/plain' \
  -d 'apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: nginx
    image: nginx:latest'
```

Using curl to convert a single file:

```bash
curl -X 'POST' 'http://localhost:8000/convert/file' \
  -H 'accept: application/json' \
  -F 'file=@/path/to/your-file.yaml' \
```

Using curl to convert multiple files:

```bash
curl -X 'POST' 'http://localhost:8000/convert/batch' \
  -H 'accept: application/json' \
  -F 'files=@/path/to/file1.yaml' \
  -F 'files=@/path/to/file2.yaml' \
  -F 'pretty=true'
```

#### Example CLI Usage

Use the CLI tool for bulk conversion of YAML files:

```bash
# Convert a single file
python k8s_converter cli path/to/file.yaml -o output/dir

# Convert all YAML files in a directory
python k8s_converter cli path/to/directory -o output/dir

# Recursively convert files in subdirectories
python k8s_converter cli path/to/directory -o output/dir -r

# Output minified JSON
python k8s_converter cli path/to/directory -o output/dir --no-pretty

# Enable verbose logging
python k8s_converter cli path/to/directory -o output/dir -v
```

## Development

### Running Tests

The project uses pytest for testing. To run the tests:

1. Install development dependencies:

```bash
pip install -r requirements.txt
```

2. Run the tests:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=k8s_converter

# Run only unit tests
pytest tests/unit

# Run only integration tests
pytest tests/integration
```

## API Response Formats

### Single File Conversion

```json
{
  "json_content": {
    "apiVersion": "v1",
    "kind": "Pod",
    "metadata": {
      "name": "my-pod"
    },
    "spec": {
      "containers": [
        {
          "name": "nginx",
          "image": "nginx:latest"
        }
      ]
    }
  },
  "message": "YAML converted successfully"
}
```

### Batch Conversion

```json
{
  "results": [
    {
      "filename": "file1.yaml",
      "status": "success",
      "json_content": { ... }
    },
    {
      "filename": "file2.yaml",
      "status": "error",
      "error": "Error message"
    }
  ],
  "successful": 1,
  "failed": 1,
  "message": "Processed 2 files: 1 successful, 1 failed"
}
```

## Project Structure

```bash
.
├── k8s_converter
│   ├── api
│   │   ├── app.py
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── cli
│   │   ├── args.py
│   │   ├── bulk_converter.py
│   │   └── __init__.py
│   ├── core
│   │   ├── converter.py
│   │   ├── __init__.py
│   │   └── logger.py
│   ├── __init__.py
│   └── __main__.py
├── k8s_converter_go # Go version of the converter
│   ├── go.mod
│   ├── go.sum
│   ├── invalid.yaml
│   ├── main.go
│   ├── main_test.go
│   └── README.md
├── k8s_sample
│   ├── dev
│   │   └── service.yaml
│   └── nginx
│       ├── configmap.yaml
│       ├── deployment.yaml
│       ├── ingress.yaml
│       ├── secret.yaml
│       └── service.yaml
├── pytest.ini
├── README.md
├── requirements.txt
└── tests
    ├── conftest.py
    ├── integration
    │   └── test_api.py
    └── unit
        ├── test_bulk_converter.py
        ├── test_cli.py
        ├── test_converter.py
        ├── test_logger.py
        └── test_schemas.py
```
