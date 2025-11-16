# Your functions (Calendar, Notes, Timers)
import datetime
import json

# --- Actual Python Functions ---

def get_current_time():
    """Returns the current time."""
    return datetime.datetime.now().strftime("%I:%M %p")

def save_note(note_content):
    """Saves a note to a local file."""
    try:
        with open("notes.txt", "a") as f:
            f.write(f"[{datetime.datetime.now()}] {note_content}\n")
        return "Note saved successfully."
    except Exception as e:
        return f"Failed to save note: {e}"

# --- OpenAI Tools Schema ---
# This tells the AI that these functions exist and how to use them.

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_note",
            "description": "Save a text note to a local file",
            "parameters": {
                "type": "object",
                "properties": {
                    "note_content": {"type": "string", "description": "The content of the note"}
                },
                "required": ["note_content"]
            }
        }
    }
]