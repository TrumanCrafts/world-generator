import json

# Load the config file
try:
    with open('config.json') as json_file:
        CONFIG = json.load(json_file)
except FileNotFoundError:
    print("Config file not found. Please create a config.json file \
            based on the config.json.example file.")
    exit(1)
