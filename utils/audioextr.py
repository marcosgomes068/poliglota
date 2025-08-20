"""
Módulo de Extração de Áudio
Este módulo fornece funcionalidades para extrair áudio de arquivos de vídeo
utilizando pydub para conversão de formatos.
"""

import os

from pydub import AudioSegment


def extrair_audio_mp4(input_path, output_path=None):
    """
    Extrai áudio de arquivo MP4 e converte para MP3.
    
    Args:
        input_path (str): Caminho do arquivo de vídeo de entrada
        output_path (str, optional): Caminho de saída para o áudio. 
                                   Se None, gera automaticamente baseado no input
        
    Returns:
        str: Caminho do arquivo de áudio extraído ou mensagem de erro
    """
    if not os.path.isfile(input_path):
        return f"Arquivo não encontrado: {input_path}"
    
    if output_path is None:
        base = os.path.splitext(os.path.basename(input_path))[0]
        pasta = os.path.dirname(input_path)
        output_path = os.path.join(pasta, f"{base}.mp3")
    
    try:
        audio = AudioSegment.from_file(input_path, format="mp4")
        audio.export(output_path, format="mp3")
        return output_path
    except Exception as e:
        return f"Erro ao extrair áudio: {e}"
