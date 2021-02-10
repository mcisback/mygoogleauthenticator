import os
import sys

from os.path import expanduser

import json

from GoogleAuth import sanitize_secret

class ConfigManager:
    def __init__(self):
        self.HOME = expanduser("~")
        self.CONFIG_DIR_NAME = '/.mygoogleauth'
        self.CONFIG_DIR = f"{self.HOME}{self.CONFIG_DIR_NAME}"
        self.CONFIG_FILE = 'totp.json'
        self.CONFIG_FILE_PATH = f"{self.CONFIG_DIR}/{self.CONFIG_FILE}"
        self.MASTER_PASSWORD = ''

        self.config = {}

    def get(self):
        return self.config

    def init_config_file(self):
        return self.save_and_set_config({
            'config': {},
            'secrets': {}
        })

    def init_config(self):
        try:
            os.mkdir(self.CONFIG_DIR)
        except OSError:
            print("Creation of the directory %s failed" % self.CONFIG_DIR)
        else:
            print("Successfully created the directory %s" % self.CONFIG_DIR)

        print(f"Creating Config File: {self.CONFIG_DIR}")

        self.init_config_file()


    def load_config(self):
        if not os.path.isdir(self.CONFIG_DIR):
            print(f"{self.CONFIG_DIR} is not present... creating it")

            self.init_config()
        elif not os.path.isfile(self.CONFIG_FILE_PATH):
            print(f"{self.CONFIG_FILE_PATH} is not present... creating it")

            self.init_config_file()

        with open(self.CONFIG_FILE_PATH, "r") as file:
            file_content = file.read()
            file.close()

            self.config = json.loads(file_content)

            return self.config

    def save_config(self):
        try:
            file = open(self.CONFIG_FILE_PATH, 'w+')
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
        except:  # handle other exceptions such as attribute errors
            print("Unexpected error:", sys.exc_info()[0])

        json_string = json.dumps(self.config)

        # print("Writing JSON Config: ", json_string)

        file.write(json_string)
        file.close()

    def save_and_set_config(self, new_config):
        self.check_config(new_config)

        self.config = new_config

        return self.save_config()

    def sanitize_key(self, custom_id):
        if not isinstance(custom_id, str):
            raise TypeError("custom_id is not a string")

        return custom_id.lower()

    def add_entry(self, custom_id, secret, save=True):
        custom_id = self.sanitize_key(custom_id)
        self.config['secrets'][custom_id] = sanitize_secret(secret)

        if save:
            self.save_config()

    def del_entry(self, custom_id, save=True):
        custom_id = self.sanitize_key(custom_id)

        if self.has_entry(custom_id):
            del self.config['secrets'][custom_id]

            if save:
                self.save_config()
            return True
        else:
            raise KeyError(f"{custom_id} not in config")

    def get_entry_by_key(self, custom_id):
        custom_id = self.sanitize_key(custom_id)

        if self.has_entry(custom_id):
            return self.config['secrets'][custom_id]
        else:
            raise KeyError(f"{custom_id} not in config")

    def num_entries(self):
        return len(self.list_entries())

    def list_entries(self):
        return self.config['secrets']

    def has_entry(self, custom_id):
        return self.sanitize_key(custom_id) in self.config['secrets']

    def check_config(self, config):
        if not isinstance(config, dict):
            raise TypeError("config is not a dictionary")

        # Empty Dict evaluate to False in Python
        if bool(config) == False:
            raise ValueError("config is an empty dict, missing required keys")

        REQUIRED_KEYS = {
            'config': 'dict',
            'secrets': 'dict'
        }

        for req_key, type in REQUIRED_KEYS.items():
            if not req_key in config:
                raise ValueError(f"config is missing '{req_key}' key")
            if not isinstance(config[req_key], eval(type)):
                raise TypeError(f"config['{req_key}'] is not of required type: {type}")

        return True