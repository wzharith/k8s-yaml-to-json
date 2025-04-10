from fastapi.testclient import TestClient
from k8s_converter.api.app import app

client = TestClient(app)


class TestApiEndpoints:
    """Test cases for the API endpoints"""

    def test_root_endpoint(self):
        """Test the root endpoint returns API information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data

    def test_convert_raw_yaml_valid(self):
        """Test converting valid raw YAML"""
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
        response = client.post(
            "/convert/raw", content=yaml_content, headers={"Content-Type": "text/plain"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "json_content" in data
        assert data["json_content"]["kind"] == "Pod"
        assert data["json_content"]["metadata"]["name"] == "test-pod"

    def test_convert_raw_yaml_invalid(self):
        """Test converting invalid raw YAML"""
        yaml_content = """
        apiVersion: v1
        kind: Pod
        metadata:
          name: test-pod
          this is invalid yaml
        """
        response = client.post(
            "/convert/raw", content=yaml_content, headers={"Content-Type": "text/plain"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_convert_raw_yaml_non_kubernetes(self):
        """Test converting non-Kubernetes YAML"""
        yaml_content = """
        foo: bar
        items:
          - one
          - two
        """
        response = client.post(
            "/convert/raw", content=yaml_content, headers={"Content-Type": "text/plain"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_convert_raw_yaml_empty(self):
        """Test converting empty YAML"""
        response = client.post(
            "/convert/raw", content="", headers={"Content-Type": "text/plain"}
        )
        assert response.status_code == 422  # FastAPI returns 422 for empty body
        data = response.json()
        assert "detail" in data

    def test_convert_file_valid(self, tmp_path):
        """Test converting a valid YAML file"""
        # Create a temporary YAML file
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
        temp_file = tmp_path / "test.yaml"
        temp_file.write_text(yaml_content)

        with open(temp_file, "rb") as f:
            response = client.post(
                "/convert/file", files={"file": ("test.yaml", f, "text/plain")}
            )

        assert response.status_code == 200
        data = response.json()
        assert "json_content" in data
        assert data["json_content"]["kind"] == "Pod"
        assert data["json_content"]["metadata"]["name"] == "test-pod"

    def test_convert_file_invalid(self, tmp_path):
        """Test converting an invalid YAML file"""
        # Create a temporary invalid YAML file
        yaml_content = """
        apiVersion: v1
        kind: Pod
        metadata:
          name: test-pod
          this is invalid yaml
        """
        temp_file = tmp_path / "invalid.yaml"
        temp_file.write_text(yaml_content)

        with open(temp_file, "rb") as f:
            response = client.post(
                "/convert/file", files={"file": ("invalid.yaml", f, "text/plain")}
            )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_convert_file_non_kubernetes(self, tmp_path):
        """Test converting a non-Kubernetes YAML file"""
        # Create a temporary non-Kubernetes YAML file
        yaml_content = """
        foo: bar
        items:
          - one
          - two
        """
        temp_file = tmp_path / "non-k8s.yaml"
        temp_file.write_text(yaml_content)

        with open(temp_file, "rb") as f:
            response = client.post(
                "/convert/file", files={"file": ("non-k8s.yaml", f, "text/plain")}
            )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_convert_file_binary(self, tmp_path):
        """Test converting a binary file"""
        # Create a temporary binary file
        binary_data = b"\x00\x01\x02\x03\x04\x05"
        temp_file = tmp_path / "binary.bin"
        temp_file.write_bytes(binary_data)

        with open(temp_file, "rb") as f:
            response = client.post(
                "/convert/file",
                files={"file": ("binary.bin", f, "application/octet-stream")},
            )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
