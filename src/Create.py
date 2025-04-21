import datetime

from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer

from .LoadDocuments import load_documents

def vector_store_create():

    start = datetime.datetime.now()

    data = load_documents()

    embeddings = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

    texts = [x.page_content for x in data["documents"]]
    metadata = [x.metadata for x in data["documents"]]

    text_embeddings = embeddings.encode(texts, batch_size=64, show_progress_bar=True)
    
    text_embedding_pairs = list(zip(texts, text_embeddings))
    vector_store = FAISS.from_embeddings(text_embedding_pairs, embeddings, metadatas=metadata)

    finish = datetime.datetime.now()

    print("começo ->",start,"término ->", finish)
    print("tempo total :", finish - start)

    return vector_store
