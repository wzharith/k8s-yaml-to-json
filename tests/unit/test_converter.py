import pytest
from k8s_converter.core.converter import parse_k8s_yaml, K8sParserError


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
