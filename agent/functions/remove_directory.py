import os
import sys

def remove_directory(directory_path: str) -> dict:
    try:
        os.rmdir(directory_path)
        return {"result": f"Directory '{directory_path}' removed successfully."}
    except OSError as e:
        return {"error": f"Error removing directory '{directory_path}': {e}"}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        path_to_remove = sys.argv[1]
        result = remove_directory(path_to_remove)
        if "error" in result:
            print(result["error"])
        else:
            print(result["result"])
    else:
        print("Usage: python remove_directory.py <directory_path>")

schema_remove_directory = {
    "name": "remove_directory",
    "description": "removes directory from the specified path.",
    "parameters": {
        "type": "object",
        "properties": {
            "directory_path": {
                "type": "string",
                "description": "The path of the directory to remove",
            },
        },
        "required": ["directory_path"],
    },
}
