import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum

import yaml
from pydantic import BaseModel, Field
import requests
from dotenv import load_dotenv, set_key
from datetime import datetime, timedelta
from jarvix.utils.printer import debug_print

# Load environment variables
load_dotenv()

if os.getenv('LOGGING', 'false').lower() == 'true':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    logger = logging.getLogger(__name__)


# Constants for endpoints and actions
ENTITY_ENDPOINT = '/api/states'
SERVICE_ENDPOINT_TEMPLATE = '/api/services/{domain}/{service}'

class Action(Enum):
    TURN_ON = 'turn_on'
    TURN_OFF = 'turn_off'
    TOGGLE = 'toggle'

ACTION_SERVICE_MAP = {
    Action.TURN_ON: 'turn_on',
    Action.TURN_OFF: 'turn_off',
    Action.TOGGLE: 'toggle',
}

class EntityType(str, Enum):
    LIGHT = 'light'
    SWITCH = 'switch'


class Entity(BaseModel):
    entity_id: str
    state: str
    attributes: Dict[str, Any] = Field(default_factory=dict)

class HAFunctionInput(BaseModel):
    action: Action
    entity_name: str
    entity_type: Optional[EntityType] = None

class HAConfig(BaseModel):
    friendly_name: str
    username: str
    password: str
    name: str
    latitude: float
    longitude: float
    elevation: int
    unit_system: str
    currency: str
    country: str
    time_zone: str
    language: str

