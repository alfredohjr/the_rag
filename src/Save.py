import os

from .Config import config_load
from .Create import vector_store_create
from .Update import vector_store_update

def model_save(vector_store=None) -> None:

    if vector_store is None:
        return 

    config = config_load()
    model_name = config["DEFAULT"]["The_model"]

    folder = 'tmp'

    vector_store.save_local(f"{folder}/{model_name}_faiss_index")

def run(option='append'):

    config = config_load()
    model_name = config["DEFAULT"]["The_model"]

    model_path = f"tmp/{model_name}_faiss_index"
    if os.path.isdir(model_path):
        if option == 'append':
            model_save(vector_store=vector_store_update())
            return

    if option in ['save','append']:
        model_save(vector_store=vector_store_create())