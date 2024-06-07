import openai
import whisper
from TTS.api import TTS
import speech_recognition as sr
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize the recognizer and TTS engine
recognizer = sr.Recognizer()
whisper_model = whisper.load_model("base")
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)

# Set your OpenAI API key
openai.api_key = os.getenv('API_KEY')

def recognize_speech():
    with sr.Microphone() as source:
        print("Say something!")
        audio = recognizer.listen(source)

    try:
        audio_data = audio.get_wav_data()
        result = whisper_model.transcribe(audio_data)
        text = result['text']
        print("You said: " + text)
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        return None

def get_response_from_gpt(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

def speak(text):
    tts.tts_to_file(text=text, file_path="output.wav")
    os.system("aplay output.wav")

def main():
    while True:
        prompt = recognize_speech()
        if prompt:
            response = get_response_from_gpt(prompt)
            print("ChatGPT: " + response)
            speak(response)

if __name__ == "__main__":
    main()