class HAInitializer:
    def __init__(self, ha_directory: str = Path(__file__).parent / 'homeassistant', config: HAConfig = None):
        self.ha_directory = ha_directory
        self.start_command = f'hass --config {self.ha_directory}'
        self.base_url = f"http://{os.getenv('INTERNAL_URL', 'localhost:8123')}"
        self.headers = {'Content-Type': 'application/json'}
        self.auth_code = os.getenv('HA_AUTH_CODE', None)
        self.config = config
        self._initialize_home_assistant()
        set_key(Path(__file__).parents[2] / '.env', 'IS_HA_CONFIGURED', 'True')

    def _initialize_home_assistant(self):
        """Initialize Home Assistant and configure necessary settings."""
        # Ensure the HA directory exists
        if not os.path.exists(self.ha_directory):
            os.makedirs(self.ha_directory)

        # Start HA to create necessary files
        subprocess.Popen(self.start_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)  # Wait for HA to start (increase if necessary)
        self._create_configuration_file() # Overwrite configuration.yaml with user info

        # Wait until HA is live
        if not self._wait_until_ha_is_live():
            raise TimeoutError("Home Assistant initialization failed.")

        # Run onboarding tasks and create a new user
        self._run_onboarding()

    def _create_configuration_file(self):
        """Create the configuration.yaml file with basic Home Assistant information."""
        config_path = f"{self.ha_directory}/configuration.yaml"
        if self.config:
            config_data = {
                'homeassistant': {
                    'name': self.config.name,
                    'latitude': self.config.latitude,
                    'longitude': self.config.longitude,
                    'elevation': self.config.elevation,
                    'unit_system': self.config.unit_system,
                    'currency': self.config.currency,
                    'country': self.config.country,
                    'time_zone': self.config.time_zone,
                    'external_url': self.base_url,
                }
            }
            with open(config_path, 'w') as config_file:
                yaml.dump(config_data, config_file)
        else:
            raise ValueError("HAConfig object is required to create the configuration.yaml file.")

    def _wait_until_ha_is_live(self, timeout: int = 60) -> bool:
        """Wait until Home Assistant is running and responsive."""
        start_time = time.time()
        while True:
            try:
                response = requests.get(f"{self.base_url}/manifest.json", timeout=2)
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                pass
            if time.time() - start_time > timeout:
                return False
            time.sleep(2)

    def _run_onboarding(self):
        """Run the onboarding steps for Home Assistant, including creating a user."""
        # Check if onboarding is already done
        if os.path.exists(f"{self.ha_directory}/.storage/onboarding"):
            with open(f"{self.ha_directory}/.storage/onboarding") as onboarding_file:
                onboarding_json = json.load(onboarding_file)
                onboarding_data = onboarding_json.get("data", "")
                if onboarding_data:
                    self.done_list = onboarding_data.get("done", [])
                    debug_print("Current onboarding done list:", self.done_list)
        else:
            self.done_list = []
            debug_print(f"{self.ha_directory}/.storage/onboarding file does not exist. Proceeding with onboarding.")

        # Create a new user via API if not already created
        if "user" not in self.done_list:
            user_created = self._create_user()
            if user_created:
                self._create_token()

        # Run other onboarding steps
        self._run_core_config()
        self._run_integration_config()
        self._run_analytics_config()

    def _create_user(self) -> bool:
        """Create a new user via Home Assistant API."""
        user_url = f"{self.base_url}/api/onboarding/users"
        payload = json.dumps({
            "client_id": self.base_url,
            "name": self.config.friendly_name,
            "username": self.config.username,
            "password": self.config.password,
            "language": self.config.language
        })
        response = requests.post(user_url, headers=self.headers, data=payload)
        debug_print(response.text)

        if response.status_code == 200:
            self.auth_code = response.json().get("auth_code", "")
            return True
        else:
            debug_print("Failed to create user. Response was:", response.text)
            return False

    def _create_token(self):
        """Create a token for further actions using the authorization code."""
        token_url = f"{self.base_url}/auth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": self.base_url,
            "code": self.auth_code
        }
        response = requests.post(token_url, data=data)
        debug_print(response.text)

        if response.status_code == 200:
            access_token = response.json().get("access_token", "")
            refresh_token = response.json().get("refresh_token", "")
            if access_token:
                self.headers['Authorization'] = f"Bearer {access_token}"
                set_key(Path(__file__).parents[2] / '.env', 'HA_REFRESH_TOKEN', refresh_token)
            else:
                debug_print("Failed to retrieve access token. Response was:", response.text)
        else:
            debug_print("Failed to obtain access token. Response was:", response.text)

    def _run_core_config(self):
        """Run the core configuration step of onboarding."""
        if "core_config" not in self.done_list:
            core_config_url = f"{self.base_url}/api/onboarding/core_config"
            response = requests.post(core_config_url, headers=self.headers)

            debug_print(response.text)
        else:
            debug_print("Core config onboarding task has already been run.")

    # TODO: This is always returning 400 - see how we can fix this
    # TODO: Check out https://community.home-assistant.io/t/how-to-add-new-user-with-command-line-or-even-to-change-user-password-with-command-line/158730/12?u=jarvix
    def _run_integration_config(self):
        """Run the integration configuration step of onboarding."""
        if "integration" not in self.done_list:
            integration_url = f"{self.base_url}/api/onboarding/integration"
            response = requests.post(integration_url, headers=self.headers)
            debug_print(response.text)
        else:
            debug_print("Integration onboarding task has already been run.")

    def _run_analytics_config(self):
        """Run the analytics configuration step of onboarding."""
        if "analytics" not in self.done_list:
            analytics_url = f"{self.base_url}/api/onboarding/analytics"
            response = requests.post(analytics_url, headers=self.headers)
            debug_print(response.text)
        else:
            debug_print("Analytics onboarding task has already been run.")


