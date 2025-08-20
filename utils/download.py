"""
Módulo de Download para YouTube Shorts
Este módulo fornece funcionalidades para baixar vídeos do YouTube Shorts
utilizando yt-dlp com configurações otimizadas.
"""

import os
import re

import yt_dlp

from utils.url import shorts_url_ok


def download_shorts(url, output_path="downloads"):
    """
    Baixa vídeo do YouTube Shorts para o diretório especificado.
    
    Args:
        url (str): URL do YouTube Shorts
        output_path (str): Diretório de saída para o arquivo baixado
        
    Returns:
        str: Caminho do arquivo baixado ou mensagem de erro
    """
    if not shorts_url_ok(url):
        return "URL inválida. Não é possível baixar."
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # Extrai o ID do vídeo da URL
    match = re.search(r"shorts/([\w-]+)", url)
    video_id = match.group(1) if match else "video"
    video_filename = f"{video_id}.mp4"
    
    ydl_opts = {
        'outtmpl': os.path.join(output_path, video_filename),
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': True,
        'noplaylist': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            filename = os.path.join(output_path, video_filename)
            print(f"Download concluído: {filename}")
            return filename
    except Exception as e:
        print(f"Erro ao baixar: {e}")
        return f"Erro: {e}"