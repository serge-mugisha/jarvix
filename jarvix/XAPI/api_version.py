import openai
from dotenv import load_dotenv
import os


def process_text_with_gpt(text):
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        raise ValueError("API Key for OpenAI not found.")

    # Initialize the OpenAI client with the API key
    client = openai.Client(api_key=api_key)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system",
             "content": "You are an AI System Called Jarvix. Your Job is to answer every question users ask you. Dont forget your name is Jarvix. If a user asks please tell them your name. You only speak ENGLISH"},
            {"role": "user", "content": text}
        ]
    )
    return completion.choices[0].message.content
