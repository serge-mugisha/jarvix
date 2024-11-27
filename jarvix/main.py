import os
import time
import threading
import sys
from dotenv import load_dotenv, set_key
from jarvix.XMODELS.api_version import ApiClient, ModelType
from jarvix.XAUTO.home_assistant import HAClient, HAInitializer, HAConfig
from jarvix.XCHATBOT.wake import WakeWordDetector
from jarvix.XCHATBOT.chatbot import Chatbot
from jarvix.XMODELS.ollama_client import OllamaClient, OllamaModel

load_dotenv()

class InteractiveMenu:
    def __init__(self):
        self.config = None
        self.selected_model = None
        self.gpt_api_key = None
        self.home_assistant_config = None

    def setup_configuration(self):
        print("\n✨ Welcome to Jarvix Setup Wizard! ✨")
        print("Let's get everything configured step-by-step to ensure the best experience. Sit back, relax, and let’s begin our journey!\n")

        # Setting up LLM Model Selection
        print("🚀 First, let's select the Language Model you'll be using:")
        print("1. OpenAI GPT - Requires API Key and works online")
        print("2. Claude by Anthropic - Requires API Key and works online")
        print("3. Ollama Llama - Already set up with Jarvix for offline use, no additional setup required")
        model_choice = input("Enter your choice (1/2/3): ")

        if model_choice == "1":
            self.selected_model = ModelType.GPT
            self.gpt_api_key = input("🔑 Enter your OpenAI API Key: ")
            os.environ['OPENAI_API_KEY'] = self.gpt_api_key
            set_key('.env', 'OPENAI_API_KEY', self.gpt_api_key)
        elif model_choice == "2":
            self.selected_model = ModelType.CLAUDE
            claude_api_key = input("🔑 Enter your Anthropic API Key: ")
            os.environ['ANTHROPIC_API_KEY'] = claude_api_key
            set_key('.env', 'ANTHROPIC_API_KEY', claude_api_key)
        elif model_choice == "3":
            self.selected_model = ModelType.OLLAMA
            print("You have selected Ollama Llama. No additional key is required.")
        else:
            print("⚠️ Invalid choice. Defaulting to Ollama Llama.")
            self.selected_model = ModelType.OLLAMA

        # Checking if Home Assistant has already been configured
        is_ha_configured = os.getenv('IS_HA_CONFIGURED', 'False').lower() == 'true'
        if not is_ha_configured:
            # Asking the user if they want to set up Home Assistant
            setup_ha = input("\n🏠 Jarvix can integrate with Home Assistant to control your smart devices. Would you like to set it up now? (yes/no): ")
            if setup_ha.strip().lower() == "yes":
                print("\n🏠 Great! Let's configure your Home Assistant:")
                print("Please provide the following details to set up your smart home integration.")
                friendly_name = input("🏷️ Friendly Name (e.g., Bob's Home): ")
                username = input("👤 Home Assistant Username: ")
                password = input("🔒 Home Assistant Password: ")
                name = input("🏠 Home Assistant Name: ")
                latitude = float(input("🌍 Latitude: "))
                longitude = float(input("🌍 Longitude: "))
                elevation = int(input("📏 Elevation (in meters): "))
                unit_system = input("📐 Unit System (metric/imperial): ")
                currency = input("💵 Currency (e.g., USD): ")
                country = input("🌎 Country (e.g., US): ")
                time_zone = input("⏰ Time Zone (e.g., America/Los_Angeles): ")
                language = input("🗣️ Language (e.g., en): ")

                self.home_assistant_config = HAConfig(
                    friendly_name=friendly_name,
                    username=username,
                    password=password,
                    name=name,
                    latitude=latitude,
                    longitude=longitude,
                    elevation=elevation,
                    unit_system=unit_system,
                    currency=currency,
                    country=country,
                    time_zone=time_zone,
                    language=language
                )
            else:
                print("\n👍 Skipping Home Assistant setup. You can configure it later if you wish.")

    def run(self):
        print("\n🚦 Please wait while we initialize everything for you...")
        print("⚙️Initializing components ⚙️")
        # Load wake word detector
        wake_detector = WakeWordDetector()
        # Load chatbot (API key will be assigned later)
        chatbot = Chatbot()
        # Initialize Home Assistant if configured
        ha_client = None
        function_registry = {}
        if os.getenv('IS_HA_CONFIGURED', 'False').lower() == 'false':
            if self.home_assistant_config is not None:
                HAInitializer(config=self.home_assistant_config)
                ha_client = HAClient()
                function_registry["control_home_device"] = ha_client.control_home_device
            else:
                print("\n⚠️ Home Assistant is not configured. Skipping initialization.")
        else:
            ha_client = HAClient()
            function_registry["control_home_device"] = ha_client.control_home_device

        # Setup API client based on the selected model
        api_client = None
        if self.selected_model == ModelType.GPT:
            api_client = ApiClient(gpt_api_key=self.gpt_api_key, function_registry=function_registry)
        elif self.selected_model == ModelType.CLAUDE:
            claude_api_key = os.getenv('ANTHROPIC_API_KEY')
            api_client = ApiClient(claude_api_key=claude_api_key)
        elif self.selected_model == ModelType.OLLAMA:
            api_client = OllamaClient(model_name=OllamaModel.LLAMA, function_registry=function_registry)
        else:
            print("⚠️ Invalid model selected. Defaulting to Ollama Llama.")
            api_client = OllamaClient(model_name=OllamaModel.LLAMA, function_registry=function_registry)

        print("\n✨ All systems are ready! Let's begin your journey with Jarvix. ✨\n")

        # Select Running Mode
        print("\nChoose how you want to proceed:")
        selected_mode = input("1. Live Mode - Interact in real-time. \n2. Test Mode - Quick test for functionality.\nEnter your choice (1/2): ")
        try:
            loop = True
            while loop:
                if selected_mode == "1":
                    print("\n🎙️ Listening for your wake word... Say the magic word to start interacting!")
                    if wake_detector.listen_for_wake_word():
                        print("\n💬 Wake word detected! Let's chat...")
                        chatbot.start_conversation(processor=api_client.process_text)
                        print("\n🤖 Conversation ended. Ready to listen for your next command.")
                elif selected_mode == "2":
                    print("\n🛠️ Running in test mode...")
                    # user_input = "What is 3 x 4?"
                    user_input = "Who are you?"
                    # user_input = "Can you switch on the test plug?"
                    chatbot.start_conversation(processor=api_client.process_text, test_text=user_input)
                    loop = False
                    print("\n🧪 Test Conversation ended.")
                else:
                    print("⚠️ Invalid mode selected. Exiting setup.")
                    loop = False
        except KeyboardInterrupt:
            print("\n🛑 Stopping... Goodbye!")

if __name__ == "__main__":
    menu = InteractiveMenu()
    menu.setup_configuration()
    menu.run()
