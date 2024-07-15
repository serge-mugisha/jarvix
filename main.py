import openai
import os
from dotenv import load_dotenv
from pathlib import Path
import pygame
import sounddevice as sd
import soundfile as sf


# Load environment variables from .env file
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Check and raise an error if API key is not found
if not api_key:
    raise ValueError("API Key for OpenAI not found.")

# Initialize the OpenAI client with the API key
client = openai.Client(api_key=api_key)

def speech_to_text(file):
    audio_file= open(file, "rb")
    transcription = client.audio.transcriptions.create(
      model="whisper-1",
      file=audio_file
    )
    return transcription.text



def process_text_with_gpt(text):
    completion = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[
                    {"role": "system", "content":"You are an AI System Called Jarvix. Your Job is to answer every question users ask you. Dont forget your name is Jarvix. If a user asks please tell them your name. You only speak ENGLISH" },
                    {"role": "user", "content": text}
                ]
            )

            # Access the message content correctly
    response_content = completion.choices[0].message.content

    return response_content

def text_to_speech(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
      model="tts-1",
      voice="nova",
      input= text
    )

    response.stream_to_file(speech_file_path)



def record_audio(duration=10, fs=44100, filename='output.wav'):
    """
    Record audio from the microphone and save it to a file.
    Args:
    duration (int): Recording duration in seconds.
    fs (int): Sampling frequency in Hz.
    filename (str): Filename to save the recording.
    """
    print("Recording...")
    # Change 'channels=2' to 'channels=1' for mono recording
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()  # Wait until recording is finished
    print("Recording stopped, saving file...")
    sf.write(filename, audio, fs)
    print(f"File saved as {filename}")

def play_audio(audio_file_path):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


# Main workflow
if __name__ == "__main__":

    # Use relative paths
    current_dir = Path(__file__).parent
    input_audio_path = current_dir / "output.wav"
    output_audio_path = current_dir / "speech.mp3"

    duration = int(input("Enter the recording duration in seconds: "))
    audio = record_audio(duration)

    # Does the Speech to text
    output = speech_to_text(input_audio_path)

    #sends to GPT for Querying
    answer = process_text_with_gpt(output)

    #generates Speech output
    text_to_speech(answer)

    #Plays the output
    play_audio(output_audio_path)
