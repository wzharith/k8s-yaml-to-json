from pydantic import BaseModel
from typing import Dict, Any


class YamlRequest(BaseModel):
    yaml_content: str


class ConversionResponse(BaseModel):
    json_content: Dict[str, Any]
    message: str = "Conversion successful"
