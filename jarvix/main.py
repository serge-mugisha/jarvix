import os

from dotenv import load_dotenv

from jarvix.XAPI.api_version import ApiClient
from jarvix.XCHATBOT.wake import WakeWordDetector
from jarvix.XCHATBOT.chatbot import Chatbot
from jarvix.XMODELS.ollama_client import OllamaClient

load_dotenv()

# Main workflow
if __name__ == "__main__":
    api_key = os.getenv('OPENAI_API_KEY')

    wake_detector = WakeWordDetector()
    chatbot = Chatbot(api_key=api_key)

    ollama_client = OllamaClient(model_name="phi3:mini")
    api_client = ApiClient(api_key=api_key)

    try:
        while True:
            print("Listening for wake word...")
            if wake_detector.listen_for_wake_word():
                print("Wake word detected! Starting conversation...")

                # Pass in the function you want to process the prompt
                chatbot.start_conversation(processor=api_client.process_text_with_api)  # Use External API
                # chatbot.start_conversation(processor=ollama_client.process_text_with_ollama)  # Use Local LLM

                print("Conversation ended. Listening for wake word again...")
    except KeyboardInterrupt:
        print("Stopping...")
