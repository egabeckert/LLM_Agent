import litellm
from prompts import system_prompt
from functions.get_files_info import schema_get_files_info
from functions.write_file import schema_write_file
from functions.run_python_file import schema_run_python_file
from functions.get_file_content import schema_get_file_content
from functions.create_directory import schema_create_directory
from functions.remove_directory import schema_remove_directory
from functions.remove_file import schema_remove_file
from functions.move_file import schema_move_file

def generate_content(messages, verbose):
    # Add the system prompt to the beginning of the messages list
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    tools = [
        {"type": "function", "function": schema_get_files_info},
        {"type": "function", "function": schema_write_file},
        {"type": "function", "function": schema_run_python_file},
        {"type": "function", "function": schema_get_file_content},
        {"type": "function", "function": schema_create_directory},
        {"type": "function", "function": schema_remove_directory},
        {"type": "function", "function": schema_remove_file},
        {"type": "function", "function": schema_move_file},
    ]

    response = litellm.completion(
        model='gemini/gemini-2.5-flash', # Specify 'gemini/' prefix for LiteLLM
        messages=full_messages,
        temperature=0,
        tools=tools,
        tool_choice="auto",
    )

    message = response.choices[0].message
    messages.append(message)

    if message.tool_calls:
        return message.tool_calls
    else:
        return message.content
