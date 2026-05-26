import os
from config import MAX_CHARS, SANDBOX_ROOT

def get_file_content(file_path: str, **kwargs) -> str:
    try:
        # Handle potential hallucinated parameter names (like 'path')
        if "path" in kwargs and not file_path:
            file_path = kwargs["path"]

        # 1. Enforce the sandbox as the base
        base_path = os.path.abspath(SANDBOX_ROOT)
        
        # 2. Resolve the target path
        target_path = os.path.normpath(os.path.join(base_path, file_path))
        
        # 3. Security check: is the result still inside the base?
        if not os.path.commonpath([base_path, target_path]) == base_path:
            return f'Error: Access denied. "{file_path}" is outside the sandbox.'
        
        # 4. Check existence
        if not os.path.isfile(target_path):
            return f'Error: File not found: "{file_path}"'

        # 5. Read the safe path
        with open(target_path, "r") as f:
            file_content_string = f.read(MAX_CHARS)
            if f.read(1):
                file_content_string += f'\n[...File truncated at {MAX_CHARS} characters]'
        return file_content_string

    except Exception as e:
         return f"Error: {e}"
    
schema_get_file_content = {
    "name": "get_file_content",
    "description": "Reads the content of a specific file from the sandbox.",
    "parameters": {
        "type": "object",
        "required": ["file_path"],
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to read, relative to the sandbox root."
            }
        }
    }
}