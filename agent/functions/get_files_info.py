import os

from agent.config import SANDBOX_ROOT


def get_files_info(directory: str = ".", **kwargs) -> str:
    try:
        # 1. Handle hallucinated arguments first
        if "working_directory" in kwargs:
            directory = kwargs["working_directory"]
            
        # 2. Define your paths
        base_path = os.path.abspath(SANDBOX_ROOT)
        target_dir = os.path.normpath(os.path.join(base_path, directory))
        print(f"DEBUG: base_path={base_path}")
        print(f"DEBUG: directory={directory}")
        print(f"DEBUG: target_dir={target_dir}")
        # 3. Security and existence checks
        if not os.path.commonpath([base_path, target_dir]) == base_path:
            return f'Error: Access denied. "{directory}" is outside the sandbox.'
        
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'
        
        # 4. Define what to ignore
        ignore_list = {".git", "__pycache__", ".venv", "node_modules", ".pytest_cache"}
        
        target_file_info = []
        
        # 5. One single loop to process files
        for item in os.listdir(target_dir):
            # Skip hidden files and ignored directories
            if item.startswith('.') or item in ignore_list:
                continue
                
            item_path = os.path.join(target_dir, item)
            name = item
            is_directory = os.path.isdir(item_path)
            size = os.path.getsize(item_path) if not is_directory else 0
            
            info = f"- {name}: file_size={size} bytes, is_dir={is_directory}"
            target_file_info.append(info)
        results = "\n".join(target_file_info)
        print(f"DEBUG: Returning to LLM:\n{results}")
        return results
    except Exception as e:
        return f"Error: {e}"
        

  
schema_get_files_info = {
    "name": "get_files_info",
    "description": "Lists files in a specified directory relative to the working directory, providing file size and directory status",
    "parameters": {
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Directory path to list files from, relative to the working directory (default is the working directory itself)",
            },
        },
    },
}
