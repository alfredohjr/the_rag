import configparser
import os

config = configparser.ConfigParser()

def config_load(file='config.ini'):
    """Reads a configuration file and returns the configuration object."""
    
    config.read(file)

    model_name = config["DEFAULT"]["The_model"]
    tmp_dir = 'tmp'

    documents_dir = f"{tmp_dir}/{model_name}_documents"
    if not os.path.isdir(documents_dir):
        os.makedirs(documents_dir)

    return config

def list_projects(file="config.ini"):

    config.read(file)

    new_list = []
    for i in config.sections():
        if i == "DEFAULT":
            continue
        new_list.append(i)
    return new_list

def list_chat_in_projects(project, file="config.ini"):

    config.read(file)

    if project not in config.sections():
        return []

    path = f"tmp/{project}_responses/chat"
    if not os.listdir(path):
        return []

    new_list = []
    for i in os.listdir(path):
        new_list.append(i)
    return new_list