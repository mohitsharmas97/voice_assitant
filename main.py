from audio_manager import AudioManager
from openai_client import get_chat_response, text_to_speech
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Check API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env file.")
        return

    # Initialize Audio Manager
    audio = AudioManager()
    
    print("\n--- Voice Assistant Started ---")
    print("Say 'Quit' or 'Exit' to stop.")
    
    while True:
        # 1. Listen
        user_text = audio.listen_and_transcribe(api_key)
        
        if user_text:
            print(f"User: {user_text}")
            
            # Check for exit command
            if any(word in user_text.lower() for word in ["quit", "exit", "stop"]):
                print("Goodbye!")
                break

            # 2. Think
            ai_response = get_chat_response(user_text)
            print(f"AI: {ai_response}")

            # 3. Speak
            audio_file = text_to_speech(ai_response)
            audio.play_audio(audio_file)
            
            # Cleanup temp file
            if os.path.exists(audio_file):
                os.remove(audio_file)

if __name__ == "__main__":
    main()
