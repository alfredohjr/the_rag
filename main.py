import argparse
import os

from src import manual_ask, auto_task, save_model, config_load

if __name__ == "__main__":

    config = config_load()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--default',type=str, default=None)
    parser.add_argument('-f','--file',type=str, default=None)
    parser.add_argument('-n','--new',type=str, default=None)
    parser.add_argument('-o','--option',type=str,default=None)
    parser.add_argument('-s','--save_option',type=str,default='append')

    args = parser.parse_args()

    if args.new is not None:
        name = args.new
        path_documents = f'tmp/{name}_documents'
        if not os.path.isdir(path_documents):
            os.makedirs(path_documents)

        config[name] = {}
        config[name]['tmp'] = 'tmp_dir'

        with open('config.ini','w') as f:
            config.write(f)
            
    if args.default is not None:
        default = args.default
        if default not in config:
            raise Exception(f"Defina a chave [{default}] ou use o comando main.py --new [nome] para criar automaticamente")

        config["DEFAULT"]["The_model"] = default

        with open('config.ini','w') as f:
            config.write(f)

    if args.option == 'ask':
        if args.file is None:
            manual_ask()
        else:
            auto_task(args.file)
    elif args.option == 'save':
        save_model(args.save_option)