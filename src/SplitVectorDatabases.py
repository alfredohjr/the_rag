import os
import json
from collections import defaultdict
from langchain.schema import Document

from .Load import load_model
from .Save import model_save
from .Config import config_load
from .Metadata import get_metadata

PATH = 'tmp/vector_files'

def vector_path_list_files():

    path = 'tmp/vector_files'
    files = []
    for file in os.listdir(path):
        file = file.split('/')[-1].split('.')[:-1]
        file = '.'.join(file)
        files.append(file)

    return files

def vector_path_save_list_files():

    with open('tmp/vector_files.txt','w',encoding='utf-8') as f:
        f.write('\n'.join(vector_path_list_files()))

def vector_store_split_database():

    if not os.path.isdir(PATH):
        os.makedirs(PATH)

    vector_store = load_model()

    metadatas = get_metadata(vector_store)

    docs = metadatas['texts']
    vectors = metadatas['vectors']

    group_by_file = defaultdict(list)

    for doc, vec in zip(docs, vectors):
        filename = doc.metadata.get("source", "desconhecido")
        group_by_file[filename].append({
            "text": doc.page_content,
            "metadata": doc.metadata,
            "vector": vec.tolist()
        })

    for name, chunks in group_by_file.items():
        name = name.split('/')[-1].split('.')[:-1]
        name = '.'.join(name)
        with open(f"tmp/{name}.json", "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)


def vector_store_merge_database(database_files:list = None):

    if not os.path.isdir(PATH):
        os.makedirs(PATH)

    config = config_load()
    model_name = config["DEFAULT"]["The_model"]
    
    if 'documents' not in config[model_name]:
        return None
    
    vector_store = load_model()

    metadatas = get_metadata(vector_store)

    all_sources = set(metadatas['sources'])

    database_files = config[model_name]['documents'].split('|')
    path = 'tmp/vector_files'
    for file in database_files:
        full_file_path = f"{path}/{file}.json"
        if not os.path.isfile(full_file_path):
            continue
        
        if file in all_sources:
            continue

        with open(full_file_path, "r", encoding="utf-8") as f:
            dados = json.load(f)

        text_embeddings = [[chunk["text"], chunk["vector"]] for chunk in dados]
        metadata = [chunk["metadata"] for chunk in dados]

        vector_store.add_embeddings(text_embeddings=text_embeddings, metadatas=metadata)

    model_save(vector_store=vector_store)

    vector_path_save_list_files()