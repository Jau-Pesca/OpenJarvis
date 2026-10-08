"""Check Ollama and its installed inventory without downloading or loading models."""
import os
from pathlib import Path
import sys
import tomllib
from openjarvis.engine.ollama import OllamaEngine

ROOT = Path(__file__).resolve().parent


def prepare(root=ROOT, engine=None):
    with (root/'config.toml').open('rb') as source:
        main = tomllib.load(source)['intelligence']['default_model']
    temp = os.environ.get('OJ_TEMP_MODEL', 'qwen3.5:4b')
    engine = engine or OllamaEngine(host='http://127.0.0.1:11434', timeout=10)
    if not engine.health():
        raise RuntimeError('O Ollama não respondeu. Confira o serviço local.')
    installed = engine.list_models()
    missing = [model for model in dict.fromkeys([main, temp]) if model not in installed]
    if missing:
        print('Não instalados: ' + ', '.join(missing) + '. Use Downloads na interface.')
    print('Ollama disponível. Nenhum modelo carregado pela inicialização; carregamento somente ao enviar uma mensagem ou executar um passo.', flush=True)


if __name__ == '__main__':
    try:
        prepare()
    except Exception as error:
        print('Inicialização incompleta: ' + str(error), file=sys.stderr, flush=True)
        sys.exit(1)
