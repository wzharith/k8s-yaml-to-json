from pydantic import BaseModel
from typing import Dict, Any, List


class YamlRequest(BaseModel):
    yaml_content: str


class ConversionResponse(BaseModel):
    json_content: Dict[str, Any]
    message: str = "Conversion successful"


class BatchConversionResponse(BaseModel):
    results: List[Dict[str, Any]]
    successful: int
    failed: int
    message: str = "Batch conversion completed"
