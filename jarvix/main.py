import os
from dotenv import load_dotenv
from jarvix.XAPI.api_version import ApiClient
from jarvix.XCHATBOT.wake import WakeWordDetector
from jarvix.XCHATBOT.chatbot import Chatbot

load_dotenv()

def select_model():
    while True:
        choice = input("Select a model (gpt/claude): ").lower()
        if choice in ["gpt", "claude"]:
            return choice
        print("Invalid choice. Please enter 'gpt' or 'claude'.")

if __name__ == "__main__":
    gpt_api_key = os.getenv('OPENAI_API_KEY')
    claude_api_key = os.getenv('ANTHROPIC_API_KEY')

    wake_detector = WakeWordDetector()
    chatbot = Chatbot(api_key=gpt_api_key)  # We'll override this with the selected model's API key

    api_client = ApiClient(gpt_api_key=gpt_api_key, claude_api_key=claude_api_key)

    # Ask for model selection before entering the main loop
    selected_model = select_model()
    print(f"Using {selected_model.upper()} model for all conversations.")

    try:
        while True:
            print("Listening for wake word...")
            if wake_detector.listen_for_wake_word():
                print("Wake word detected! Starting conversation...")

                chatbot.start_conversation(processor=lambda text: api_client.process_text(text, model=selected_model))

                print("Conversation ended. Listening for wake word again...")
    except KeyboardInterrupt:
        print("Stopping...")
