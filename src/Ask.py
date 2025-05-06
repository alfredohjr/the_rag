import os
import datetime
import time
from google import genai
from dotenv import load_dotenv
import time
from google.genai import types

load_dotenv()

from .Load import load_model
from .Config import config_load

config = config_load()

def print_slow(text, delay=0.075):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print('\n') 

def get_token(text):
    print('Token por palavra', len(text.split()))

def now():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

def count_token(text):
    print('Tokens[palavras]',len(text.split()))

def print_slow(text,delay=.075):
    for t in text:
        print(t,end='',flush=True)
        time.sleep(delay)


def load_prompt(question, context, project_info:dict=None):

    if project_info is None:
        model = config["DEFAULT"]["The_model"]
        file_template = config[model]["prompt_template_file"] if "prompt_template_file" in config[model] else None

        if file_template is None:
            return f"Responda essa questão:{question} usando somente esse contexto:{context} não use dados externos"

        with open(f'templates/{file_template}','r') as f:
            text = f.read()

        text = text.format(question=question,context=context)
        return text
    else:
        file_template = project_info[4]
        prompt = project_info[5]

        if file_template:

            with open(f'templates/{file_template}','r') as f:
                text = f.read()

            text = text.format(question=question,context=context)
            return text
        
        if prompt:
            return prompt.format(question=question, context=context)

        return f"Responda essa questão:{question} usando somente esse contexto:{context} não use dados externos"

def main_translate(question, model_language):
    question = f"""convert the text : {question}, to : {model_language}, return only the translation"""
    return main_ask_gemini(question=question)

def main_ask_gemini(question:str, history:list=None):

    gemini_api_key = os.getenv('gemini_api_key')
    if gemini_api_key is None:
        raise Exception('Adicione a variavel de ambiente gemini_api_key para continuar')

    client = genai.Client(api_key=gemini_api_key)

    content = []
    if history is not None:
        for h in history:
            content.append(
                types.Content(
                    role=h[1],
                    parts=[
                        types.Part.from_text(text=h[2]),
                    ],
                )
            )
    
    content.append(
        types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=question),
                ],
        )
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=content,
    )

    return {'response' : response.text} 

def main_ask(question:str, project_info:list, chat_info:list, history:list=None):

    project_info = project_info[0]
    chat_info = chat_info[0]

    model_language = project_info[3]

    ask = question.split('|')[0]

    if model_language is not None:
        ask = main_translate(ask, model_language)['response']

    vector_store = load_model(project_info[6])

    results = vector_store.similarity_search(
        ask,
        k=chat_info[2]
    )

    context = ""
    for index, res in enumerate(results):
        result = f"[{index+1}] {res.page_content}"

        context += result.replace('\n',' ') + '\n\n'

    question = load_prompt(question, context, project_info)
    response = {}
    response['context'] = context
    response['response'] = main_ask_gemini(question=question, history=history)['response']
    return response

def ask_get(question=None):

    vector_store = load_model()

    results = vector_store.similarity_search(
        "me fale sobre o egito",
        k=5
    )

    for index, res in enumerate(results):
        print(f"{index+1} * {res.page_content} [{res.metadata}]")


def ask_to_gemini(question=None, history:list=None, obj:dict=None):

    gemini_api_key = os.getenv('gemini_api_key')
    if gemini_api_key is None:
        raise Exception('Adicione a variavel de ambiente gemini_api_key para continuar')

    client = genai.Client(api_key=gemini_api_key)

    if obj is None:
        model_name = config["DEFAULT"]["The_model"]
        model_language = None if 'language' not in config[model_name] else config[model_name]['language']

    ask = question.split('|')[0]

    if model_language is not None:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""convert the text : {ask}, to : {model_language}, return only the translation""",
        )

        ask = response.text

    vector_store = load_model()

    results = vector_store.similarity_search(
        ask,
        k=5
    )

    context = ""
    for index, res in enumerate(results):
        result = f"[{index+1}] {res.page_content}"

        context += result.replace('\n',' ') + '\n\n'

    content = []
    if history is not None:
        for h in history[-5:]:
            content.append(
                types.Content(
                    role=h[1],
                    parts=[
                        types.Part.from_text(text=h[2]),
                    ],
                )
            )
    
    content.append(
        types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=load_prompt(question, context)),
                ],
        )
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=content,
    )

    return {
        'response' : response.text,
        'context' : context
    } 


def manual_ask(save_data=True):

    model_name = config["DEFAULT"]["The_model"]

    path = f'tmp/{model_name}_responses/manual'
    if save_data:
        if not os.path.isdir(path):
            os.makedirs(path)

    n = now()
    n_format = datetime.datetime.strptime(n,'%Y%m%d%H%M%S').strftime('%d/%m/%Y %H:%M:%S')
    quit = False
    count = 1
    while not quit:
        print("#"*5)
        question = input("Qual a sua pergunta? ")

        if question.strip().lower() in ['q','quit','exit','']:
            quit = True
            continue

        response = ask_to_gemini(question)
        print_slow(response['response'])
        context = response['context']
        response = response['response']

        if save_data:
            with open(f'{path}/question_{n}_{count}.md','w', encoding='utf-8') as f:
                f.write(f'Question : {question}\nDate : {n_format}\n\n<div style="padding:24px;font-size:12px">\nContext : \n\n{context}\n</div>\n\nResponse : \n\n{response}')
            count += 1

def auto_task(file=None,save_data=True):

    if file is None:
        return

    if not os.path.isfile(file):
        return
    
    question_list = []
    with open(file,'r',encoding='utf-8') as f:
        question_list = f.readlines()

    model_name = config["DEFAULT"]["The_model"]

    n = now()
    n_format = datetime.datetime.strptime(n,'%Y%m%d%H%M%S').strftime('%d/%m/%Y %H:%M:%S')

    path = f'tmp/{model_name}_responses/r{n}'
    if save_data:
        if not os.path.isdir(path):
            os.makedirs(path)

    for index, question in enumerate(question_list):

        if not question.startswith(('*')):
            continue

        print('question:',question)
        response = ask_to_gemini(question)
        context = response['context']
        response = response['response']

        print('context', context)
        print('response', response)

        if save_data:
            with open(f'{path}/question_{index+1}_{n}.md','w', encoding='utf-8') as f:
                f.write(f'File : {file}\n\nQuestion : {question}\nDate : {n_format}\n\n<div style="padding:24px;font-size:12px">\nContext : \n\n{context}\n</div>\n\nResponse : \n\n{response}')