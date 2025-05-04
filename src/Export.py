from uuid import uuid4
import pandas as pd

from .DB import get_chat_history

def main_export(chat_id:str, format:str, options=['all']) -> str:
    
    if format not in options_exports:
        raise Exception("Option not allowed")
    
    chat_history = get_chat_history(chat_id)

    print(chat_id, format, options)

    if 'all' in options:
        return options_exports[format](chat_history)
    
    chat_history_filtered = []
    for ch in chat_history:
        tmp = []
        if 'bot' in options:
            if ch[1] == 'assistant':
                tmp.append('bot')
                tmp.append(ch[2])
        if 'user' in options:
            if ch[1] == 'user':
                tmp.append('user')
                tmp.append(ch[2])
        if 'context' in options:
            tmp.append('context')
            tmp.append(ch[3])
        chat_history_filtered.append(tmp)
    
    return options_exports[format](chat_history_filtered)


def export_to_csv(chat_history):
    file_id = str(uuid4())
    file = f"tmp/export_chat_history_{file_id}.csv"

    pd.DataFrame(chat_history).to_csv(file, index=None)
    return file

def export_to_txt(chat_history):
    
    file_id = str(uuid4())
    file = f"tmp/export_chat_history_{file_id}.txt"

    with open(file,'w', encoding='utf8') as f:
        for ch in chat_history:
            f.write('|'.join([str(x) for x in ch]))
    return file


def export_to_pdf(chat_history):
    pass


def export_to_markdown(chat_history):
    
    pass


options_exports = {
    'csv':export_to_csv,
    'txt':export_to_txt,
    'pdf':export_to_pdf,
    'md':export_to_markdown
}