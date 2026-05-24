import os
from google.genai import types


def write_file(working_directory: str, file_path: str, content: str) -> str:
    
    try:
        working_file_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_file_abs, file_path))
        # Will be True or False
        valid_target_file = os.path.commonpath([working_file_abs, target_file]) == working_file_abs
        if valid_target_file is False:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        if os.path.isdir(target_file) is True:
            return f'Error: Cannot write to "{file_path}" as it is a directory'
        
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, "w") as f:
                f.write(content)
                return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        
    except Exception as e:
        return f"Error: {e}"

schema_write_file = types.FunctionDeclaration(
     name="write_file",
     description="Writes to a file from the specified path",
     parameters=types.Schema(
          type=types.Type.OBJECT,
          required=["file_path","content"],
          properties={
               "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="File to be written on."
               ),
               "content": types.Schema(
                    type=types.Type.STRING,
                    description="content to be written to file"
               )
          }
     )
)