import os
from enum import Enum

import openai
from anthropic import Anthropic
from pydantic import BaseModel, Field

CHAT_ROLE_MESSAGE = (
    "You are an AI System Called Jarvix. Your job is to answer every question users ask you. "
    "Don't forget your name is Jarvix. If a user asks, please tell them your name. You only speak ENGLISH."
)

IOT_ROLE_MESSAGE = (
    "You are a helpful assistant that extracts actions and entity names from user commands for use in home automation API."
)

class ModelType(Enum):
    GPT = "GPT"
    CLAUDE = "CLAUDE"
    OLLAMA = "OLLAMA"

class ChatType(Enum):
    CONVERSATION = "conversation"
    IOT = "iot"

class ApiClient(BaseModel):
    gpt_api_key: str = Field(..., env='OPENAI_API_KEY')
    claude_api_key: str = Field(None, env='ANTHROPIC_API_KEY')
    gpt_model_name: str = "gpt-4o-mini"
    claude_model_name: str = "claude-3-haiku-20240307"

    class Config:
        protected_namespaces = ()
        arbitrary_types_allowed = True

    def process_text(self, text: str, chat_type: ChatType = ChatType.CONVERSATION) -> str:
        selected_model = ModelType(os.getenv('SELECTED_MODEL'))

        if selected_model == ModelType.GPT:
            client = openai.Client(api_key=self.gpt_api_key)
            completion = client.chat.completions.create(
                model=self.gpt_model_name,
                messages=[
                    {"role": "system", "content": CHAT_ROLE_MESSAGE if chat_type == ChatType.CONVERSATION else IOT_ROLE_MESSAGE},
                    {"role": "user", "content": text}
                ]
            )
            return completion.choices[0].message.content
        elif selected_model == ModelType.CLAUDE:
            client = Anthropic(api_key=self.claude_api_key)
            completion = client.messages.create(
                model=self.claude_model_name,
                max_tokens=1000,
                messages=[
                    {"role": "system", "content": CHAT_ROLE_MESSAGE if chat_type == ChatType.CONVERSATION else IOT_ROLE_MESSAGE},
                    {"role": "user", "content": text}
                ]
            )
            return completion.content[0].text
        else:
            raise ValueError("Unsupported model type. Use 'gpt' or 'claude'.")
