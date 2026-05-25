import os

def resolve_and_validate_path(working_directory: str, target_path: str, is_directory: bool = False):
    working_dir_abs = os.path.abspath(working_directory)
    resolved_path = os.path.normpath(os.path.join(working_dir_abs, target_path))

    if not os.path.commonpath([working_dir_abs, resolved_path]) == working_dir_abs:
        raise ValueError(f"Error: Cannot access \"{target_path}\" as it is outside the permitted working directory")

    if is_directory and not os.path.isdir(resolved_path):
        raise ValueError(f"Error: \"{target_path}\" is not a directory")
    elif not is_directory and os.path.isdir(resolved_path):
        raise ValueError(f"Error: Cannot operate on \"{target_path}\" as it is a directory")

    return resolved_path
