import datetime
import os
from sentence_transformers import SentenceTransformer


from .Load import load_model
from .Config import config_load
from .LoadDocuments import load_documents
from .Metadata import get_metadata

def vector_store_update():

    start = datetime.datetime.now()

    vector_store = load_model()

    config = config_load()
    model_name = config["DEFAULT"]["The_model"]
    path_documents = f"tmp/{model_name}_documents"

    metadatas = get_metadata(vector_store)

    files = []
    for file in os.listdir(path_documents):

        if os.path.isdir(f"{path_documents}/{file}"):
            continue

        if '.'.join(file.split('.')[:-1]) in metadatas['sources']:
            continue

        files.append(file)

    if len(files) == 0:
        return None

    data = load_documents(files)

    if len(data['documents']) == 0:
        return None

    embeddings = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

    texts = [x.page_content for x in data["documents"]]
    metadata = [x.metadata for x in data["documents"]]

    text_embeddings = embeddings.encode(texts, batch_size=64, show_progress_bar=True)
    text_embeddings = list(zip(texts,text_embeddings.tolist()))

    vector_store.add_embeddings(text_embeddings=text_embeddings, metadatas=metadata)
    
    finish = datetime.datetime.now()

    print("começo ->",start,"término ->", finish)
    print("tempo total :", finish - start)

    return vector_store