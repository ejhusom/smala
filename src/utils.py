import yaml

def load_settings():
    """Load settings from yaml."""
    with open("config/settings.yaml", "r") as file:
        settings = yaml.safe_load(file)
    return settings
