from jarvix.XAUTO.home_assistant import HAFunctionInput

function_definitions = [
    {
        "type": "function",
        "function": {
            "name": "control_home_device",
            "description": "Control a home device via Home Assistant. Call this whenever you want to control any home device for example when a user says 'turn on the bedroom light'.",
            "parameters": HAFunctionInput.model_json_schema()
        }
    },
]