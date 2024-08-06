import ollama
import subprocess
import time


class OllamaClient:
    def __init__(self, model_name, word_limit=100):
        self.model_name = model_name
        self.word_limit = word_limit
        self.conversation_history = []
        self.max_tokens = 4000

    def process_text_with_ollama(self, text):
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

    def _send_request_with_history(self):
        response = ollama.chat(model=self.model_name, messages=self.conversation_history)
        return response['message']['content']

    def _truncate_history_if_needed(self):
        total_tokens = sum(len(entry["content"].split()) for entry in self.conversation_history)
        while total_tokens > self.max_tokens:
            self.conversation_history.pop(0)
            total_tokens = sum(len(entry["content"].split()) for entry in self.conversation_history)

    def _is_ollama_running(self):
        try:
            response = ollama.chat(model=self.model_name, messages=[])
            return True
        except:
            return False

    def _start_ollama(self):
        subprocess.Popen(["ollama", "start"])

    def _wait_for_ollama(self):
        print("Waiting for Ollama to start...")
        while not self._is_ollama_running():
            time.sleep(1)


# TODO: Delete all audios after using them
# TODO: First prompt passes and the following one fails. Add logs and run in debug mode