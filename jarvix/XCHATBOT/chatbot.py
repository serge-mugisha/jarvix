from openai import Client
from pathlib import Path
import sounddevice as sd
import soundfile as sf
from playsound import playsound
from pydantic import BaseModel, Field, PrivateAttr


class Chatbot(BaseModel):
    api_key: str = Field(..., env='OPENAI_API_KEY')
    _client: Client = PrivateAttr()
    duration: int = 5
    fs: int = 44100
    filename: str = 'user_input.wav'
    tts_model: str = "tts-1"
    tts_voice: str = "nova"
    whisper_model: str = "whisper-1"

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self._client = Client(api_key=self.api_key)

    def speech_to_text(self, file: Path) -> str:
        with open(file, "rb") as audio_file:
            transcription = self._client.audio.transcriptions.create(
                model=self.whisper_model,
                file=audio_file
            )
        return transcription.text

    def text_to_speech(self, text: str) -> Path:
        speech_file_path = Path(__file__).parent / "completion_response.mp3"
        response = self._client.audio.speech.create(
            model=self.tts_model,
            voice=self.tts_voice,
            input=text
        )
        response.stream_to_file(speech_file_path)
        return speech_file_path

    def record_audio(self) -> Path:
        speech_file_path = Path(__file__).parent / self.filename
        print("Recording...")
        audio = sd.rec(int(self.duration * self.fs), samplerate=self.fs, channels=1, dtype='float32')
        sd.wait()
        print("Recording stopped, saving file...")
        sf.write(speech_file_path, audio, self.fs)
        print(f"File saved as {speech_file_path}")
        return speech_file_path

    def start_conversation(self, processor: callable, test_text: str = None) -> None:
        text = test_text
        input_audio_path = None
        if not test_text:
            input_audio_path = self.record_audio()
            text = self.speech_to_text(input_audio_path)
        response = processor(text)
        output_audio_path = self.text_to_speech(response)
        playsound(str(output_audio_path)) # convert PosixPath to str because playsound 1.2.2 on mac doesn't take PosixPath

        output_audio_path.unlink()
        if input_audio_path:
            input_audio_path.unlink()
