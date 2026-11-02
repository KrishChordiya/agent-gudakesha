from pydantic import BaseModel, Field, ConfigDict
from typing import Any

# Result
class ToolResult(BaseModel):
    status : str
    data: Any = None
    error_message:str|None =  None
    error_code:str|None = None

# File Tools
class ReadFileArgs(BaseModel):
    file_path:str

class WriteFileArgs(BaseModel):
    file_path:str
    content:str

# Bash Tool
class BashArgs(BaseModel):
    command :str
    timeout:int= Field(default=30, ge=1, le=120)

# Web Tool
class WebSearchArgs(BaseModel):
    query:str
    max_results:int=Field(default=5, ge=1, le=10)