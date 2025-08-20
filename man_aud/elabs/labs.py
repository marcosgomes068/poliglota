"""
Módulo de Geração de Áudio ElevenLabs
Este módulo fornece funcionalidades para gerar áudios em inglês usando a API ElevenLabs,
convertendo textos traduzidos em arquivos de áudio de alta qualidade.
"""

import json
import os
import re
import requests

from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")


def gerar_audios_ingles_elevenlabs(api_key=None, voice_id=None, modelo="eleven_multilingual_v2"):
    """
    Lê arquivo de traduções em inglês e gera áudios com ElevenLabs, sobrescrevendo os recortes.
    
    Args:
        api_key (str, optional): Chave da API ElevenLabs
        voice_id (str): ID da voz (narrador)
        modelo (str): Modelo de voz ElevenLabs
        
    Raises:
        ValueError: Se API key ou voice_id não forem fornecidos
    """
    caminho_json = r"C:\Users\Gabriel\Documents\pydub\downloads\aud_recort\transcricoes_traduzido.json"
    pasta_recortes = r"C:\Users\Gabriel\Documents\pydub\downloads\aud_recort"
    
    # Valida parâmetros obrigatórios
    if api_key is None:
        api_key = ELEVENLABS_API_KEY
    if not api_key:
        raise ValueError("API key da ElevenLabs não encontrada no .env!")
    if not voice_id:
        raise ValueError("Informe o voice_id de um narrador da ElevenLabs!")
    
    # Carrega dados de tradução
    dados = _carregar_dados_traducao(caminho_json)
    
    # Configura API ElevenLabs
    url_base = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Processa cada arquivo
    for nome_arquivo, textos in dados.items():
        _processar_arquivo_audio(
            nome_arquivo, textos, pasta_recortes, url_base, headers, modelo
        )


def _carregar_dados_traducao(caminho_json):
    """
    Carrega dados de tradução do arquivo JSON.
    
    Args:
        caminho_json (str): Caminho do arquivo JSON com traduções
        
    Returns:
        dict: Dados de tradução carregados
    """
    with open(caminho_json, "r", encoding="utf-8") as f:
        return json.load(f)


def _processar_arquivo_audio(nome_arquivo, textos, pasta_recortes, url_base, headers, modelo):
    """
    Processa um arquivo individual para geração de áudio.
    
    Args:
        nome_arquivo (str): Nome do arquivo a ser processado
        textos (list): Lista de textos traduzidos
        pasta_recortes (str): Pasta onde salvar o áudio gerado
        url_base (str): URL base da API ElevenLabs
        headers (dict): Headers da requisição HTTP
        modelo (str): Modelo de voz a ser usado
    """
    frases_ingles = _filtrar_frase_ingles(textos)
    texto = " ".join(frases_ingles)
    
    if not texto:
        print(f"Nenhuma frase em inglês válida para {nome_arquivo}, ignorando.")
        return
    
    # Prepara dados para API
    data = {
        "text": texto,
        "model_id": modelo,
        "output_format": "wav"
    }
    
    # Faz requisição para ElevenLabs
    response = requests.post(url_base, headers=headers, json=data)
    caminho_saida = os.path.join(pasta_recortes, nome_arquivo)
    
    if response.status_code == 200:
        _salvar_audio_gerado(response.content, caminho_saida)
    else:
        print(f"Erro ao gerar {nome_arquivo}: {response.status_code} - {response.text}")


def _filtrar_frase_ingles(frases):
    """
    Filtra frases que parecem ser traduções em inglês válidas.
    
    Args:
        frases (list): Lista de frases a serem filtradas
        
    Returns:
        list: Lista de frases em inglês válidas
    """
    resultado = []
    
    for frase in frases:
        frase = frase.strip()
        if not frase:
            continue
        
        # Ignora frases que começam com explicações ou desculpas
        if frase.lower().startswith(("i'm sorry", "here's", "let me know")):
            continue
        
        # Ignora frases em português (com acentos)
        if re.search(r'[áéíóúãõâêôç]', frase):
            continue
        
        resultado.append(frase)
    
    return resultado


def _salvar_audio_gerado(content, caminho_saida):
    """
    Salva áudio gerado pela API ElevenLabs.
    
    Args:
        content (bytes): Conteúdo binário do áudio
        caminho_saida (str): Caminho onde salvar o arquivo
    """
    with open(caminho_saida, "wb") as f:
        f.write(content)
    print(f"Áudio gerado e salvo: {caminho_saida}")
