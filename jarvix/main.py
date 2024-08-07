import os

from dotenv import load_dotenv
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

    try:
        while True:
            print("Listening for wake word...")
            if wake_detector.listen_for_wake_word():
                print("Wake word detected! Starting conversation...")

                # Pass in the function you want to process the prompt
                # chatbot.start_conversation(processor=process_text_with_gpt)
                chatbot.start_conversation(processor=ollama_client.process_text_with_ollama)

                print("Conversation ended. Listening for wake word again...")
    except KeyboardInterrupt:
        print("Stopping...")

    # asyncio.get_event_loop().run_until_complete(use_chat_gpt_gui())
