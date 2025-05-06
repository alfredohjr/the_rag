import streamlit as st
import time

from src.Ask import main_ask
from src.Config import list_projects, list_file_extensions_allowed
from src.Export import main_export
from src.DB import (
    check_database, 
    get_projects, 
    get_chats, 
    get_chat_history, 
    create_chat_history, 
    create_chat, 
    get_vetores,
    create_project,
    update_project,
    update_chat,
    update_chat_history,
    get_alises_folders_and_id,
    get_vectors,
    sinc_unique_project_vector,
)

check_database()

vectors = get_vectors()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "projects" not in st.session_state:
    st.session_state.projects = []

if "chats" not in st.session_state:
    st.session_state.chats = []

def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.075)

st.set_page_config(page_title="the_rag", page_icon=None)
st.title("the_rag")

st.sidebar.write("Olá")

projects = [x[1] for x in get_projects()]

st.session_state.projects = projects

if input_project := st.sidebar.selectbox(
        "Pastas:",
        st.session_state.projects,
        index=None,
        placeholder="Add/Select",
        accept_new_options=True):

    if input_project not in projects:
        create_project(input_project)
        st.session_state.projects.append(input_project)

chats = None
if input_project:
    chats = [x[1] for x in get_chats(project_name=input_project)]

st.session_state.chats = chats

chat_history = []

if input_chat := st.sidebar.selectbox(
    "Chats:",
    st.session_state.chats, 
    index=None,
    placeholder="Add/Select",
    accept_new_options=True):

    if input_chat not in chats:
        create_chat(input_chat, input_project)
        st.session_state.chats.append(input_chat)

    chat_history = get_chat_history(
        chat_id=get_chats(chat_name=input_chat, project_name=input_project)[0][0]
    )

    st.session_state.messages = []
    for history in chat_history:
        st.session_state.messages.append({"role": history[1], "content": history[2]})
        with st.chat_message(history[1]):
            if history[1] == 'assistant':
                expander_chat_history = st.expander("Contexto")
                expander_chat_history.write(history[3])
            st.markdown(history[2])
            if history[1] == 'assistant':
                input_feedback = st.feedback("thumbs", key=history[0])
                if input_feedback is not None:
                    if input_feedback != history[4]:
                        update_chat_history(chat_id=history[0], obj={'score':input_feedback})



@st.dialog("Exportar dados")
def exports():

    container_options = st.container(border=True)
    container_options.title("Exportar:")
    input_export_bot = container_options.checkbox("Conversa BOT")
    input_export_user = container_options.checkbox("Conversa Usuário")
    input_export_context = container_options.checkbox("Contexto")
    input_export_all = container_options.checkbox("Completo")

    options_input_download = [
        'bot' if input_export_bot else None,
        'user' if input_export_user else None,
        'context' if input_export_context else None,
        'all' if input_export_all else None
    ]

    container_formats = st.container(border=True)

    options = ['csv','txt']
    if input_download_format := container_formats.selectbox("Formato",options, index=None, placeholder="Selecione a opção"):

        with open(main_export(chat_info[0][0],input_download_format, options_input_download),'rb') as file:
            container_formats.download_button("Download", data=file, file_name=f'export.{input_download_format}', mime=f"text/{input_download_format}")

def t(o):
    print(o)

@st.dialog("Configurações")
def show_vectors():

    container_geral = st.container(border=True)
    container_geral.title("Geral:")
    project_info = get_projects(where={'name':input_project})
    input_save_documents = container_geral.checkbox(
            "Salvar documentos em json?", 
            value=True if project_info[0][2] == 1 else False)
    
    if input_save_documents != project_info[0][2]:
        update_project(project_id=project_info[0][0], obj={"save_json": 1 if input_save_documents else 0})
    
    container_pasta = st.container(border=True)
    container_pasta.title("Pasta:")

    input_language = container_pasta.text_input("Linguagem", value=project_info[0][3])
    if input_language != project_info[0][3]:
        update_project(project_id=project_info[0][0], obj={'language':input_language})

    input_prompt = container_pasta.text_area("Prompt", value=project_info[0][5])
    if input_prompt != project_info[0][5]:
        update_project(project_id=project_info[0][0], obj={'prompt':input_prompt})

    chat_info = get_chats(project_name=input_project, chat_name=input_chat)
    container_conversa = st.container(border=True)
    container_conversa.title("Conversa:")
    input_k = container_conversa.slider("K",1,10,value=chat_info[0][2],step=1)
    if input_k != chat_info[0][2]:
        update_chat(chat_id=chat_info[0][0], obj={'k': input_k})

    input_size_history = container_conversa.slider("Historico",1,30,value=chat_info[0][3], step=1)
    if input_size_history != chat_info[0][3]:
        update_chat(chat_id=chat_info[0][0], obj={'history':input_size_history})
    
    container_documentos = st.container(border=True)
    container_documentos.write(f"Extensões permitidas : {', '.join(list_file_extensions_allowed())}")
    input_upload_file = container_documentos.file_uploader("Upload de arquivos", accept_multiple_files=True)

    container_documentos.title("Documentos:")
    vetors_projects = get_vectors(input_project)

    input_vectors = container_documentos.multiselect(
        "Selecione os documentos",
        options=[x[1] for x in vectors],
        default=[x[1] for x in vetors_projects]
        )
        
    if container_documentos.button("Atualizar"):
        if len(vetors_projects) == 0:
            for v in vectors:
                if v[1] in input_vectors:
                    sinc_unique_project_vector(project_info[0][0], v[0], True)

        else:
            for v1 in vetors_projects:
                if v1[1] in input_vectors:
                    sinc_unique_project_vector(project_info[0][0], v1[0], True)
                else:
                    sinc_unique_project_vector(project_info[0][0], v1[0], False)

            for iv in input_vectors:
                if iv not in [v[1] for v in vetors_projects]:
                    for v1 in vectors:
                        if iv == v1[1]:
                            sinc_unique_project_vector(project_info[0][0], v1[0], True)
                            break


project_info = get_projects(where={'name':input_project})
chat_info = get_chats(project_name=input_project, chat_name=input_chat)

if input_chat:
    if st.sidebar.button("Configurações"):
        show_vectors()

    if st.sidebar.button("Exportar conversa"):
        exports()

chat_id = get_chats(project_name=input_project, chat_name=input_chat)

if prompt := st.chat_input("Digite sua mensagem:", disabled=True if input_chat is None else False):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        create_chat_history(chat_id=chat_id[0][0], role="user", content=prompt)

    response = None    
    with st.spinner('Pensando...'):
        response = main_ask(prompt, project_info=project_info, chat_info=chat_info, history=chat_history[(chat_info[0][3]+1)*-1:-1])

    if response is not None:
        st.session_state.messages.append({"role": "assistant", "content": response["response"]})
        with st.chat_message("assistant"):
            expander_assistant_response = st.expander("Contexto")
            expander_assistant_response.write(response["context"])
            create_chat_history(
                chat_id=chat_id[0][0], 
                role="assistant", 
                content=response["response"].replace("'",''), 
                context=response["context"].replace("'",''))
            st.write_stream(stream_data(response["response"]))
            input_feedback = st.feedback("thumbs")
            print(input_feedback)
