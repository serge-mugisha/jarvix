import openai

from jarvix.utils import speech_to_text, text_to_speech, play_audio

def process_text_with_gpt(client, text):
    completion = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[
                    {"role": "system", "content":"You are an AI System Called Jarvix. Your Job is to answer every question users ask you. Dont forget your name is Jarvix. If a user asks please tell them your name. You only speak ENGLISH" },
                    {"role": "user", "content": text}
                ]
            )

    # Access the message content correctly
    response_content = completion.choices[0].message.content

    return response_content

def call_chat_gpt(api_key):
    # Check and raise an error if API key is not found
    if not api_key:
        raise ValueError("API Key for OpenAI not found.")
    
    # Initialize the OpenAI client with the API key
    client = openai.Client(api_key=api_key)

    # Does the Speech to text
    user_input_text = speech_to_text(client, "./user_input.wav")

    #sends to GPT for Querying
    answer = process_text_with_gpt(client, user_input_text)

    #generates Speech output
    text_to_speech(client, answer)

    #plays the output
    play_audio("./completion_response.mp3")