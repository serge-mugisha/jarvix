import os
from dotenv import load_dotenv
from jarvix.XMODELS.api_version import ApiClient, ModelType
from jarvix.XAUTO.home_assistant import HAClient
from jarvix.XCHATBOT.wake import WakeWordDetector
from jarvix.XCHATBOT.chatbot import Chatbot
from jarvix.XMODELS.ollama_client import OllamaClient

load_dotenv()

if __name__ == "__main__":
    gpt_api_key = os.getenv('OPENAI_API_KEY')
    home_assistant_api_key = os.getenv('HOME_ASSISTANT_API_KEY')
    home_assistant_base_url = os.getenv('HOME_ASSISTANT_BASE_URL')
    selected_model = ModelType(os.getenv('SELECTED_MODEL'))

    wake_detector = WakeWordDetector()
    chatbot = Chatbot(api_key=gpt_api_key)  # We'll override this with the selected model's API key
    ha_client = HAClient(base_url=home_assistant_base_url, api_key=home_assistant_api_key)

    function_registry = {
        "control_home_device": ha_client.control_home_device,
    }

    api_client = None
    if selected_model == ModelType.GPT:
        gpt_api_key = os.getenv('OPENAI_API_KEY')
        api_client = ApiClient(gpt_api_key=gpt_api_key, function_registry=function_registry)
    elif selected_model == ModelType.CLAUDE:
        claude_api_key = os.getenv('ANTHROPIC_API_KEY')
        api_client = ApiClient(claude_api_key=claude_api_key)
    elif selected_model == ModelType.OLLAMA:
        api_client = OllamaClient(model_name="llama3.2", function_registry=function_registry)
    else:
        print("Invalid model loaded from environment. Defaulting to GPT")
        gpt_api_key = os.getenv('OPENAI_API_KEY')
        api_client = ApiClient(gpt_api_key=gpt_api_key)

    selected_mode = input("Select running mode: \n 1.Live \n 2.Test \n")

    try:
        loop = True
        while loop:
            if selected_mode == "1":
                print("Listening for wake word...")
                if wake_detector.listen_for_wake_word():
                    print("Wake word detected! Starting conversation...")
                    chatbot.start_conversation(processor=api_client.process_text)
                    # chatbot.start_conversation(processor=api_client.process_text, test_text="Turn off the test plug")
                    print("Conversation ended. Listening for wake word again...")
            else:
                print("Running in test mode...")

                # user_input = "What is 4 x 7?"
                user_input = "Can you turn off the test plug?"
                chatbot.start_conversation(processor=api_client.process_text, test_text=user_input)

                # success = ha_client.perform_action("switch.test_plug", Action.TURN_ON)
                loop = False
                print("Test Conversation ended.")

    except KeyboardInterrupt:
        print("Stopping...")
