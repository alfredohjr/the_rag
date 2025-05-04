import os
from uuid import uuid4

from .Config import list_projects

def create_chat_file(project):

    if project not in list_projects():
        return {}
    
    path = f"tmp/{project}_responses/chat"
    chat_id = uuid4()
    with open(f"{path}/{chat_id}.txt","w") as f:
        f.write("title : null\n\n")

def chat(question, project, chat_id=None) -> dict:

    if project not in list_projects():
        return {}
    
    
