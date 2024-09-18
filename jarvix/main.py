import os
from dotenv import load_dotenv
from jarvix.XAPI.api_version import ApiClient
from jarvix.XCHATBOT.wake import WakeWordDetector
from jarvix.XCHATBOT.chatbot import Chatbot
from jarvix.XMODELS.ollama_client import OllamaClient

load_dotenv()


def select_model():
    while True:
        model = input("Select a model number: \n 1.GPT \n 2.Claude \n 3.Ollama \n")
        if model == "1":
            gpt_api_key = os.getenv('OPENAI_API_KEY')
            api_client = ApiClient(gpt_api_key=gpt_api_key)
            return api_client.process_text_with_gpt
        elif model == "2":
            api_client = ApiClient(claude_api_key=claude_api_key)
            return api_client.process_text_with_claude
        elif model == "3":
            ollama_client = OllamaClient(model_name="phi3:mini")
            return ollama_client.process_text_with_ollama
        else:
            print("Invalid choice. Defaulting to GPT")
            gpt_api_key = os.getenv('OPENAI_API_KEY')
            api_client = ApiClient(gpt_api_key=gpt_api_key)
            return api_client.process_text_with_gpt


if __name__ == "__main__":
    gpt_api_key = os.getenv('OPENAI_API_KEY')
    claude_api_key = os.getenv('ANTHROPIC_API_KEY')

    wake_detector = WakeWordDetector()
    chatbot = Chatbot(api_key=gpt_api_key)  # We'll override this with the selected model's API key
    # ollama_client = OllamaClient(model_name="jarvix-mini:latest")
    # api_client = ApiClient(gpt_api_key=gpt_api_key, claude_api_key=claude_api_key)

    # Ask for model selection before entering the main loop
    selected_model = select_model()
    selected_mode = input("Select running mode: \n 1.Live \n 2.Test \n")

    try:
        loop = True
        while loop:
            if selected_mode == "1":
                print("Listening for wake word...")
                if wake_detector.listen_for_wake_word():
                    print("Wake word detected! Starting conversation...")
                    chatbot.start_conversation(processor=selected_model)
                    print("Conversation ended. Listening for wake word again...")
            else:
                print("Running in test mode...")
                chatbot.start_conversation(processor=selected_model, test_text="What is 7 * 4 - 3")
                loop = False
                print("Test Conversation ended.")

    except KeyboardInterrupt:
        print("Stopping...")
