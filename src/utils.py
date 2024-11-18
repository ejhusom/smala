import json
import yaml

def load_settings():
    """Load settings from yaml."""
    with open("config/settings.yaml", "r") as file:
        settings = yaml.safe_load(file)
    return settings

def load_conversation_from_file(file_path):
    """Load a conversation from a JSON file."""
    if not os.path.exists(file_path):
        print(f"Warning: No existing conversation found at {file_path}. Starting a new conversation.")
        return []

    with open(file_path, "r") as file:
        conversation = json.load(file)

    return conversation

def save_conversation_to_file(conversation, file_path):
    """Save the conversation to a JSON file"""
    with open(file_path, "w") as file:
        json.dump(conversation, file, indent=2)

def get_multiline_input(line=""):
    """Allow multi-line input using triple quotes to start and end."""
    lines = [line]
    while True:
        line = input(">>> ")
        if line.strip() == '"""':  # End multi-line input if '"""' is typed
            break
        lines.append(line)
    return "\n".join(lines)  # Combine all lines into a single string
