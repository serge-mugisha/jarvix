import openai
from pydantic import BaseModel, Field


class ApiClient(BaseModel):
    api_key: str = Field(..., env='OPENAI_API_KEY')
    model_name: str = "gpt-3.5-turbo-0125"

    class Config:
        protected_namespaces = ()
        arbitrary_types_allowed = True

    def process_text_with_api(self, text: str) -> str:
        client = openai.Client(api_key=self.api_key)

        completion = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system",
                 "content": "You are an AI System Called Jarvix. Your Job is to answer every question users ask you. Dont forget your name is Jarvix. If a user asks please tell them your name. You only speak ENGLISH"},
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message.content
