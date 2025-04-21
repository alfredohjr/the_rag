import pandas as pd

def load_csv_to_text(file:str=None) -> str:
    
    df = pd.read_csv(file)

    keys = df.keys()

    text = ''
    for _, v in df.iterrows():
        text_tmp = []
        for k in keys:
            text_tmp.append(f'{k} : {v[k]}')
        text_tmp = ' | '.join(text_tmp)
        text += text_tmp + '\n\n'

    return text

if __name__ == "__main__":

    load_csv_to_text()