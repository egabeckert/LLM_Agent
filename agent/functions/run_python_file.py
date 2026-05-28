import os 
import subprocess
from agent.config import SANDBOX_ROOT
import sys

# 1. Made working_directory optional and added **kwargs
def run_python_file(
    file_path: str, args: list[str] | None = None, working_directory: str = ".", **kwargs
) -> str:
    try:
        # 2. Capture common hallucinated names
        if "directory" in kwargs:
            working_directory = kwargs["directory"]

        base_path = os.path.abspath(SANDBOX_ROOT)
        # We combine sandbox + working_dir + file_path
        target_dir = os.path.normpath(os.path.join(base_path, working_directory))
        target_file = os.path.normpath(os.path.join(target_dir, file_path))
        
        # Security Gatekeeper: Ensure we are still inside the sandbox
        if not os.path.commonpath([base_path, target_file]) == base_path:
            return f'Error: Access denied. "{file_path}" is outside the sandbox.'

        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not target_file.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file'

        command = [sys.executable, target_file]
        if args is not None:
            command.extend(args)

        # 3. Use target_dir for cwd to ensure the script runs where it expects
        result = subprocess.run(
            command, 
            cwd=target_dir, 
            capture_output=True, 
            timeout=30, 
            text=True
        )
        
        return_statement = []
        if result.returncode != 0:
            return_statement.append(f"Process exited with code {result.returncode}")
        if not result.stderr and not result.stdout:
            return_statement.append("No output produced")
        if result.stdout:
            return_statement.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            return_statement.append(f"STDERR:\n{result.stderr}")
            
        return "\n".join(return_statement)
        
    except Exception as e:
        return f"Error executing python file: {e}"

schema_run_python_file = {
    "name": "run_python_file",
    "description": "Executes a Python file within the sandbox environment.",
    "parameters": {
        "type": "object",
        "required": ["file_path"],
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the python file to be run, relative to the working directory.",
            },
            "working_directory": {
                "type": "string",
                "description": "Optional directory to run the script from (defaults to sandbox root).",
            },
            "args": {
                "type": "array",
                "items": {
                    "type": "string",
                },
                "description": "Optional arguments to pass to the python file.",
            },
        },
    },
}