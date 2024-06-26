import os
import asyncio
from dotenv import load_dotenv

from jarvix.XAPI import call_chat_gpt
from jarvix.XGUI import use_chat_gpt_gui
from jarvix.utils import record_audio


# Load environment variables from .env file
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Main workflow
if __name__ == "__main__":
    duration = int(input("Enter the recording duration in seconds: "))
    audio = record_audio(duration)

    # call_chat_gpt(api_key)
    asyncio.get_event_loop().run_until_complete(use_chat_gpt_gui())
   
