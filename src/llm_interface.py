import requests
import yaml

# Load settings from YAML
def load_settings():
    with open("config/settings.yaml", "r") as file:
        settings = yaml.safe_load(file)
    return settings

class LLMInterface:
    def __init__(self):
        self.settings = load_settings()
        self.api_url = self.settings.get("api_url")
        self.model = self.settings.get("default_model")

    def generate_response(self, prompt):
        # Send prompt to the LLM API and get a response
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }

        try:
            response = requests.post(self.api_url, json=data)
            response.raise_for_status()  # Raises HTTPError for bad responses
            return response.json().get("message").get("content")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
