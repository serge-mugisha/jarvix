import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load environment variables
api_key = os.getenv('OPENAI_API_KEY')


class CustomModels:
    def __init__(self, model_name_or_path):
        self.model_name_or_path = model_name_or_path
        self.model = None
        self.tokenizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.local_model_path = os.path.join("models", *model_name_or_path.split("/"))

    def load_model(self):
        # if os.path.exists(self.local_model_path):
        #     print(f"Loading model from local path: {self.local_model_path}")
        #     self.tokenizer = AutoTokenizer.from_pretrained(self.local_model_path)
        #     self.model = AutoModelForCausalLM.from_pretrained(self.local_model_path)
        # else:
        print(f"Local model not found. Loading model from online repository: {self.model_name_or_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name_or_path)

        # Save the downloaded model locally for future use
        # self.tokenizer.save_pretrained(self.local_model_path)
        # self.model.save_pretrained(self.local_model_path)

        self.model.to(self.device)
        print("Model loaded successfully.")

    def unload_model(self):
        del self.model
        del self.tokenizer
        torch.cuda.empty_cache()
        self.model = None
        self.tokenizer = None

    def run(self):
        self.load_model()

    def stop(self):
        print("Stopping Model...")
        self.unload_model()
        print("Model unloaded!")

    def interact(self, text: str, max_new_tokens: int = 50) -> str:
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model is not loaded. Call run(True) to load the model.")

        inputs = self.tokenizer(text, return_tensors='pt').to(self.device)
        outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


if __name__ == "__main__":
    model_name = "microsoft/Phi-3-mini-4k-instruct"
    phi3 = CustomModels(model_name_or_path=model_name)

    # Example usage
    phi3.run()  # Load the model

    print("Sending an interaction...")
    response = phi3.interact("Hello, how are you?")
    print("Response: ")
    print(response)

    phi3.stop()  # Unload the model


