
def config_load(file='config.ini'):
    """Reads a configuration file and returns the configuration object."""
    import configparser
    import os
    
    config = configparser.ConfigParser()
    config.read(file)

    model_name = config["DEFAULT"]["The_model"]
    tmp_dir = 'tmp'

    documents_dir = f"{tmp_dir}/{model_name}_documents"
    if not os.path.isdir(documents_dir):
        os.makedirs(documents_dir)

    return config