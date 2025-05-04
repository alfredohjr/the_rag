import os
from uuid import uuid4

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from .Config import config_load
from .LoadPDFs import pdfs_load_to_text
from .LoadCSVs import load_csv_to_text
from .Metadata import get_metadata

def load_documents(files:list=None):

    config = config_load()

    model_name = config["DEFAULT"]["The_model"]
    tmp_dir = 'tmp'

    documents_dir = f"{tmp_dir}/{model_name}_documents"

    documents = []
    for file in os.listdir(documents_dir):

        if os.path.isdir(f'{documents_dir}/{file}'):
            continue
        
        if files is None:
            pass
        else:
            if file not in files:
                continue

        file_lower = file.lower()
        if not file_lower.endswith(('.txt','.pdf','.csv')):
            continue
        
        text = ""
        if file_lower.endswith('.txt'):
            with open(f"{documents_dir}/{file}", "r", encoding="utf-8") as f:
                text = f.read()

        if file_lower.endswith('.pdf'):
            text = pdfs_load_to_text(f"{documents_dir}/{file}")

        if file_lower.endswith('.csv'):
            text = load_csv_to_text(f"{documents_dir}/{file}")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,          
            chunk_overlap=100,       
            separators=["\n\n", "\n", ".", " ", ""],
        )

        chunks = splitter.split_text(text)

        print(f"{len(chunks)} chunks gerados.")

        file = '.'.join(file.split('.')[:-1])

        for chunk in chunks:
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={"source": file},
                )
            )

        

    uuids = [str(uuid4()) for _ in range(len(documents))]

    print("Total",len(documents))

    return {
        'documents' : documents,
        'ids' : uuids
    }