class HAClient:
    def __init__(self, base_url: str = "http://localhost:8123"):
        debug_print(f"Initializing Home Assistant on: {base_url}")
        load_dotenv(override=True) # This is to ensure we get updated refresh token as its been updated during HAInitializer
        self.base_url = base_url.rstrip('/')
        self.refresh_token = os.getenv('HA_REFRESH_TOKEN', None)
        self.ha_token = None
        self.headers = {
            'Content-Type': 'application/json',
        }

        if not self.is_ha_running():
            self.start_home_assistant()
            self.wait_until_ha_is_live()

    def is_ha_running(self) -> bool:
        """Check if HA is running by sending a request to the base URL."""
        try:
            response = requests.get(f"{self.base_url}/manifest.json", timeout=2)
            return response.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            return False

    def _get_token(self) -> str:
        """Get a valid token, refreshing or generating a new one if necessary."""
        if self.ha_token is None or datetime.now() >= self.ha_token["expires_in"]:
            if not self.refresh_token:
                raise Exception("No refresh token found in the environment.")

            token_url = f"{self.base_url}/auth/token"
            data = {
                "grant_type": "refresh_token",
                "client_id": self.base_url,
                "refresh_token": self.refresh_token
            }
            response = requests.post(token_url, data=data)
            if response.status_code == 200:
                self.ha_token = response.json()
                self.ha_token["access_token"] = self.ha_token["access_token"]
                self.ha_token["expires_in"] = datetime.now() + timedelta(seconds=self.ha_token["expires_in"])
                self.headers['Authorization'] = f"Bearer {self.ha_token['access_token']}"
            else:
                raise Exception("Failed to obtain a valid access token.")

        if self.ha_token:
            return self.ha_token["access_token"]
        else:
            raise Exception("Unable to obtain a valid access token.")

    def start_home_assistant(self) -> None:
        """Start Home Assistant by running a subprocess."""
        debug_print("Home Assistant is not running, starting it now...")
        subprocess.Popen(['hass'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def wait_until_ha_is_live(self, timeout: int = 60) -> None:
        """Wait until Home Assistant is running and responsive."""
        debug_print("Waiting for Home Assistant to start...")
        start_time = time.time()
        while not self.is_ha_running():
            if time.time() - start_time > timeout:
                raise TimeoutError("Home Assistant did not start within the given time limit.")
            time.sleep(2)  # Check every 2 seconds
        debug_print("Home Assistant is live!")

    def get_entities(self) -> List[Entity]:
        url = f"{self.base_url}{ENTITY_ENDPOINT}"
        self._get_token()
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        entities_data = response.json()
        entities = [Entity(**entity) for entity in entities_data]
        return entities

    def perform_action(self, entity_id: str, action: Action) -> bool:
        domain = entity_id.split('.')[0]
        service = ACTION_SERVICE_MAP.get(action)
        if not service:
            raise ValueError(f"Unsupported action: {action}")
        service_endpoint = SERVICE_ENDPOINT_TEMPLATE.format(domain=domain, service=service)
        url = f"{self.base_url}{service_endpoint}"
        self._get_token()
        data = {'entity_id': entity_id}
        response = requests.post(url, headers=self.headers, json=data)
        return response.status_code == 200

    def control_home_device(self, action: str, entity_name: str, entity_type: Optional[str] = None) -> str:
        entities = self.get_entities()

        # Filter entities based on the entity name and type
        matching_entities = []
        for entity in entities:
            friendly_name = entity.attributes.get('friendly_name', '').lower()
            if entity_name.lower() in friendly_name:
                if entity_type:
                    if entity.entity_id.startswith(entity_type):
                        matching_entities.append(entity)
                else:
                    matching_entities.append(entity)

        if not matching_entities:
            return f"Sorry, I couldn't find any device named '{entity_name}'."
        elif len(matching_entities) > 1:
            return f"I found multiple devices named '{entity_name}'. Please be more specific."
        else:
            target_entity = matching_entities[0]
            success = self.perform_action(entity_id=target_entity.entity_id, action=Action(action))
            if success:
                return f"'{target_entity.attributes.get('friendly_name')}' has been '{action.replace('_', ' ')}' successfully."
            else:
                return f"Sorry, I couldn't '{action.replace('_', ' ')}' '{target_entity.attributes.get('friendly_name')}'."
