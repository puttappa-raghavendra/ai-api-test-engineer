from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

class APIInput(BaseModel):
    """API path input to extract the API spec"""
    path: str = Field(..., description="The OpenAPI spec for the API Endpoint")
    method: str = Field(..., description="The HTTP method for the API Endpoint")

# tool to extract the API spec from the given text
@tool("fetch_api_openapi_specification", args_schema=APIInput)
def fetch_api_openapi_specification(path: str, method: str) -> str:
    """Tool help to extract the API specification from the given API path. Use the path and method as parameters to extract the API spec."""
    return get_api_spec(path, method, "data/apis/openapi-specification.yaml")


import yaml

# Function to load and summarize APIs from an OpenAPI specification file
def get_api_spec(path, method, openapi_spec_path) -> str:
    
    # Load the OpenAPI specification file (assuming it's in YAML format)
    with open(openapi_spec_path, 'r') as f:
        spec_dict = yaml.safe_load(f)

    # Get paths and operations from the spec
    paths = spec_dict.get('paths', {})

       # Retrieve paths from the OpenAPI spec
    paths = spec_dict.get('paths', {})

    # Check if the specified path exists in the spec
    if path in paths:
        
        # Retrieve the path item corresponding to the specified path
        path_item = paths[path]

        # Check if the specified method exists for the path
        if method.lower() in path_item:
            # Retrieve the operation details for the specified method
            operation_details = path_item[method.lower()]

            # Return the operation details
            return operation_details

    return None

