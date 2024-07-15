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

    def process_text_with_gpt(self, text):
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are an AI System Called Jarvix. Your Job is to answer every question users ask you. Don't forget your name is Jarvix. If a user asks please tell them your name. You only speak ENGLISH"},
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message.content

    def text_to_speech(self, text):
        speech_file_path = Path(__file__).parent / "speech.mp3"
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        response.stream_to_file(speech_file_path)
        return speech_file_path

    def record_audio(self, duration=5, fs=44100, filename='output.wav'):
        print("Recording...")
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()
        print("Recording stopped, saving file...")
        sf.write(filename, audio, fs)
        print(f"File saved as {filename}")
        return filename

    def play_audio(self, audio_file_path):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def start_conversation(self):
        input_audio_path = self.record_audio()
        text = self.speech_to_text(input_audio_path)
        response = self.process_text_with_gpt(text)
        output_audio_path = self.text_to_speech(response)
        self.play_audio(output_audio_path)
