import requests
import json
from utils import load_settings


class LLMInterface:
    def __init__(self):
        self.settings = load_settings()
        self.api_url = self.settings.get("api_url")
        self.model = self.settings.get("default_model")
        self.system_message = self.settings.get("system_message")

    def _post_request(self, data):
        """Internal helper to send a post request and handle exceptions."""
        try:
            response = requests.post(self.api_url, json=data, stream=data.get("stream", False))
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def generate_response(self, message_history, system_message=None):
        """Generate a response based on the message history."""
        if isinstance(message_history, str):
            message_history = [message_history]
        
        data = {
            "model": self.model,
            "system_message": system_message or self.system_message,
            "messages": message_history,
            "stream": False
        }

        if self.settings.get("verbose"): 
            print(data)

        response = self._post_request(data)
        if response:
            return response.json().get("message", {}).get("content", "Error: No content received.")
        return None

    def generate_streaming_response(self, message_history):
        """Generate a streaming response and return the full content."""
        data = {
            "model": self.model,
            "system_message": self.system_message,
            "messages": message_history,
            "stream": True
        }

        if self.settings.get("verbose"): 
            print(data)

        full_response = []
        response = self._post_request(data)

        if response:
            print("Assistant: ", end="", flush=True)
            for chunk in response.iter_lines():
                if chunk:
                    try:
                        chunk_data = json.loads(chunk.decode("utf-8"))
                        message_content = chunk_data.get("message", {}).get("content", "")
                        print(message_content, end="", flush=True)
                        full_response.append(message_content)
                        if chunk_data.get("done"):
                            break
                    except json.JSONDecodeError as e:
                        print("\nError decoding JSON:", e)
            print("\n")
            return "".join(full_response)
        return None
