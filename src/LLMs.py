from langchain_ollama.llms import OllamaLLM

def ask_to_local_ollama_qwen3_06b(question, history) -> str:
    model = OllamaLLM(model='qwen3:0.6b')
    response = model.invoke(question)
    return {
        'response' : response
    }