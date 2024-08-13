from pydantic import field_validator


@field_validator('api_key', mode='before')
def validate_api_key(cls, v):
    if not v:
        raise ValueError("API Key for OpenAI not found.")
    return v
