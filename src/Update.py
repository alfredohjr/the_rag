import datetime
import os
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer


from .Load import load_model
from .Config import config_load
from .LoadDocuments import load_documents

def vector_store_update():

    start = datetime.datetime.now()

    vector_store = load_model()

    config = config_load()
    model_name = config["DEFAULT"]["The_model"]
    path_documents = f"tmp/{model_name}_documents"

    all_docs = vector_store.docstore._dict.values()

    sources = set([doc.metadata["source"] for doc in all_docs])

    files = []
    for file in os.listdir(path_documents):

        if os.path.isdir(f"{path_documents}/{file}"):
            continue

        if f"{path_documents}/{file}" in sources:
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
    
    text_embedding_pairs = list(zip(texts, text_embeddings))
    vector_store_2 = FAISS.from_embeddings(text_embedding_pairs, embeddings, metadatas=metadata)

    vector_store.merge_from(vector_store_2)

    finish = datetime.datetime.now()

    print("começo ->",start,"término ->", finish)
    print("tempo total :", finish - start)

    return vector_store