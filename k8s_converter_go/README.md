# Kubernetes YAML to JSON Converter

A simple command-line tool written in Go that converts Kubernetes YAML files to JSON format.

## Features

- Convert Kubernetes YAML files to JSON format
- Support for all Kubernetes resource types
- Pretty-printed JSON output
- Option to save output to a file or print to stdout

## Prerequisites

- Go 1.16 or higher

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd k8s_converter_go
```

2. Install dependencies:
```bash
go mod download
```

## Usage

The converter supports two modes of operation:

1. Print JSON to stdout:
```bash
go run main.go -input <yaml-file>
```

2. Save JSON to a file:
```bash
go run main.go -input <yaml-file> -output <json-file>
```

### Example

Convert a Kubernetes deployment YAML to JSON:
```bash
# Print to stdout
go run main.go -input ../k8s_sample/nginx/deployment.yaml

# Save to file
go run main.go -input ../k8s_sample/nginx/deployment.yaml -output deployment.json
```

## Testing

Run the unit tests:
```bash
# Run tests
go test

# Run tests with verbose output
go test -v
```

The tests verify:
- YAML file reading
- JSON file writing
- File operations
- Basic conversion functionality

## Sample Files

The repository includes sample Kubernetes YAML files in the `k8s_sample` directory:

### Nginx Application
- `deployment.yaml`: Nginx deployment configuration
- `service.yaml`: Nginx service configuration
- `ingress.yaml`: Nginx ingress configuration
- `configmap.yaml`: Nginx configuration map
- `secret.yaml`: Nginx secrets

### Development Environment
- `service.yaml`: Development service configuration

## Building

To build the binary:
```bash
go build -o k8s-converter
```

Then you can run it directly:
```bash
./k8s-converter -input <yaml-file> [-output <json-file>]
```

