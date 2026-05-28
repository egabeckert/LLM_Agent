import litellm
from agent.prompts import system_prompt
from agent.functions.get_files_info import schema_get_files_info
from agent.functions.write_file import schema_write_file
from agent.functions.run_python_file import schema_run_python_file
from agent.functions.get_file_content import schema_get_file_content
from agent.functions.create_directory import schema_create_directory
from agent.functions.remove_directory import schema_remove_directory
from agent.functions.remove_file import schema_remove_file
from agent.functions.move_file import schema_move_file

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
    return message

