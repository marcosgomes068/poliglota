"""
Módulo Principal de Manipulação de Vídeo
Este módulo fornece o fluxo principal simplificado para processamento de vídeo,
chamando as funcionalidades do json_form.py para formatação e preparação de ambiente.
"""

import importlib.util
import os


def main():
    """
    Função principal que executa o fluxo de processamento de vídeo.
    Carrega e executa o módulo json_form para processar intervalos e preparar ambiente.
    """
    caminho_json_form = os.path.join(os.path.dirname(__file__), 'json_form.py')
    spec_json = importlib.util.spec_from_file_location('json_form', caminho_json_form)
    json_form_mod = importlib.util.module_from_spec(spec_json)
    spec_json.loader.exec_module(json_form_mod)
    
    # Executa formatação JSON e preparação de ambiente
    json_form_mod.json_form()
    json_form_mod.preparar_ambiente()


if __name__ == "__main__":
    main()
