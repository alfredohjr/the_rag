from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from .Config import config_load

def load_model() -> FAISS:

    config = config_load()
    model_name = config["DEFAULT"]["The_model"]

    folder = 'tmp'

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    return FAISS.load_local(
        f"{folder}/{model_name}_faiss_index", embeddings, allow_dangerous_deserialization=True
    )