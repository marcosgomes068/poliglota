"""
Módulo de Tradução de Texto
Este módulo fornece funcionalidades para traduzir textos de português para inglês
utilizando o Google Translator através da biblioteca deep_translator.
"""

import json
import os

from deep_translator import GoogleTranslator


def traduzir_json_google(input_json, output_json=None):
    """
    Traduz todas as frases do arquivo JSON de português para inglês usando GoogleTranslator.
    
    Args:
        input_json (str): Caminho do arquivo JSON de entrada
        output_json (str, optional): Caminho do arquivo JSON de saída. 
                                   Se None, adiciona '_traduzido' ao nome
    """
    with open(input_json, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    traduzidos = {}
    
    for chave, textos in dados.items():
        traduzidos[chave] = []
        
        for texto in textos:
            if texto.strip():
                try:
                    traduzido = GoogleTranslator(source="pt", target="en").translate(texto)
                except Exception as e:
                    traduzido = f"Erro na tradução: {e}"
            else:
                traduzido = ""
            
            traduzidos[chave].append(traduzido)
    
    # Define caminho de saída se não especificado
    if output_json is None:
        base, ext = os.path.splitext(input_json)
        output_json = f"{base}_traduzido{ext}"
    
    # Salva arquivo traduzido
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(traduzidos, f, ensure_ascii=False, indent=2)
    
    print(f"Tradução salva em: {output_json}")


if __name__ == "__main__":
    # Exemplo de uso
    traduzir_json_google("C:/Users/Gabriel/Documents/pydub/downloads/aud_recort/transcricoes.json")
