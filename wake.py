import os
import pvporcupine
import sounddevice as sd
import numpy as np


class WakeWordDetector:
    def __init__(self):
        self.access_key = os.getenv('PORCUPINE_ACCESS_KEY')

        # Get keyword paths from a directory in the root folder
        root_folder = os.path.dirname(os.path.abspath(__file__))
        keyword_dir = os.path.join(root_folder, '')
        self.keyword_paths = [os.path.join(keyword_dir, f) for f in os.listdir(keyword_dir) if f.endswith('.ppn')]

        if not self.keyword_paths:
            raise ValueError("No .ppn files found in the keyword_files directory.")


        if not self.access_key or not self.keyword_paths:
            raise ValueError("Porcupine access key or keyword paths not found.")

        self.porcupine = pvporcupine.create(
            access_key=self.access_key,
            keyword_paths=self.keyword_paths
        )
        self.wake_word_detected = False

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        audio_frame = np.frombuffer(indata, dtype=np.int16)
        keyword_index = self.porcupine.process(audio_frame)
        if keyword_index >= 0:
            print("Wake word detected!")
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
