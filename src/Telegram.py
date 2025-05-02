import telebot
import os
import datetime
import time
from dotenv import load_dotenv

from .Ask import ask_to_gemini, now
from .Config import config_load
from .Metadata import get_metadata
from .Load import load_model

load_dotenv()
config = config_load()
model_name = config["DEFAULT"]["The_model"]

path = f'tmp/{model_name}_responses/manual'
if not os.path.isdir(path):
    os.makedirs(path)

def telegram_run():

    bot = telebot.TeleBot(os.getenv("telegram_bot_api"), parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN


    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "Olá, se precisar de algo pode mandar email para alfredojrgasper@gmail.com")
        
    @bot.message_handler(commands=['vector'])
    def send_vectors(message):
        vector_store = load_model()
        metadatas = get_metadata(vector_store)
        sources = metadatas['sources']
        sources = '\n'.join(sources)
        bot.reply_to(message, f"Os arquivos que fazem parte deste vector_store são:\n{sources}")
    
    @bot.message_handler(func=lambda m: True)
    def echo_all(message):
        text = message.text
        response = ask_to_gemini(text)
        n = now()
        n_format = datetime.datetime.strptime(n,'%Y%m%d%H%M%S').strftime('%d/%m/%Y %H:%M:%S')        
        
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        username = message.from_user.username
        language_code = message.from_user.language_code

        user_info = f"ID -> {user_id}, First name -> {first_name}, Last name -> {last_name}, username -> {username}, language -> {language_code}"

        with open(f'{path}/question__telegram_{n}.md','w', encoding='utf-8') as f:
            f.write(f'User info : {user_info}\nQuestion : {text}\nDate : {n_format}\n\n<div style="padding:24px;font-size:12px">\nContext : \n\n{response["context"]}\n</div>\n\nResponse : \n\n{response["response"]}')

        bot.reply_to(message, response['context'])
        time.sleep(1)
        bot.reply_to(message, response['response'])
        
    bot.infinity_polling()