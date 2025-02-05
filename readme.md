## Jarvix ##

### Installation and Running ###
1. Clone the repository
2. Install the required packages
3. Create a .env file in the same directory as the script
4. Add the required environment variables
5. Have Docker installed & navigate to the project root
6. Build a docker container `docker-compose build jarvix-app`
7. Spin the container `docker-compose run jarvix-app`

### Setup ###
Environment Variables:
Create a .env file in the same directory as the script.
Add the following in your .env file:

### Env variables ###
```
PORCUPINE_ACCESS_KEY="YOUR_PORCUPINE_ACCESS_KEY"
PORCUPINE_FILE_NAME=wake_word.ppn
HOME_ASSISTANT_BASE_URL=http://localhost:8123
OLLAMA_HOME=./XMODELS/local_models
DEBUG=True
LOGGING=True
TEST_MODE=True
IS_HA_CONFIGURED='False'
HA_REFRESH_TOKEN='AUTO_GENERATED_HA_REFRESH_TOKEN'
```

### Home Assistant Configuration ###

When you run the script for the first time, it will ask you to configure Home Assistant.
Respond with `yes` to configure Home Assistant, otherwise you will need to restart the script to configure Home Assistant.
After HA is configured:

1. visit http://localhost:8123
2. Finalize the setup
3. Use the HA dashboard to add new devices to control via voice commands
