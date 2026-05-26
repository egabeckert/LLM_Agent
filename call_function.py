import os
from collections.abc import Callable
from functions.get_files_info import get_files_info
from functions.write_file import write_file
from functions.run_python_file import run_python_file
from functions.get_file_content import get_file_content
from functions.remove_directory import remove_directory
from functions.create_directory import create_directory
from functions.remove_file import remove_file
from functions.move_file import move_file

# Mapping of function names to actual Python implementations
function_map: dict[str, Callable[..., str]] = {
    "get_file_content": get_file_content,
    "get_files_info": get_files_info,
    "run_python_file": run_python_file,
    "write_file": write_file,
    "remove_directory": remove_directory,
    "create_directory": create_directory,
    "remove_file": remove_file,
    "move_file": move_file,
}

def call_function(
    function_name: str, function_args: dict, verbose: bool = False
) -> dict:
    
    # Trimmed down call reporting to only display tool calls
    print(f" - Calling function: {function_name}")

    # 2. Validation
    if function_name not in function_map:
        return {"error": f"Unknown function: {function_name}"}
    
    # 3. Execution
    try:
        # Call the mapped function with the unpacked arguments
        function_result = function_map[function_name](**function_args)
        
        return {"result": function_result}
    except Exception as e:
        # If the actual python function crashes, return the error to the LLM
        return {"error": str(e)}
