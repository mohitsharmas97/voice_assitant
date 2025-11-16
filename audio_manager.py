# Handles Mic input and Speaker output
import speech_recognition as sr
import os
import platform
import subprocess
from openai import OpenAI

class AudioManager:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Initialize OpenAI Client here as well for transcription
        from dotenv import load_dotenv
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Select the correct microphone (Index 1 based on your logs)
        # If 1 fails, try changing this to 5
        try:
            self.mic = sr.Microphone(device_index=1)
        except:
            print("Microphone index 1 failed, trying default.")
            self.mic = sr.Microphone()

        print("\nCalibrating microphone... (Please be quiet)")
        with self.mic as source:
            # Set a high threshold to avoid picking up background noise
            self.recognizer.energy_threshold = 1000  
            self.recognizer.dynamic_energy_threshold = False 
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Calibration complete.")

    def listen_and_transcribe(self, api_key):
        """
        Records audio, saves to temp file, and sends to OpenAI Whisper.
        """
        try:
            with self.mic as source:
                print("\nListening... (Speak clearly)")
                # Record audio
                audio_data = self.recognizer.listen(source, timeout=3, phrase_time_limit=10)
            
            print("Audio captured. Transcribing...")

            # 1. Save audio to a temporary wav file
            temp_filename = "temp_input.wav"
            with open(temp_filename, "wb") as f:
                f.write(audio_data.get_wav_data())

            # 2. Send that file to OpenAI Whisper
            with open(temp_filename, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            
            text = transcription.text
            
            # 3. Clean up temp file
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            
            # Debug print
            print(f"RAW TRANSCRIPTION: '{text}'") 
            
            if not text or text.strip() == "":
                return None

            return text

        except sr.WaitTimeoutError:
            print("No speech detected (Timeout).")
            return None
        except Exception as e:
            print(f"General Error: {e}") 
            return None

    def play_audio(self, file_path):
        if not os.path.exists(file_path):
            return
        system_name = platform.system()
        try:
            if system_name == "Windows":
                # Using powershell to play is cleaner on Windows than os.startfile
                os.system(f'powershell -c (New-Object Media.SoundPlayer "{file_path}").PlaySync();')
            elif system_name == "Darwin":
                subprocess.run(["afplay", file_path])
            elif system_name == "Linux":
                subprocess.run(["aplay", file_path])
        except Exception as e:
            print(f"Playback Error: {e}")