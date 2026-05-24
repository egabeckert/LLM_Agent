import os
from config import MAX_CHARS
from google.genai import types

def get_file_content(working_directory: str, file_path: str) -> str:
        
    try:
        working_path_abs = os.path.abspath(working_directory)
        target_path = os.path.normpath(os.path.join(working_path_abs, file_path))
        # Will be True or False
        valid_target_path = os.path.commonpath([working_path_abs, target_path]) == working_path_abs
        if valid_target_path is False:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        
        if os.path.isfile(target_path) is False:
            return f'Error: File not found or is not a regular file: "{file_path}"'

        
        with open(target_path, "r") as f:
            file_content_string = f.read(MAX_CHARS)
            # After reading the first MAX_CHARS...
            if f.read(1):
                file_content_string += f'[...File "{target_path}" truncated at {MAX_CHARS} characters]'
        return file_content_string
    except Exception as e:
         return f"Error: {e}"
    
schema_get_file_content = types.FunctionDeclaration(
    name = "get_file_content",
    description="path to the file to read, relative to the working directory",
    parameters=types.Schema(
            type=types.Type.OBJECT,
            required=["file_path"],
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="File contents from specified path, relative to the working directory (default is the working directory itself)"
                    )
                }
        )
    )
         

    