import os
import faiss
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore

from .Config import config_load

def load_model() -> FAISS:

    config = config_load()
    model_name = config["DEFAULT"]["The_model"]

    folder = 'tmp'

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    if not os.path.isdir(f"{folder}/{model_name}_faiss_index"):

        index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

        return FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )

    return FAISS.load_local(
        f"{folder}/{model_name}_faiss_index", embeddings, allow_dangerous_deserialization=True
    )