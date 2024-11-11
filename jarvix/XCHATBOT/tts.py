from pydantic import BaseModel, Field
import pyttsx3
from typing import Optional

"""
    Usage:
    new_settings = TTSSettings(rate=130)
    tts = NaturalTTS(new_settings)
    tts.speak("New settings applied")
"""
class TTSSettings(BaseModel):
    rate: int = Field(default=150, ge=50, le=300)
    volume: float = Field(default=0.9, ge=0.0, le=1.0)
    voice_id: Optional[str] = None


class NaturalTTS:
    _instance = None
    _engine = None

    def __new__(cls, settings: Optional[TTSSettings] = None):
        # Create singleton instance
        if cls._instance is None:
            cls._instance = super(NaturalTTS, cls).__new__(cls)
            cls._engine = pyttsx3.init()
        return cls._instance

    def __init__(self, settings: Optional[TTSSettings] = None):
        if settings:
            self.settings = settings
            self._setup_engine()
        elif not hasattr(self, 'settings'):
            self.settings = TTSSettings()
            self._setup_engine()

    def _setup_engine(self):
        self._engine.setProperty('rate', self.settings.rate)
        self._engine.setProperty('volume', self.settings.volume)
        if self.settings.voice_id:
            self._engine.setProperty('voice', self.settings.voice_id)

    def speak(self, text: str) -> None:
        self._engine.say(text)
        self._engine.runAndWait()

    def list_voices(self) -> list:
        return [voice.id for voice in self._engine.getProperty('voices')]