import pytest
import json
from k8s_converter.core.converter import (
    parse_k8s_yaml,
    K8sParserError,
    yaml_file_to_json,
    save_json_to_file,
    process_file,
    process_directory,
)


class TestConverter:
    """Test cases for the YAML to JSON converter"""

    def test_parse_valid_yaml(self):
        """Test parsing a valid Kubernetes YAML"""
        yaml_content = """
        apiVersion: v1
        kind: Pod
        metadata:
          name: test-pod
        spec:
          containers:
          - name: nginx
            image: nginx:latest
        """
        result = parse_k8s_yaml(yaml_content)
        assert isinstance(result, dict)
        assert result["apiVersion"] == "v1"
        assert result["kind"] == "Pod"
        assert result["metadata"]["name"] == "test-pod"
        assert len(result["spec"]["containers"]) == 1
        assert result["spec"]["containers"][0]["name"] == "nginx"

    def test_parse_invalid_yaml_syntax(self):
        """Test parsing YAML with invalid syntax"""
        yaml_content = """
        apiVersion: v1
        kind: Pod
        metadata:
          name: test-pod
          labels:
            app: test
          this is invalid yaml
        """
        with pytest.raises(K8sParserError):
            parse_k8s_yaml(yaml_content)

    def test_parse_non_kubernetes_yaml(self):
        """Test parsing YAML that is not a Kubernetes resource"""
        yaml_content = """
        foo: bar
        items:
          - one
          - two
        """
        with pytest.raises(K8sParserError):
            parse_k8s_yaml(yaml_content)

    def test_parse_empty_yaml(self):
        """Test parsing empty YAML"""
        with pytest.raises(K8sParserError):
            parse_k8s_yaml("")

    def test_parse_whitespace_only_yaml(self):
        """Test parsing YAML with only whitespace"""
        with pytest.raises(K8sParserError):
            parse_k8s_yaml("   \n   \t   ")

    def test_complex_kubernetes_resource(self):
        """Test parsing a complex Kubernetes resource with nested structures"""
        yaml_content = """
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: nginx-deployment
          labels:
            app: nginx
        spec:
          replicas: 3
          selector:
            matchLabels:
              app: nginx
          template:
            metadata:
              labels:
                app: nginx
            spec:
              containers:
              - name: nginx
                image: nginx:1.14.2
                ports:
                - containerPort: 80
                env:
                - name: NGINX_HOST
                  value: example.com
                - name: NGINX_PORT
                  value: "80"
                resources:
                  limits:
                    cpu: 500m
                    memory: 512Mi
                  requests:
                    cpu: 200m
                    memory: 256Mi
        """
        result = parse_k8s_yaml(yaml_content)
        assert result["kind"] == "Deployment"
        assert result["spec"]["replicas"] == 3
        assert len(result["spec"]["template"]["spec"]["containers"]) == 1
        assert len(result["spec"]["template"]["spec"]["containers"][0]["env"]) == 2
        assert (
            result["spec"]["template"]["spec"]["containers"][0]["resources"]["limits"][
                "memory"
            ]
            == "512Mi"
        )

    def test_yaml_with_special_characters(self):
        """Test parsing YAML with special characters"""
        yaml_content = """
        apiVersion: v1
        kind: ConfigMap
        metadata:
          name: special-config
        data:
          special.how: "Tabs and newlines"
          special.what: 'Quotes: "single" and "double"'
        """
        result = parse_k8s_yaml(yaml_content)
        assert "Tabs and newlines" in result["data"]["special.how"]
        assert "Quotes:" in result["data"]["special.what"]
        assert "single" in result["data"]["special.what"]
        assert "double" in result["data"]["special.what"]

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

    def test_yaml_file_to_json(self, sample_yaml_content, tmp_path):
        """Test converting a YAML file to JSON"""
        # Create a temporary YAML file
        file_path = tmp_path / "test.yaml"
        file_path.write_text(sample_yaml_content)

        # Convert the file to JSON
        result = yaml_file_to_json(file_path)

        # Verify the result
        assert result["kind"] == "Pod"
        assert result["metadata"]["name"] == "test-pod"

    def test_save_json_to_file(self, tmp_path):
        """Test saving JSON to a file"""
        # Sample JSON data
        json_data = {"kind": "Pod", "metadata": {"name": "test-pod"}}

        # Output file path
        output_path = tmp_path / "test.json"

        # Save JSON to file
        save_json_to_file(json_data, output_path)

        # Verify the file was created and contains the correct data
        assert output_path.exists()
        with open(output_path) as f:
            data = json.load(f)
            assert data["kind"] == "Pod"

    def test_process_file(self, sample_yaml_content, tmp_path):
        """Test processing a single file"""
        # Create a temporary YAML file
        input_file = tmp_path / "test.yaml"
        input_file.write_text(sample_yaml_content)

        # Create a temporary output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Process the file
        result = process_file(input_file, output_dir)

        # Verify the result
        assert result is True

        # Check that the output file was created
        output_file = output_dir / "test.json"
        assert output_file.exists()

    def test_process_directory(self, sample_yaml_content, tmp_path):
        """Test processing a directory of YAML files"""
        # Create a temporary directory with YAML files
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        # Create a few YAML files
        for i in range(2):
            file_path = input_dir / f"test{i}.yaml"
            file_path.write_text(sample_yaml_content)

        # Create a temporary output directory
        output_dir = tmp_path / "output"

        # Process the directory
        successful, total = process_directory(input_dir, output_dir)

        # Verify the results
        assert successful == 2
        assert total == 2

        # Check that the output files were created
        for i in range(2):
            output_file = output_dir / f"test{i}.json"
            assert output_file.exists()
