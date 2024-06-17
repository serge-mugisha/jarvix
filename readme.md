## Jarvix ##

### Installation and Running ###

1. Make `run.sh` executable: `chmod +x run.sh`
2. Run the script: `./run.sh`


### Requirements ####
Before you can run this script, make sure you have the following installed:

1.Python 3.8 or higher

2.openai

3.sounddevice

4.soundfile

5.pygame

6.python-dotenv

## Setup ##
Environment Variables:
Create a .env file in the same directory as the script.
Add your OpenAI API key to the .env file:


## How It Works ##
Record Audio: Starts recording from your microphone for a specified duration and saves it as output.wav.

Speech to Text: Converts the recorded speech in output.wav to text using OpenAI's Whisper model.

Process Text with GPT: Sends the transcribed text to GPT for processing, receives a response tailored to the context of an AI system named Jarvix.

Text to Speech: Converts the GPT response text to speech and saves it as speech.mp3.

Play Audio: Plays the speech.mp3 file, letting you hear the AI's response.

## Note ##
Ensure the paths for output.wav and speech.mp3 are correctly set in the script to match your file structure. Modify these paths in the script if your file structure is different from the default.
