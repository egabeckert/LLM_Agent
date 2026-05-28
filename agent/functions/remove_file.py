import os
import sys

def remove_file(file_path: str) -> dict:
    try:
        os.remove(file_path)
        return {"result": f"File '{file_path}' removed successfully."}
    except OSError as e:
        return {"error": f"Error removing file '{file_path}': {e}"}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        path_to_remove = sys.argv[1]
        result = remove_file(path_to_remove)
        if "error" in result:
            print(result["error"])
        else:
            print(result["result"])
    else:
        print("Usage: python remove_file.py <file_path>")

schema_remove_file = {
    "name": "remove_file",
    "description": "removes a file from the specified path.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path of the file to remove",
            },
        },
        "required": ["file_path"],
    },
}

