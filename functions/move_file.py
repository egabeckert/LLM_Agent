import os
import sys

def move_file(source_path: str, destination_path: str) -> dict:
    """
    Moves or renames a file from the source_path to the destination_path.
    """
    try:
        # Ensure the destination directory exists if the destination_path includes a directory
        destination_dir = os.path.dirname(destination_path)
        if destination_dir and not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        os.rename(source_path, destination_path)
        return {"result": f"File '{source_path}' moved/renamed successfully to '{destination_path}'."}
    except FileNotFoundError:
        return {"error": f"Error: Source file '{source_path}' not found."}
    except PermissionError:
        return {"error": f"Error: Permission denied to move file '{source_path}' or write to '{destination_path}'."}
    except OSError as e:
        return {"error": f"Error moving/renaming file: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python move_file.py <source_path> <destination_path>")
        sys.exit(1)

    source_path = sys.argv[1]
    destination_path = sys.argv[2]
    result = move_file(source_path, destination_path)
    if "error" in result:
        print(result["error"])
    else:
        print(result["result"])

schema_move_file = {
    "name": "move_file",
    "description": "Moves or renames a file from the source_path to the destination_path.",
    "parameters": {
        "type": "object",
        "properties": {
            "source_path": {
                "type": "string",
                "description": "The path of the file to move.",
            },
            "destination_path": {
                "type": "string",
                "description": "The new path for the file, including the new file name if renaming.",
            },
        },
        "required": ["source_path", "destination_path"],
    },
}
