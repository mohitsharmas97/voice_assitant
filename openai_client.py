# Handles Whisper, GPT, and TTS interactions
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from tools import tools_schema, get_current_time, save_note

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize chat history with a system prompt
conversation_history = [
    {
        "role": "system", 
        "content": "You are a helpful voice assistant. Keep your answers short and conversational (1-2 sentences max)."
    }
]

def get_chat_response(user_input):
    """Sends user input to GPT-4o and handles any function calls."""
    
    # 1. Add user message to history
    conversation_history.append({"role": "user", "content": user_input})
    
    # 2. First API Call
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=conversation_history,
        tools=tools_schema,
        tool_choice="auto"
    )
    
    message = response.choices[0].message

    # 3. Check if AI wants to use a tool (Function Calling)
    if message.tool_calls:
        print(f"Executing tool: {message.tool_calls[0].function.name}...")
        conversation_history.append(message) 
        
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Execute the actual function
            if function_name == "get_current_time":
                function_response = get_current_time()
            elif function_name == "save_note":
                function_response = save_note(function_args.get("note_content"))
            else:
                function_response = "Error: Function not found"
            
            # Feed the result back to the AI
            conversation_history.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })

        # 4. Second API Call (Getting the final spoken answer)
        final_response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation_history
        )
        final_text = final_response.choices[0].message.content
    else:
        final_text = message.content

    # 5. Add AI response to history
    conversation_history.append({"role": "assistant", "content": final_text})
    return final_text

def text_to_speech(text):
    """Converts text to audio using OpenAI TTS."""
    output_file = "response.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova", # Options: alloy, echo, fable, onyx, nova, shimmer
        input=text
    )
    response.stream_to_file(output_file)
    return output_file