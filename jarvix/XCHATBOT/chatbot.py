import logging
import os
import time
from collections import deque
from typing import ClassVar

from pathlib import Path
import soundfile as sf
import sounddevice as sd
from pydantic import BaseModel
from faster_whisper import WhisperModel
import numpy as np

from UTILS.printer import debug_print
from XCHATBOT.tts import NaturalTTS

if os.getenv('LOGGING', 'false').lower() == 'true':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    logger = logging.getLogger(__name__)


class Chatbot(BaseModel):
    filename: str = 'user_input.wav'
    tts_model: str = "tts-1"
    tts_voice: str = "nova"
    silence_duration: float = 1.3 # 3 seconds for natural pauses
    gpt_whisper_model: str = "whisper-1"
    faster_whisper_model: ClassVar[WhisperModel] = WhisperModel("large-v3", device="cpu", compute_type="int8")
    tts: ClassVar[NaturalTTS] = NaturalTTS()

    class Config:
        arbitrary_types_allowed = True

    def speech_to_text(self, file: Path) -> str:
        segments, _ = self.faster_whisper_model.transcribe(str(file))
        transcription = ''.join(segment.text for segment in segments)
        return transcription

    def record_audio(self) -> Path:
        speech_file_path = Path(__file__).parent / self.filename
        chunk_duration = 0.1  # seconds per chunk
        sample_rate = 44100
        chunk_samples = int(sample_rate * chunk_duration)

        # Updated parameters for natural conversation
        silence_threshold = 0.02  # Slightly lower threshold
        min_duration = 1.0
        max_duration = 30
        smoothing_window = 10  # Number of chunks to average

        frames = []
        silence_counter = 0
        has_detected_sound = False
        recent_amplitudes = deque(maxlen=smoothing_window)  # For amplitude smoothing

        print("Recording... (Speak now)")

        start_time = time.time()

        with sd.InputStream(samplerate=sample_rate, channels=1,
                            dtype='float32', blocksize=chunk_samples) as stream:
            while True:
                audio_chunk, _ = stream.read(chunk_samples)
                frames.append(audio_chunk)

                # Calculate smoothed amplitude
                current_amplitude = np.max(np.abs(audio_chunk))
                recent_amplitudes.append(current_amplitude)
                avg_amplitude = np.mean(recent_amplitudes)

                recording_duration = time.time() - start_time

                # Check if we've detected sound using smoothed amplitude
                if avg_amplitude > silence_threshold:
                    has_detected_sound = True
                    silence_counter = 0
                else:
                    if has_detected_sound:  # Only count silence after we've detected sound
                        silence_counter += chunk_duration

                # Visual level meter and status
                level_bars = '=' * int(avg_amplitude * 100)
                status = f"Level: {level_bars:15}| Amplitude: {avg_amplitude:.4f}, Silence: {silence_counter:.1f}s"
                print(status, end='\r')

                # Stop conditions
                if recording_duration >= max_duration:
                    debug_print("\nMaximum duration reached")
                    break

                if has_detected_sound and recording_duration >= min_duration:
                    if silence_counter >= self.silence_duration:
                        print("\nLong silence detected - ending recording")
                        break

        debug_print("\nRecording stopped, saving file...")
        audio = np.concatenate(frames)
        sf.write(speech_file_path, audio, sample_rate)
        debug_print(f"File saved as {speech_file_path}")

        return speech_file_path

    def start_conversation(self, processor: callable, test_text: str = None) -> None:
            text = test_text
            input_audio_path = None
            if not test_text:
                input_audio_path = self.record_audio()
                text = self.speech_to_text(input_audio_path)
            response = processor(text)
            self.tts.speak(response)

            if input_audio_path:
                input_audio_path.unlink()
