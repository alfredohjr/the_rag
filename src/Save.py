import os

from .Config import config_load
from .Create import vector_store_create
from .Update import vector_store_update

def model_save(vector_store=None, model_name:str=None) -> None:

    if vector_store is None:
        return 

    if model_name is None:
        config = config_load()
        model_name = config["DEFAULT"]["The_model"]

    folder = 'tmp'

    vector_store.save_local(f"{folder}/{model_name}_faiss_index")

def run(option='append', model_name:str=None):

    if model_name is None:
        config = config_load()
        model_name = config["DEFAULT"]["The_model"]

    model_path = f"tmp/{model_name}_faiss_index"
    if os.path.isdir(model_path):
        if option == 'append':
            model_save(vector_store=vector_store_update(model_name), model_name=model_name)
            return

    if option in ['save','append']:
        model_save(vector_store=vector_store_create(model_name), model_name=model_name)