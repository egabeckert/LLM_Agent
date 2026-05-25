import os
import sys
def remove_directory(directory_path):
    if __name__ == "__main__":
        if len(sys.argv) > 1:
            path_to_remove = sys.argv[1]
        try:
            os.rmdir(path_to_remove)
            print(f"Directory '{path_to_remove}' removed successfully.")
        except OSError as e:
            print(f"Error removing directory '{path_to_remove}': {e}")
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