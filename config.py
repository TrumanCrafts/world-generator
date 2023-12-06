import yaml

# Load the config file
try:
    with open('config.yaml') as file:
        CONFIG = yaml.load(file, Loader=yaml.FullLoader)
except FileNotFoundError:
    print("Config file not found. Please create a config.json file \
            based on the config.json.example file.")
    exit(1)
