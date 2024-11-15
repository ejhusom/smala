import requests
import json
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

    def generate_streaming_response(self, message_history):
        """Generate a streaming response and return the full content"""

        if isinstance(message_history, str):
            message_history = [message_history]

        if not isinstance(message_history, list):
            raise ValueError("Message history should be a list of messages")

        # Prepare the data for the API request with streaming enabled
        data = {
            "model": self.model,
            "system_message": self.system_message,
            "messages": message_history,
            "stream": True
        }

        full_response = []  # To accumulate the full response

        try:
            response = requests.post(self.api_url, json=data, stream=True)
            response.raise_for_status()  # Raises HTTPError for bad responses

            print("Assistant: ", end="", flush=True)
            for chunk in response.iter_lines():
                if chunk:
                    try:
                        chunk_data = json.loads(chunk.decode("utf-8"))
                        message_content = chunk_data.get("message", {}).get("content", "")
                        print(message_content, end="", flush=True)

                        # Append content to the full response
                        full_response.append(message_content)

                        if chunk_data.get("done"):
                            break
                    except json.JSONDecodeError as e:
                        print("\nError decoding JSON:", e)
            print("\n")  # Newline after streaming ends

            # Return the full response as a single string
            return "".join(full_response)

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
