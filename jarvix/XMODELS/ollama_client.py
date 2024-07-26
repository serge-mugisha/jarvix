import ollama


class OllamaClient:
    def __init__(self, model_name):
        self.model_name = model_name

    def process_text_with_ollama(self, text):
        response = ollama.chat(model=self.model_name, messages=[
            {
                'role': 'user',
                'content': text,
            },
        ])

        print(f"Response: {response}")
        return response['message']['content']
