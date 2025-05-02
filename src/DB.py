import sqlite3
from uuid import uuid4
import datetime

from .Metadata import get_metadata
from .Load import load_model

DB_FILE = 'the_rag.db'

def check_database():

    con = sqlite3.connect(DB_FILE)

    create_project = """create table if not exists rag_project(id varchar(50), name varchar(50) unique, language varchar(30), template_file varchar(100), active boolean default true, created_at datetime, updated_at datetime)"""
    create_vector = """create table if not exists rag_vector(id varchar(50), name varchar(50), file varchar(250), active boolean default true, created_at datetime, updated_at datetime)"""
    create_project_vector = """create table if not exists rag_project_vetor(id varchar(50), project_id varchar(50), vector_id varchar(50), active boolean default true, created_at datetime, updated_at datetime)"""
    create_chat = """create table if not exists rag_chat(id varchar(50), name varchar(50) unique, active boolean default true, project_id varchar(50), created_at datetime, updated_at datetime)"""
    create_history = """create table if not exists rag_chat_history(id varchar(50), chat_id varchar(50), role varchar(30), content text, context text, active boolean default true, score int default -1, created_at datetime, updated_at datetime)"""

    cur = con.cursor()
    for command in [create_project, create_vector, create_project_vector, create_chat, create_history]:
        cur.execute(command)
    cur.close()
    con.close()

def create(table,obj,prefix='rag_'):

    check_database()

    con = sqlite3.connect(DB_FILE)

    obj["id"] = str(uuid4())
    obj["created_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    obj["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    column_name = ','.join(list(obj.keys()))
    column_value = "'" + "','".join(list(obj.values())) + "'"

    insert_command = f"insert into {prefix}{table}({column_name}) values({column_value})"

    cur = con.cursor()
    cur.execute(insert_command)
    cur.execute('commit')
    cur.close()
    con.close()

def update(table, obj, obj_id, prefix='rag_'):

    if table in ['rag_chat_history']:
        return None

    check_database()

    con = sqlite3.connect(DB_FILE)

    obj["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    list_update = []
    for o in obj:
        list_update.append(
            f"{o[0]} = '{o[1]}'"
        )

    list_update = ', '.join(list_update)

    update_command = f"update {prefix}{table} set {list_update} where id = {obj_id}"

    cur = con.cursor()
    cur.execute(update_command)
    cur.execute('commit')
    cur.close()
    con.close()

def get(table:str, where:dict=None, columns='*', prefix='rag_'):

    check_database()

    con = sqlite3.connect(DB_FILE)

    list_update = []
    if where is None:
        list_update = ''
    else:
        for o in where.items():
            list_update.append(
                f"{o[0]} = '{o[1]}'"
            )

        list_update = 'where ' + ' and '.join(list_update)

    select = f"select {columns} from {prefix}{table} {list_update} order by updated_at asc"

    cur = con.cursor()
    res = cur.execute(select)
    res_select = res.fetchall()
    cur.close()
    con.close()

    return res_select


def get_projects(columns='id, name', where:dict=None):

    res = get(table='project', columns=columns, where=where)
    return res

def create_project(name):

    projects = get_projects()
    for project in projects:
        if name == project[1]:
            return f'Project {project} already exists'
    
    create(table='project', obj={'name':name})


def get_chats(project_name:str, chat_name:str=None):

    project = get_projects(where={'name':project_name})
    if len(project) == 0:
        return None

    if chat_name is None:
        where = {}
        where['project_id'] = project[0][0]
        return get(table='chat',where=where)
    else:
        where = {}
        where['name'] = chat_name
        where['project_id'] = project[0][0]
        return get(table='chat',where=where)


def create_chat(name:str, project:str):

    project = get_projects(where={'name':project})
    if len(project) == 0:
        return []
    
    chats = get_chats(project_name=project[0][1],chat_name=name)
    if len(chats) == 0:
        create(table='chat', obj={'name':name,'project_id':project[0][0]})

    return get_chats(project_name=project[0][1], chat_name=name)


def get_chat_history(chat_id:str):

    return get(table='chat_history',columns='id, role, content', where={'chat_id':chat_id})

def create_chat_history(chat_id:str, role:str, content:str, context:str=None):

    chat = get(table='chat', where={'id':chat_id})
    if len(chat) == 0:
        return []
    
    create(table='chat_history', 
           obj={'chat_id':chat_id, 
                'role':role, 
                'content':content,
                'context':context if context else ''})
    
def get_vetores():
        vector_store = load_model()
        metadatas = get_metadata(vector_store)
        return metadatas['sources']



create_project('NumeroUm')
create_chat("NumeroUm","NumeroUm")