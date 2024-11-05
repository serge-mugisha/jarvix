import json
import os
from enum import Enum

import openai
from anthropic import Anthropic
from pydantic import BaseModel, Field

from jarvix.XMODELS.function_definitions import function_definitions

CHAT_ROLE_MESSAGE = (
    "You are an AI System called Jarvix. Your job is to answer every question users ask you no matter what."
    "You also support in extracting actions and entity names from user commands for use in Home Assistant API through function calling. Use supplied tools to assist the user."
)

class ModelType(Enum):
    GPT = "GPT"
    CLAUDE = "CLAUDE"
    OLLAMA = "OLLAMA"

class ChatType(Enum):
    CONVERSATION = "conversation"


class ApiClient(BaseModel):
    gpt_api_key: str = Field(..., env='OPENAI_API_KEY')
    claude_api_key: str = Field(None, env='ANTHROPIC_API_KEY')
    gpt_model_name: str = "gpt-4o-mini"
    claude_model_name: str = "claude-3-haiku-20240307"
    function_registry: dict = Field(default_factory=dict)

    class Config:
        protected_namespaces = ()
        arbitrary_types_allowed = True

    def process_text(self, text: str) -> str:
        selected_model = ModelType(os.getenv('SELECTED_MODEL'))

        if selected_model == ModelType.GPT:
            client = openai.Client(api_key=self.gpt_api_key)
            completion = client.chat.completions.create(
                model=self.gpt_model_name,
                messages=[
                    {"role": "system", "content": CHAT_ROLE_MESSAGE},
                    {"role": "user", "content": text}
                ],
                tools=function_definitions
            )

            # Check if GPT suggests a function call
            choice = completion.choices[0]
            if choice.finish_reason == 'tool_calls':
                tool_call_function = choice.message.tool_calls[0].function
                function_name = tool_call_function.name
                function_args = json.loads(tool_call_function.arguments)

                # Check if function is registered
                if function_name in self.function_registry:
                    function_to_call = self.function_registry[function_name]
                    # Call the function dynamically with arguments unpacked
                    return function_to_call(**function_args)
                else:
                    return f"Unknown function: {function_name}"

            else:
                # Regular response without function call
                return choice.message.content

        elif selected_model == ModelType.CLAUDE:
            client = Anthropic(api_key=self.claude_api_key)
            completion = client.messages.create(
                model=self.claude_model_name,
                max_tokens=1000,
                messages=[
                    {"role": "system", "content": CHAT_ROLE_MESSAGE},
                    {"role": "user", "content": text}
                ]
            )
            return completion.content[0].text
        else:
            raise ValueError("Unsupported model type. Use 'gpt' or 'claude'.")
