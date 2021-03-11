import configparser, os

configurations = configparser.RawConfigParser()
config_file=os.path.join(os.path.dirname(__file__), 'config.ini')
configurations.read(config_file)