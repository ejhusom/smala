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
        self.system_message = self.settings.get("system_message")  # Get system message from settings

    def generate_response(self, message_history):
        """Generate a response based on the message history"""

        if isinstance(message_history, str):
            message_history = [message]

        if not isinstance(message_history, list):
            raise ValueError("Message history should be a list of messages")

        # Prepare the data for the API request
        data = {
            "model": self.model,
            "system_message": self.system_message,
            "messages": message_history,
            "stream": False
        }
        
        try:
            response = requests.post(self.api_url, json=data)
            response.raise_for_status()  # Raises HTTPError for bad responses
            return response.json().get("message").get("content")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
