import sqlite3
from uuid import uuid4
import datetime
import os

from .Metadata import get_metadata
from .Load import load_model
from .Config import get_debug, get_alias

DEBUG = get_debug()

DB_FILE = 'the_rag.db'

def check_database():

    con = sqlite3.connect(DB_FILE)

    create_project = """create table if not exists rag_project(id varchar(50), name varchar(50) unique, language varchar(30), template_file varchar(100), active boolean default true, created_at datetime, updated_at datetime)"""
    create_vector = """create table if not exists rag_vector(id varchar(50), name varchar(50), file varchar(250), active boolean default true, created_at datetime, updated_at datetime)"""
    create_project_vector = """create table if not exists rag_project_vetor(id varchar(50), project_id varchar(50), vector_id varchar(50), active boolean default true, created_at datetime, updated_at datetime)"""
    create_chat = """create table if not exists rag_chat(id varchar(50), name varchar(50) unique, active boolean default true, project_id varchar(50), created_at datetime, updated_at datetime)"""
    create_history = """create table if not exists rag_chat_history(id varchar(50), chat_id varchar(50), role varchar(30), content text, context text, active boolean default true, score int default -1, created_at datetime, updated_at datetime)"""

    migration_1 = [create_project, create_vector, create_project_vector, create_chat, create_history]

    create_config = """create table if not exists rag_config(key varchar(100) unique, value text, description text, active boolean default true, created_at datetime, updated_at datetime)"""
    create_log = """create table if not exists rag_log(key varchar(100) unique, value text, active boolean default true, created_at datetime, updated_at datetime)"""
    add_column_project_prompt = """alter table rag_project add column prompt text"""
    add_column_chat_k = """alter table rag_chat add column k int default 5"""
    add_column_chat_history = """alter table rag_chat add column history int default 20"""

    migration_2 = [create_config, create_log, add_column_project_prompt, add_column_chat_k, add_column_chat_history]
    migration_2 += migration_1

    add_column_config_id = """alter table rag_config add column id varchar(50)"""
    add_column_log_id = """alter table rag_log add column id varchar(50)"""

    migration_3 = [add_column_config_id, add_column_log_id]
    migration_3 += migration_2

    add_column_project_save_json = """alter table rag_project add column save_json boolean default 1"""

    migration_4 = [add_column_project_save_json]
    migration_4 += migration_3

    add_column_project_alias_folder = """alter table rag_project add column alias_folder varchar(50) default 'theprince'"""

    migration_5 = [add_column_project_alias_folder]
    migration_5 += migration_4

    add_column_vector_description = """alter table rag_vector add column description"""
    
    migration_6 = [add_column_vector_description]
    migration_6 += migration_5

    migrations = migration_6

    cur = con.cursor()
    for command in migrations:
        try:
            cur.execute(command)
        except Exception as e:
            print(e)
    cur.close()
    con.close()

    create_vectors()

def create(table,obj,prefix='rag_',use_id=True):

    con = sqlite3.connect(DB_FILE)

    if use_id:
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

