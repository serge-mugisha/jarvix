import openai
from anthropic import Anthropic

from pydantic import BaseModel, Field

class ApiClient(BaseModel):
    gpt_api_key: str = Field(..., env='OPENAI_API_KEY')
    claude_api_key: str = Field(..., env='ANTHROPIC_API_KEY')
    gpt_model_name: str = "gpt-4o-mini"
    claude_model_name: str = "claude-3-haiku-20240307"

    class Config:
        protected_namespaces = ()
        arbitrary_types_allowed = True

    def process_text(self, text: str, model: str = "gpt") -> str:
        if model.lower() == "gpt":
            return self.process_text_with_gpt(text)
        elif model.lower() == "claude":
            return self.process_text_with_claude(text)
        else:
            raise ValueError("Invalid model selected. Choose either 'gpt' or 'claude'.")

    def process_text_with_gpt(self, text: str) -> str:
        client = openai.Client(api_key=self.gpt_api_key)
        completion = client.chat.completions.create(
            model=self.gpt_model_name,
            messages=[
                {"role": "system", "content": "You are an AI System Called Jarvix. Your Job is to answer every question users ask you. Don't forget your name is Jarvix. If a user asks please tell them your name. You only speak ENGLISH"},
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message.content

    def process_text_with_claude(self, text: str) -> str:
        client = Anthropic(api_key=self.claude_api_key)
        completion = client.messages.create(
            model=self.claude_model_name,
            max_tokens=1000,
            messages=[
                {"role": "system", "content": "You are an AI System Called Jarvix. Your Job is to answer every question users ask you. Don't forget your name is Jarvix. If a user asks please tell them your name. You only speak ENGLISH"},
                {"role": "user", "content": text}
            ]
        )
        return completion.content[0].text
