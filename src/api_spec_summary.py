from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
    
class ApiSummary(BaseModel):
    path: str
    method: str
    summary: str
    
@tool("search_apis")
def search_apis() -> list[ApiSummary]:
    """Search all APIs in the OpenAPI spec"""
    return get_all_apis("data/apis/openapi-specification.yaml")

import yaml

def get_all_apis(openapi_spec_path):
    """List all avialble APIs """
    with open(openapi_spec_path, 'r') as f:
        spec_dict = yaml.safe_load(f)

    api_summaries = []

    # Get paths and operations from the spec
    paths = spec_dict.get('paths', {})

    # Iterate over each path and its operations
    for path, path_details in paths.items():
        for method, description in path_details.items():
            if type(description) is not dict:
                continue 
            summary = description.get('summary', '')
            api_summaries.append(ApiSummary(path=path, method=method.upper(), summary=summary))

    return api_summaries