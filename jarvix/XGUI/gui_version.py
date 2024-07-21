import os
import time
import openai

from pyppeteer import launch
from dotenv import load_dotenv
from jarvix.utils import speech_to_text, text_to_speech, play_audio

# Load environment variables
load_dotenv()
EMAIL = os.getenv('CHATGPT_EMAIL')
PASSWORD = os.getenv('CHATGPT_PASSWORD')
api_key = os.getenv('OPENAI_API_KEY')


class ChatGPTClient:
    def __init__(self, email, password, use_voice=False):
        self.email = email
        self.password = password
        self.use_voice = use_voice
        self.browser = None
        self.page = None
        self.chat_id = None
        self.start_time = None
        self.chromium_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'browser', 'chrome')

    async def sign_in(self):
        self.browser = await launch(headless=False, executablePath=self.chromium_path)
        self.page = await self.browser.newPage()
        await self.page.goto('https://chatgpt.com/')

        # Fill email and password fields and log in
        # await self.page.click('button[data-testid="login-button"]')
        # await self.page.waitForSelector('input[name="email"]', timeout=60000)
        #
        # await self.page.type('input[name="email"]', self.email)
        # await self.page.click('[class="continue-btn"]')
        # await self.page.waitForSelector('input[name="password"]', timeout=60000)
        # await self.page.type('input[name="password"]', self.password)
        # await self.page.click('button[type="submit"]')

        # Wait for login to complete
        # await self.page.waitForNavigation()
        await self.page.waitForSelector('textarea[id="prompt-textarea"]', timeout=60000)
        # self.start_time = time.time()

    async def send_message(self, text):
        # if time.time() - self.start_time > 3600:
        #     await self.reset_chat()

        # Type message
        await self.page.type('textarea[id="prompt-textarea"]', text)
        await self.page.keyboard.press('Enter')

        # Wait for response
        await self.page.waitForSelector('button[data-testid="fruitjuice-send-button"]', timeout=60000)
        response_element = await self.page.querySelector('div[data-message-author-role="assistant"]:last-child')

        if self.use_voice:
            await self.page.click('button[aria-label="Read aloud"]')
            await self.page.waitForSelector('button[aria-label="Stop"]', hidden=True)
            return True
        else:
            response_text = await self.page.evaluate('(element) => element.textContent', response_element)
            return response_text

    async def reset_chat(self):
        # Delete the current chat and start a new one
        await self.page.click('button[aria-label="Delete conversation"]')
        await self.page.waitForSelector('button[aria-label="Confirm"]')
        await self.page.click('button[aria-label="Confirm"]')
        await self.page.waitForNavigation()
        await self.page.click('button[aria-label="New conversation"]')
        self.start_time = time.time()

    async def close(self):
        await self.browser.close()


async def use_chat_gpt_gui():
    client = ChatGPTClient(email=EMAIL, password=PASSWORD, use_voice=False)
    await client.sign_in()

    # Initialize the OpenAI client with the API key
    api_client = openai.Client(api_key=api_key)

    # Does the Speech to text
    user_input_text = speech_to_text(api_client, "./user_input.wav")

    response = await client.send_message(user_input_text)
    print("Response:", response)
    await client.close()

    #generates Speech output
    text_to_speech(client, response)

    #Plays the output
    play_audio("./completion_response.mp3")

# if __name__ == "__main__":
#     asyncio.get_event_loop().run_until_complete(use_chat_gpt_gui())