def update(table, obj, obj_id, prefix='rag_', update_deleted=False):

    con = sqlite3.connect(DB_FILE)

    obj["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    list_update = []
    for o in obj.items():
        list_update.append(
            f"{o[0]} = '{o[1]}'"
        )

    list_update = ', '.join(list_update)

    update_command = f"update {prefix}{table} set {list_update} where id = '{obj_id}'"
    if update_deleted is False:
        update_command += ' and active = 1'
    print(update_command)

    log_uuid = str(uuid4())
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    log_key = f"{prefix}{table}_{obj_id}_{timestamp}"
    log_command = f"""insert into {prefix}log(id, key, value, created_at, updated_at) values('{log_uuid}','{log_key}','{update_command.replace("'","")}','{obj['updated_at']}','{obj['updated_at']}')"""
    
    cur = con.cursor()
    cur.execute(update_command)
    cur.execute(log_command)
    cur.execute('commit')
    cur.close()
    con.close()

def get(table:str, where:dict=None, columns='*', prefix='rag_', get_deleted=False):

    con = sqlite3.connect(DB_FILE)

    list_update = []
    if where is None:
        list_update = ''
    else:
        if get_deleted is False:
            where['active'] = 1
        
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


def get_projects(columns='id, name, save_json, language, template_file, prompt, alias_folder', where:dict=None):

    res = get(table='project', columns=columns, where=where)
    return res


def create_project(name):

    import string

    projects = get_projects()
    for project in projects:
        if name == project[1]:
            return f'Project {project} already exists'
    alias_folder = ''
    for n in name.lower():
        if n in string.ascii_lowercase:
            alias_folder += n

    create(table='project', obj={'name':name,'alias_folder':alias_folder})


def update_project(project_id:str, obj:dict):

    update(table='project', obj_id=project_id, obj=obj)


def get_alises_folders_and_id(project_info:dict=None):

    aliases = get_alias()
    alias_id = 0
    count = 0
    for a in aliases:
        if project_info[0][6] == a:
            alias_id = count
            break
        count += 1

    return {
        'aliases':aliases,
        'alias_id':alias_id
    }


def get_chats(project_name:str, chat_name:str=None, columns='id, name, k, history'):

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
        return get(table='chat',where=where,columns=columns)


def create_chat(name:str, project:str):

    project = get_projects(where={'name':project})
    if len(project) == 0:
        return []
    
    chats = get_chats(project_name=project[0][1],chat_name=name)
    if len(chats) == 0:
        create(table='chat', obj={'name':name,'project_id':project[0][0]})

    return get_chats(project_name=project[0][1], chat_name=name)


def update_chat(chat_id:str, obj:dict):

    update('chat', obj_id=chat_id, obj=obj)


def get_chat_history(chat_id:str):

    return get(table='chat_history',columns='id, role, content, context, score', where={'chat_id':chat_id})


def create_chat_history(chat_id:str, role:str, content:str, context:str=None):

    chat = get(table='chat', where={'id':chat_id})
    if len(chat) == 0:
        return []
    
    create(table='chat_history', 
           obj={'chat_id':chat_id, 
                'role':role, 
                'content':content,
                'context':context if context else ''})
    

def update_chat_history(chat_id:str, obj:dict):

    update('chat_history',obj_id=chat_id, obj=obj)


def get_vetores():
        
        if get_debug():
            return [f"Vector {x}" for x in range(10)]
        
        vector_store = load_model()
        metadatas = get_metadata(vector_store)
        return metadatas['sources']


def get_vectors(model_name:str=None):
    
    if model_name:
        projects = get_projects()
        project_vector = []
        l = []
        for p in projects:
            if p[1] == model_name:
                project_vector = get(table='project_vetor', columns='vector_id', where={'project_id':p[0]})
        
        for v in get(table='vector', columns='id, name, file, description'):
            if v[0] in [x[0] for x in project_vector]:
                l.append(v) 

        return l

    return get(table='vector', columns='id, name, file, description')


def create_vectors():
    
    path = 'tmp/vector_files'
    vectors = get_vectors()

    if not os.path.isdir(path):
        os.makedirs(path)

    for file in os.listdir(path):
        if not file.endswith('.json'):
            continue
        
        if file not in [x[2] for x in vectors]:
            create(table='vector', obj={'name':file, 'file':file})


def get_project_vectors(model_name:str=None):

    return get(table='project_vetor', columns='id, project_id, vector_id, updated_at, created_at')


def sinc_unique_project_vector(project_id, vector_id, enabled=True):

    res = get(table='project_vetor', columns='id, active', where={'project_id': project_id, 'vector_id': vector_id}, get_deleted=True)

    if len(res) == 0:
        create(table='project_vetor', 
               obj={'active': '1' if enabled else '0',
                    'project_id': project_id, 
                    'vector_id': vector_id})
    else:
        update(table='project_vetor', obj_id=res[0][0], obj={'active': '1' if enabled else '0'}, update_deleted=True)


def sinc_projects_vectors(model_name:str=None, vectors_names:list=None):
    
    vectors = get_vectors(model_name=model_name)
    project_info = get_projects(where={'name':model_name})
    for vector in vectors_names:
        if vector not in [x[2] for x in vectors]:

            vector_id = None
            for i, v in enumerate(vectors):
                if v[2] == vector:
                    vector_id = v[0]
                
            if vector_id is not None:
                create(
                    table='project_vetor',
                    obj={'project_id':project_info[0][0],
                        'vector_id':vector_id})
            
