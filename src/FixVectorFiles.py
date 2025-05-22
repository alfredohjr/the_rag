import json
import os

def run():
    path = 'tmp/vector_files'
    for file in os.listdir(path):

        if not file.endswith('.json'):
            continue

        print(f'Inicio : {file}')
        
        data = {}
        with open(f'{path}/{file}','r',encoding='latin1') as f:
            data = json.load(f)
        
        tamanho_original = len(data)
        print(f'Itens : {tamanho_original}')
        
        new_data = []
        index = []
        for d in data:
            if d['text'] in index:
                continue
            new_data.append(d)
            index.append(d['text'])
        
        tamanho_apos_verificacao = len(new_data)
        print(f'Tamanho apos checar : {tamanho_apos_verificacao}')

        if tamanho_original == tamanho_apos_verificacao:
            continue
        
        try:
            with open(f'{path}/{file}', "w", encoding="utf-8") as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
        except:
            print(f"Erro no arquivo -> {file}")

        print(f'Termino : {file}')


if __name__ == "__main__":
    run()