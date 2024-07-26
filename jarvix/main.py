from jarvix.XAPI import process_text_with_gpt
from jarvix.XCHATBOT.chatbot import Chatbot
from jarvix.XCHATBOT.wake import WakeWordDetector
from dotenv import load_dotenv

# from jarvix.XGUI import use_chat_gpt_gui
# from jarvix.utils import record_audio

load_dotenv()

# Main workflow
if __name__ == "__main__":
    wake_detector = WakeWordDetector()
    chatbot = Chatbot()

    try:
        while True:
            print("Listening for wake word...")
            if wake_detector.listen_for_wake_word():
                print("Wake word detected! Starting conversation...")
                # Pass in the function you want to process the prompt
                chatbot.start_conversation(processor=process_text_with_gpt)
                print("Conversation ended. Listening for wake word again...")
    except KeyboardInterrupt:
        print("Stopping...")

    # asyncio.get_event_loop().run_until_complete(use_chat_gpt_gui())
