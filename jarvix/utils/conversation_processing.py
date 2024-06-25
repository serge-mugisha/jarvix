from pathlib import Path
import pygame
import sounddevice as sd
import soundfile as sf

def speech_to_text(client, file):
    audio_file= open(file, "rb")
    transcription = client.audio.transcriptions.create(
      model="whisper-1",
      file=audio_file
    )
    return transcription.text

def text_to_speech(client, text):
    speech_file_path = Path(__file__).parent / "../../completion_response.mp3"
    print("Saving response audio at", speech_file_path)
    response = client.audio.speech.create(
      model="tts-1",
      voice="nova",
      input= text
    )

    response.stream_to_file(speech_file_path)


def record_audio(duration=10, fs=44100, filename='user_input.wav'):
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