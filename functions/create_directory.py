import os

def create_directory(directory_path):
    """
    Creates a directory at the specified path if it doesn't already exist.

    Args:
        directory_path (str): The path of the directory to create.
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"Directory '{directory_path}' created successfully or already exists.")
    except OSError as e:
        print(f"Error creating directory '{directory_path}': {e}")

if __name__ == "__main__":
    # Example usage:
    # To be called from another script or directly with arguments
    import sys
    if len(sys.argv) > 1:
        path_to_create = sys.argv[1]
        create_directory(path_to_create)
    else:
        print("Usage: python create_directory.py <directory_path>")

schema_create_directory = {
    "name": "create_directory",
    "description": "Creates a directory at the specified path if it doesn't already exist.",
    "parameters": {
        "type": "object",
        "properties": {
            "directory_path": {
                "type": "string",
                "description": "The path of the directory to create.",
            },
        },
        "required": ["directory_path"],
    },
}
