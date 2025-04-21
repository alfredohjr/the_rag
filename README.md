## the_rag

Esse projeto é um estudo de como um RAG funciona, neste momento só funciona via linha de comando, um projeto relativamente pequeno mas totalmente funcional.

O projeto inicial já tem o livro "O principe" de Maquiavel compilado e pronto para ser usado.

# O RAG

O RAG(Open Retrieval-Augmented Generation) é uma abordagem de geração de texto que combina a recuperação de informações com a geração de linguagem natural. O objetivo é melhorar a qualidade e a relevância das respostas geradas por modelos de linguagem, utilizando informações externas(arquivos txt, pdf e etc) para enriquecer o contexto da geração.

## Instalação

Python : 3.10.7 ou superior.

Para instalar o projeto, você pode usar os seguintes procedimentos:

Crie um ambiente virtual (opcional, mas recomendado):

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

clone o repositório:

```bash
git clone https://github.com/alfredohjr/the_rag.git
```

```bash
pip install -r requirements.txt
```

para comecar a usar:

```bash
python main.py -o ask
```

## Uso

### Para criar a base de dados para consulta:

```bash
python main.py -n [nome do projeto]
```

depois disso é criado um diretório dentro da pasta `tmp` com o nome `[nome do projeto]_documents`, dentro dele você pode colocar os arquivos que deseja usar como base de consulta.

O procedimento aceita arquivos txt, pdf ou csv.

depois disso você deve definir o projeto como padrão, para isso utilize o seguinte comando:

```bash
python main.py -d [nome do projeto]
```

isso vai alterar o arquivo `config.ini`.

Obs.: Você pode alterar o arquivo `config.ini` manualmente.

### Para fazer as perguntas:

```bash
python main.py -o ask
```

Todas as os dados(pergunta, contexto e resposta) são salvos dentro da pasta `tmp` dentro do diretório `[nome do projeto]_responses`.

para sair do processo use : q, quit, exit ou de um enter.

### Criando um arquivo e fazendo as perguntas em lote.

Você também pode criar um arquivo com as perguntas e fazer a consulta em lote, para isso crie um arquivo `.txt` com as perguntas, uma por linha, e utilize o seguinte comando:

Obs.: as perguntas devem iniciar com \*.

```bash
python main.py -o ask -f [caminho e nome do arquivo]
```

## Configurações

Utilize o arquivo config.ini para configuração das bases de consulta.

## Extras

Dentro de cada chave do arquivo `config.ini` você pode adicionar a configuração:

### Linguagem dos documentos

```ini
language = pt
```

Com isso, você pode fazer a pergunta e antes do processo procurar pelos documentos, a pergunta vai ser traduzida para o idioma definido.
Isso é útil para fazer perguntas em inglês e buscar documentos em português, por exemplo.

### Adicionando um arquivo de template

```ini
prompt_template_file = [nome do arquivo]
```

Neste caso, coloque o arquivo de template dentro da pasta templates, copie o arquivo `templates/prompt_template.txt` e renomeie para o nome do arquivo que você deseja usar.
Ele deve ter as chaves `{question}` e `{context}` para funcionar corretamente.

### Adicionar comandos para a LLM

Adicione um `|` para passar um comando para a LLM, por exemplo:

```bash
sobre a justiça | faça uma frase sarcastica sobre o assunto
```

a segunda parte será ignorada pelo RAG e passada para a LLM, possibilitando fazer perguntas mais complexas ou comandos mais elaborados sem interferir na busca de informações.

### Como conseguir uma chave do Gemini

Vá no Google AI Studio e crie um projeto, depois vá em `API` e clique em `Get started`, depois clique em `Create API Key` e copie a chave gerada.
Depois disso, cole a chave no arquivo `.env` na chave `gemini_api_key`.

## Outros detalhes

Bibliotecas usadas: Langchain, Huggingface, Gemini, Pandas, Sentence Transformers e FAISS.
