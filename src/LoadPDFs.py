from langchain_community.document_loaders import PyPDFLoader

def pdfs_load_to_text(file=None):

    if file is None:
        return

    loader = PyPDFLoader(file)
    documents = loader.load()

    print('File:', file,'Pages:',len(documents))

    text = ' \n '.join([documents[x].page_content for x in range(len(documents))])

    return text

if __name__ == "__main__":
    pdfs_load_to_text()