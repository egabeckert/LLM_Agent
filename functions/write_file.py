import os
from config import SANDBOX_ROOT

def write_file(file_path: str, content: str, **kwargs) -> str:
    try:
        print(f"DEBUG: Attempting to write {len(content)} chars to {file_path}")
        # Handle potential hallucinated parameter names
        if "path" in kwargs and not file_path:
            file_path = kwargs["path"]

        base_path = os.path.abspath(SANDBOX_ROOT)
        target_file = os.path.normpath(os.path.join(base_path, file_path))
        
        if not os.path.commonpath([base_path, target_file]) == base_path:
            return f'Error: Access denied. "{file_path}" is outside the sandbox.'
        
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, "w") as f:
            f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'        
        
    except Exception as e:
        return f"Error: {e}"

schema_write_file = {
    "name": "write_file",
    "description": "Writes content to a file at the specified path relative to the sandbox root.",
    "parameters": {
        "type": "object",
        "required": ["file_path", "content"],
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path where the file should be created or overwritten."
            },
            "content": {
                "type": "string",
                "description": "The string content to write into the file."
            }
        }
    }
}