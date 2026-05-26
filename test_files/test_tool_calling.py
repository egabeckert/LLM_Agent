from generate_content import generate_content
from call_function import call_function
import json

def main():
    messages = [
        {"role": "user", "content": "List the files in the current directory and then tell me what generate_content.py does."}
    ]
    
    # First call to generate_content, expecting a tool call
    response = generate_content(messages, verbose=True)
    
    if isinstance(response, list) and response and hasattr(response[0], 'function'):
        print("Received tool call(s).")
        for tool_call in response:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"Tool call: {function_name} with args {function_args}")
            tool_output = call_function(function_name, function_args, verbose=True)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(tool_output),
                }
            )
        
        # Second call to generate_content with tool output(s)
        final_response = generate_content(messages, verbose=True)
        
        if isinstance(final_response, list) and final_response and hasattr(final_response[0], 'function'):
            print("Received another tool call(s).")
            for tool_call in final_response:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"Tool call: {function_name} with args {function_args}")
                tool_output = call_function(function_name, function_args, verbose=True)
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(tool_output),
                    }
                )
            # Third call to generate_content with all tool outputs
            final_response = generate_content(messages, verbose=True)
            print(f"Final Response: {final_response}")
        else:
            print(f"Final Response: {final_response}")
    else:
        print(f"Unexpected response: {response}")

if __name__ == "__main__":
    main()
