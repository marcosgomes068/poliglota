"""
Módulo de Verificação de Duplicatas
Este módulo fornece funcionalidades para verificar se arquivos de áudio
já existem antes de processar novamente.
"""

import os


def audio_ja_existe(video_path):
    """
    Verifica se o arquivo de áudio correspondente ao vídeo já existe.
    
    Args:
        video_path (str): Caminho do arquivo de vídeo
        
    Returns:
        tuple: (bool, str) - (existe, caminho_do_audio)
    """
    base = os.path.splitext(os.path.basename(video_path))[0]
    pasta = os.path.dirname(video_path)
    audio_path = os.path.join(pasta, f"{base}.mp3")
    return os.path.exists(audio_path), audio_path
