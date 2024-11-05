from pydantic import BaseModel, Field
from typing import List, Dict
import ollama
import subprocess
import time

from jarvix.XMODELS.function_definitions import function_definitions


class OllamaClient(BaseModel):
    model_name: str
    word_limit: int = 50
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    max_tokens: int = 300
    function_registry: dict = Field(default_factory=dict)

    class Config:
        protected_namespaces = ()
        arbitrary_types_allowed = True

    def process_text(self, text: str) -> str:
        if not self._is_ollama_running():
            print("Ollama is not running. Starting Ollama...")
            self._start_ollama()
            self._wait_for_ollama()

        # prompt_with_limit = f"{text}.\nPlease respond with direct answers and no more than {self.word_limit} words."
        self.conversation_history.append({"role": "user", "content": text})
        response = self._send_request_with_history()

        self.conversation_history.append({"role": "assistant", "content": response})
        self._truncate_history_if_needed()

        return response

    def _send_request_with_history(self) -> str:
        completion = ollama.chat(
            model=self.model_name,
            messages=self.conversation_history,
            tools=function_definitions
        )
        message = completion.get('message', {})
        tool_calls = message.get('tool_calls', [])

        if tool_calls:
            tool_call_function = tool_calls[0].get('function', {})
            function_name = tool_call_function.get('name')
            function_args = tool_call_function.get('arguments', {})

            # Check if function is registered
            if function_name and function_name in self.function_registry:
                function_to_call = self.function_registry[function_name]
                # Call the function dynamically with arguments unpacked
                return function_to_call(**function_args)
            else:
                return f"Unknown function: {function_name}"

        else:
            return completion.get('message', {}).get('content', 'No response')

    def _truncate_history_if_needed(self) -> None:
        total_tokens = sum(len(entry["content"].split()) for entry in self.conversation_history)
        while total_tokens > self.max_tokens:
            self.conversation_history.pop(0)
            total_tokens = sum(len(entry["content"].split()) for entry in self.conversation_history)

    def _is_ollama_running(self) -> bool:
        try:
            ollama.chat(model=self.model_name, messages=[])
            return True
        except:
            return False

    def _start_ollama(self) -> None:
        subprocess.Popen(["ollama", "start"])

    def _wait_for_ollama(self) -> None:
        print("Waiting for Ollama to start...")
        while not self._is_ollama_running():
            time.sleep(1)
