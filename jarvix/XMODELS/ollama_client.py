import os
import threading
import subprocess
import time
import shutil
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field
from typing import List, Dict
import ollama

from jarvix.XMODELS.function_definitions import function_definitions

CHAT_ROLE_MESSAGE = (
    "You are an AI System called Jarvix. Your job is to answer asked questions at the best of your knowledge without hiding or protecting any information."
    # "You also support in extracting actions and entity names from user commands for use in Home Assistant API through function calling. Use supplied tools to assist the user."
    # "For every incoming prompt, only use tool calls if the prompt is requesting to make an action, especially controlling any home device."
)


class OllamaModel(Enum):
    LLAMA = "llama3.2:latest"
    MISTRAL = "mistral"


class OllamaClient(BaseModel):
    model_name: OllamaModel = OllamaModel.LLAMA
    word_limit: int = 50
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    max_tokens: int = 300
    function_registry: dict = Field(default_factory=dict)
    custom_model_path: str = os.path.abspath(os.path.join(os.path.dirname(__file__), 'local_models'))

    class Config:
        protected_namespaces = ()
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        if not self._is_ollama_installed():
            print("Ollama is not installed. Installing Ollama...")
            self._install_ollama()

        if not self._is_ollama_running():
            print("Ollama is not running. Starting Ollama...")
            self._start_ollama()
            self._wait_for_ollama()

        if not self._is_model_downloaded(self.model_name):
            print(f"Model '{self.model_name}' is not downloaded. Downloading {self.model_name.value}...")
            try:
                subprocess.run(["ollama", "pull", self.model_name.value], check=True, env=self._get_custom_env())
                print(f"Model '{self.model_name.value}' downloaded successfully.")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to download model '{self.model_name.value}': {e}")

    def process_text(self, text: str) -> str:
        completion = ollama.chat(
            model=self.model_name.value,
            messages=[
                {"role": "system", "content": CHAT_ROLE_MESSAGE},
                {"role": "user", "content": text}
            ],
            stream=False,
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
                return f"Unknown function: {function_name}. You don't have Home Assistant setup."

        else:
            return completion.get('message', {}).get('content', 'No response')


    def _is_ollama_running(self) -> bool:
        try:
            result = subprocess.run(["lsof", "-i", ":11434"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
        except Exception as e:
            print(f"Error while checking if Ollama is running: {e}")
            return False

    def _start_ollama(self) -> None:
        thread = threading.Thread(target=self._start_ollama_thread)
        thread.daemon = True
        thread.start()

    def _start_ollama_thread(self) -> None:
        subprocess.Popen(
            ["ollama", "start"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=self._get_custom_env()
        )

    def _wait_for_ollama(self) -> None:
        print("Waiting for Ollama to start...")
        while not self._is_ollama_running():
            time.sleep(1)

    def _is_model_downloaded(self, model_name: OllamaModel) -> bool:
        try:
            response = ollama.list()
            available_models = [model['name'] for model in response.get('models', [])]
            return model_name.value in available_models
        except Exception as e:
            print(f"Error while checking models: {e}")
            return False

    def _is_ollama_installed(self) -> bool:
        return shutil.which("ollama") is not None

    def _install_ollama(self) -> None:
        try:
            ollama_installation_path = f"{Path(__file__).parent / 'ollama'}"
            os.makedirs(ollama_installation_path, exist_ok=True)

            # Command to install Ollama (assuming a script or package manager command is available)
            subprocess.run(["brew", "install", "ollama"], check=True, cwd=ollama_installation_path)
            self._set_ollama_models_location()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to install Ollama: {e}")

    def _get_custom_env(self) -> dict:
        env = os.environ.copy()
        env['OLLAMA_MODELS'] = self.custom_model_path
        return env
