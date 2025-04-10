from k8s_converter.api.schemas import YamlRequest, ConversionResponse


class TestSchemas:
    """Test cases for the API schemas"""

    def test_yaml_request(self):
        """Test YamlRequest schema validation"""
        # Valid request
        request = YamlRequest(yaml_content="apiVersion: v1\nkind: Pod")
        assert request.yaml_content == "apiVersion: v1\nkind: Pod"

        # Empty content should be valid at schema level (validation happens later)
        request = YamlRequest(yaml_content="")
        assert request.yaml_content == ""

    def test_conversion_response(self):
        """Test ConversionResponse schema validation"""
        # Valid response
        response = ConversionResponse(
            json_content={"apiVersion": "v1", "kind": "Pod"},
            message="YAML converted successfully",
        )
        assert response.json_content["kind"] == "Pod"
        assert response.message == "YAML converted successfully"

        # Response with empty content
        response = ConversionResponse(json_content={}, message="Empty YAML converted")
        assert response.json_content == {}
        assert response.message == "Empty YAML converted"
