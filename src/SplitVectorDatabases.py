import os
import json
from collections import defaultdict
from langchain.schema import Document
import shutil

from .Load import load_model
from .Save import model_save, run as run_model_save
from .Config import config_load
from .Metadata import get_metadata
from .DB import get_vectors

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

def vector_store_split_database(model_name:str=None):

    if not os.path.isdir(PATH):
        os.makedirs(PATH)

    vector_store = load_model(model_name)
    metadatas = get_metadata(vector_store)

    docs = metadatas['texts']
    vectors = metadatas['vectors']
    sources = metadatas['sources']

    group_by_file = defaultdict(list)

    for doc, vec in zip(docs, vectors):

        execute = True

        filename = doc.metadata.get("source", "desconhecido")
        filename_2 = '.'.join(filename.split('.')[:-1])

        for file in os.listdir(PATH):
            if file.find(filename_2) >= 0:
                execute = False
                break
        
        if execute is False:
            continue

        group_by_file[filename].append({
            "text": doc.page_content,
            "metadata": doc.metadata,
            "vector": vec.tolist()
        })

    for name, chunks in group_by_file.items():
        print(f'salvando vetor : {name}')
        name = name.split('/')[-1].split('.')[:-1]
        name = '.'.join(name)
        with open(f"{PATH}/{name}.json", "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)


def vector_store_merge_database(database_files:list = None, model_name:str=None):

    if not os.path.isdir(PATH):
        os.makedirs(PATH)

    if model_name is None:
        config = config_load()
        model_name = config["DEFAULT"]["The_model"]
    
        if 'documents' not in config[model_name]:
            return None
        
        database_files = config[model_name]['documents'].split('|')
    
    vector_store = load_model(model_name=model_name)

    metadatas = get_metadata(vector_store)

    all_sources = set(metadatas['sources'])

    path = 'tmp/vector_files'
    for file in database_files:
        full_file_path = f"{path}/{file}"
        if not os.path.isfile(full_file_path):
            continue
        
        if file in all_sources:
            continue

        with open(full_file_path, "r", encoding="utf-8") as f:
            dados = json.load(f)

        text_embeddings = [[chunk["text"], chunk["vector"]] for chunk in dados]
        metadata = [chunk["metadata"] for chunk in dados]

        vector_store.add_embeddings(text_embeddings=text_embeddings, metadatas=metadata)

    model_save(vector_store=vector_store, model_name=model_name)

    vector_path_save_list_files()

def sinc_vector_db_by_database(project_info:list[list]):

    shutil.rmtree(f'tmp/{project_info[0][6]}_faiss_index')

    run_model_save(option='save', model_name=project_info[0][6])

    vector_store_split_database(project_info[0][6])    

    vectors = get_vectors(project_info[0][1])
    vector_files = [x[2] for x in vectors]

    vector_store_merge_database(vector_files, project_info[0][6])

    documents = f'tmp/{project_info[0][6]}_documents'
    for file in os.listdir(documents):
        os.remove(f'{documents}/{file}')
