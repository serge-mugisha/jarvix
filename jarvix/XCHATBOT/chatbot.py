import os
import openai
from pathlib import Path
import pygame
import sounddevice as sd
import soundfile as sf


class Chatbot:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("API Key for OpenAI not found.")
        self.client = openai.Client(api_key=self.api_key)

    def speech_to_text(self, file):
        with open(file, "rb") as audio_file:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcription.text

    def text_to_speech(self, text):
        speech_file_path = Path(__file__).parent / "completion_response.mp3"
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        response.stream_to_file(speech_file_path)
        return speech_file_path

    def record_audio(self, duration=5, fs=44100, filename='user_input.wav'):
        """
        Record audio from the microphone and save it to a file.
        Args:
        duration (int): Recording duration in seconds.
        fs (int): Sampling frequency in Hz.
        filename (str): Filename to save the recording.
        """
        speech_file_path = Path(__file__).parent / filename
        print("Recording...")
        # Change 'channels=2' to 'channels=1' for mono recording
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()
        print("Recording stopped, saving file...")
        sf.write(speech_file_path, audio, fs)
        print(f"File saved as {speech_file_path}")
        return speech_file_path

    def play_audio(self, audio_file_path):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def start_conversation(self, processor):
        input_audio_path = self.record_audio()
        text = self.speech_to_text(input_audio_path)
        response = processor(text)
        output_audio_path = self.text_to_speech(response)
        self.play_audio(output_audio_path)
