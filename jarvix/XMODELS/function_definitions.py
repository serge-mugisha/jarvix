from XAUTO.home_assistant import HAFunctionInput

function_definitions = [
    {
        "type": "function",
        "function": {
            "name": "control_home_device",
            "description": (
                "Control a home device via Home Assistant. "
                "This function should only be used when the user command is explicitly about controlling a home device. "
                "Commands include actions like turning on/off, switching, toggling, increasing, running, or otherwise manipulating devices. "
                "Examples: 'turn off the lights', 'switch on the fan', 'toggle the bedroom lamp'. "
                "Actions should always be in snake case like 'turn_off'."
            ),
            "parameters": HAFunctionInput.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "handle_general_question",
            "description": (
                "Handle general queries or conversational questions that are not about controlling a home device. "
                "This includes questions like 'why is the sky blue?' or 'tell me a joke'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "user_query": {"type": "string", "description": "The user's query for general information or assistance."}
                },
                "required": ["user_query"]
            }
        }
    }
]
