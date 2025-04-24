
def get_metadata(vector_store):

    all_docs = vector_store.docstore._dict.values()

    sources = set([doc.metadata["source"] for doc in all_docs])
    sources = [x.split('/')[-1].split('.')[:-1] if x.find('.') >= 0 else x.split('/')[-1].split('.') for x in sources]
    sources = ['.'.join(x) for x in sources]

    return {
        'sources':sources,
        'texts': list(all_docs),
        'vectors': vector_store.index.reconstruct_n(0, len(list(all_docs)))
    }