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
2. Create a virtual environment:

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
python k8s-converter api

# Specify host and port
python k8s-converter api --host 127.0.0.1 --port 8080

# Enable auto-reload for development
python k8s-converter api --reload
```

#### API Endpoints

- `GET /`: API information
- `POST /convert/raw`: Convert raw YAML text to JSON
  - Content-Type: `text/plain`
  - Request body: Raw YAML content with actual newlines
  - Query param: `pretty` (boolean)
- `POST /convert/file`: Convert uploaded YAML file to JSON
  - Form data: `file` (file upload) and `pretty` (boolean)

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
