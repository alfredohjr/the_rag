import streamlit as st
import time

from src.Ask import ask_to_gemini as ask
from src.Config import list_projects
from src.DB import check_database, get_projects, get_chats, get_chat_history, create_chat_history, create_chat, get_vetores

check_database()

if "messages" not in st.session_state:
    st.session_state.messages = []

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

input_project = st.sidebar.selectbox("Pastas:",projects)

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
            st.markdown(history[2])


@st.dialog("Documentos")
def show_vectors():
    vetors = []
    with st.spinner("carregando"):
        vectors = get_vetores()
    
    for vector in vectors:
        st.checkbox(vector)

if st.sidebar.button("Configurações"):
    show_vectors()

chat_id = get_chats(project_name=input_project, chat_name=input_chat)

if prompt := st.chat_input("Digite sua mensagem:"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        create_chat_history(chat_id=chat_id[0][0], role="user", content=prompt)

    response = None    
    with st.spinner('Pensando...'):
        response = ask(prompt, chat_history[:-1])

    if response is not None:
        st.session_state.messages.append({"role": "assistant", "content": response["response"]})
        with st.chat_message("assistant"):
            create_chat_history(
                chat_id=chat_id[0][0], 
                role="assistant", 
                content=response["response"].replace("'",''), 
                context=response["context"].replace("'",''))
            st.write_stream(stream_data(response["response"]))
