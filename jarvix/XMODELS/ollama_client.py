from pydantic import BaseModel, Field
from typing import List, Dict
import ollama
import subprocess
import time


class OllamaClient(BaseModel):
    model_name: str
    word_limit: int = 100
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    max_tokens: int = 4000

    class Config:
        protected_namespaces = ()
        arbitrary_types_allowed = True

    def process_text_with_ollama(self, text: str) -> str:
        if not self._is_ollama_running():
            print("Ollama is not running. Starting Ollama...")
            self._start_ollama()
            self._wait_for_ollama()

        prompt_with_limit = f"{text}\n\nPlease respond in no more than {self.word_limit} words."
        self.conversation_history.append({"role": "user", "content": prompt_with_limit})
        response = self._send_request_with_history()

        self.conversation_history.append({"role": "assistant", "content": response})
        self._truncate_history_if_needed()

        return response

    def _send_request_with_history(self) -> str:
        response = ollama.chat(model=self.model_name, messages=self.conversation_history)
        return response['message']['content']

    def _truncate_history_if_needed(self) -> None:
        total_tokens = sum(len(entry["content"].split()) for entry in self.conversation_history)
        while total_tokens > self.max_tokens:
            self.conversation_history.pop(0)
            total_tokens = sum(len(entry["content"].split()) for entry in self.conversation_history)

    def _is_ollama_running(self) -> bool:
        try:
            response = ollama.chat(model=self.model_name, messages=[])
            return True
        except:
            return False

    def _start_ollama(self) -> None:
        subprocess.Popen(["ollama", "start"])

    def _wait_for_ollama(self) -> None:
        print("Waiting for Ollama to start...")
        while not self._is_ollama_running():
            time.sleep(1)


# TODO: Delete all audios after using them
# TODO: First prompt passes and the following one fails. Add logs and run in debug mode