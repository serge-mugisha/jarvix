import logging
import os
from pathlib import Path

import pvporcupine
import sounddevice as sd
import numpy as np
from UTILS.printer import debug_print

if os.getenv('LOGGING', 'false').lower() == 'true':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    logger = logging.getLogger(__name__)



class WakeWordDetector:
    def __init__(self):
        self.keyword_paths = None
        self.access_key = os.getenv('PORCUPINE_ACCESS_KEY')
        file_path = Path(__file__).parent / os.getenv('PORCUPINE_FILE_NAME')
        keyword_path = [os.path.normpath(str(file_path.resolve()))]
        debug_print(f"loading PPN file at: ${keyword_path}")
        self.keyword_paths = keyword_path

        if not self.keyword_paths:
            debug_print("No .ppn files found in the chatbot directory. Defaulting to 'Bumblebee' as a wake word")
            self.keyword_paths = [pvporcupine.KEYWORD_PATHS['bumblebee']]

        if not self.access_key or not self.keyword_paths:
            raise ValueError("Porcupine access key or keyword paths not found.")

        self.porcupine = pvporcupine.create(
            access_key=self.access_key,
            keyword_paths=self.keyword_paths
        )
        self.wake_word_detected = False

    def audio_callback(self, indata, frames, time, status):
        if status:
            debug_print(status)
        audio_frame = np.frombuffer(indata, dtype=np.int16)
        keyword_index = self.porcupine.process(audio_frame)
        if keyword_index >= 0:
            debug_print("Wake word detected!")
            self.wake_word_detected = True
            raise sd.CallbackStop

    def listen_for_wake_word(self):
        self.wake_word_detected = False
        try:
            with sd.InputStream(samplerate=self.porcupine.sample_rate,
                                blocksize=self.porcupine.frame_length,
                                channels=1, dtype='int16',
                                callback=self.audio_callback):
                print("Listening for wake word... Press Ctrl+C to exit.")
                while not self.wake_word_detected:
                    sd.sleep(100)
        except sd.CallbackStop:
            pass
        return self.wake_word_detected

    def __del__(self):
        if hasattr(self, 'porcupine'):
            self.porcupine.delete()
