from google.genai import types
from call_function import available_functions, call_function
from prompts import system_prompt

def generate_content(client, messages, verbose):
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
            temperature=0,
        ),
    )

    
    if not response.usage_metadata:
         raise RuntimeError("No tokens tracked")
    if verbose:
         print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
         print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    for candidate in response.candidates:
          messages.append(candidate.content)
    if response.function_calls:
          function_responses = []
          for function_call in response.function_calls:
               result = call_function(function_call, verbose)
               if (not result.parts 
               or result.parts[0].function_response is None 
               or result.parts[0].function_response.response is None):
                    raise Exception("Functions not called or failed")
               if verbose:
                    print(f"-> {result.parts[0].function_response.response}")
               function_responses.append(result.parts[0])
          messages.append(types.Content(role="user", parts=function_responses))
          return None
    else:
          return response.text
             
            