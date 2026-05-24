import os 
import subprocess
from google.genai import types

def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
        try:
        
            working_file_abs = os.path.abspath(working_directory)
            target_file = os.path.normpath(os.path.join(working_file_abs, file_path))
            # Will be True or False
            valid_target_file = os.path.commonpath([working_file_abs, target_file]) == working_file_abs
            if valid_target_file is False:
                return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
            if os.path.isfile(target_file) is False:
                 return f'Error: "{file_path}" does not exist or is not a regular file'
            if target_file.endswith('.py') is False:
                 return f'Error: "{file_path}" is not a Python file'

            command = ["python", target_file]
            if args is not None:
                 command.extend(args)

    
            result = subprocess.run(command, cwd=working_file_abs, capture_output=True, timeout=30, text=True,)
            return_statement = []
            if result.returncode != 0:
                 return_statement.append(f"Process exited with code {result.returncode}")
            if result.stderr == "" and result.stdout == "":
                 return_statement.append("No output produced")
            if result.stdout != "":
                return_statement.append(f"STDOUT:{result.stdout}")
            if result.stderr != "":
                return_statement.append(f"STDERR:{result.stderr}\n")
            
            return "\n".join(return_statement)
        

        
        except Exception as e:
            return f"Error: executing python file: {e}"
        

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs provided python file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        required=["file_path"],
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="file path to the python file to be run",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                ),
                description="optional arguments to pass to the python file",
            ),
        },
    ),
)

