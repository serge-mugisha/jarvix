import os
from dotenv import load_dotenv
import pvporcupine
import sounddevice as sd
import numpy as np

# Load environment variables from .env file
load_dotenv()

# Get the access key and keyword file paths from the loaded environment variables
access_key = os.getenv('PORCUPINE_ACCESS_KEY')
keyword_paths = os.getenv('PORCUPINE_KEYWORD_PATHS')

# Check if the access key and keyword paths are available
if not access_key:
    raise ValueError("Porcupine access key not found in .env file. Please set the PORCUPINE_ACCESS_KEY variable.")
if not keyword_paths:
    raise ValueError("Keyword file paths not found in .env file. Please set the PORCUPINE_KEYWORD_PATHS variable.")

# Convert the comma-separated string of paths to a list
keyword_paths = keyword_paths.split(',')

# Create Porcupine instance with custom keywords
porcupine = pvporcupine.create(
    access_key=access_key,
    keyword_paths=keyword_paths
)

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_frame = np.frombuffer(indata, dtype=np.int16)
    keyword_index = porcupine.process(audio_frame)
    if keyword_index >= 0:
        print(f"Detected keyword Hey Jarvix")

try:
    with sd.InputStream(samplerate=porcupine.sample_rate, blocksize=porcupine.frame_length,
                        channels=1, dtype='int16', callback=audio_callback):
        print(f"Listening for custom wake words... Press Ctrl+C to exit.")
        print(f"Loaded keywords: {', '.join(keyword_paths)}")
        while True:
            sd.sleep(100)
except KeyboardInterrupt:
    print("Stopping...")
finally:
    porcupine.delete()
