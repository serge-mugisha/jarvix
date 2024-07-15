from dotenv import load_dotenv
from wake import WakeWordDetector
from chatbot import Chatbot

def main():
    load_dotenv()

    wake_detector = WakeWordDetector()
    chatbot = Chatbot()

    try:
        while True:
            print("Listening for wake word...")
            if wake_detector.listen_for_wake_word():
                print("Wake word detected! Starting conversation...")
                chatbot.start_conversation()
                print("Conversation ended. Listening for wake word again...")
    except KeyboardInterrupt:
        print("Stopping...")

if __name__ == "__main__":
    main()
