import subprocess
import time
from enum import Enum

import requests
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

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
    # PLUG = 'plug'

class HAFunctionInput(BaseModel):
    action: Action
    entity_name: str
    entity_type: Optional[EntityType] = None


class Entity(BaseModel):
    entity_id: str
    state: str
    attributes: Dict[str, Any] = Field(default_factory=dict)


class HAClient:
    def __init__(self, base_url: str, api_key: str, ha_start_command: str = 'hass'):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.ha_start_command = ha_start_command
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

        if not self.is_ha_running():
            self.start_home_assistant()
            self.wait_until_ha_is_live()

    def is_ha_running(self) -> bool:
        """Check if HA is running by sending a request to the base URL."""
        try:
            response = requests.get(f"{self.base_url}/api/", headers=self.headers, timeout=2)
            return response.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            return False

    def start_home_assistant(self) -> None:
        """Start Home Assistant by running a subprocess."""
        print("Home Assistant is not running, starting it now...")
        subprocess.Popen([self.ha_start_command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def wait_until_ha_is_live(self, timeout: int = 60) -> None:
        """Wait until Home Assistant is running and responsive."""
        print("Waiting for Home Assistant to start...")
        start_time = time.time()
        while not self.is_ha_running():
            if time.time() - start_time > timeout:
                raise TimeoutError("Home Assistant did not start within the given time limit.")
            time.sleep(2)  # Check every 2 seconds
        print("Home Assistant is live!")

    def get_entities(self) -> List[Entity]:
        url = f"{self.base_url}{ENTITY_ENDPOINT}"
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


