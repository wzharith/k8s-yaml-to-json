import pytest
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


# Common test fixtures
@pytest.fixture
def sample_pod_yaml():
    """Return a sample Kubernetes Pod YAML for testing"""
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


@pytest.fixture
def sample_deployment_yaml():
    """Return a sample Kubernetes Deployment YAML for testing"""
    return """
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
    """


@pytest.fixture
def invalid_yaml():
    """Return an invalid YAML string for testing"""
    return """
    apiVersion: v1
    kind: Pod
    metadata:
      name: test-pod
      labels:
        app: test
      annotations:
    spec:  # Missing colon after annotations
      containers:
      - name: nginx
        image: nginx:latest
    """


@pytest.fixture
def non_k8s_yaml():
    """Return a valid YAML that is not a Kubernetes resource"""
    return """
    foo: bar
    items:
      - one
      - two
    """
