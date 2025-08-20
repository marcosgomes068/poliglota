"""
Pydub - Processador de Vídeos YouTube Shorts
Este script serve para baixar, processar e manipular vídeos do YouTube Shorts,
extraindo áudio, detectando intervalos de fala e gerando vídeos finais processados.
"""

import os
import re
import json
import subprocess
import importlib.util
import sys

from colorama import Fore, Style

from utils.download import download_shorts
from utils.audioextr import extrair_audio_mp4
from utils.induplique import audio_ja_existe
from utils.url import shorts_url_ok


class Shortstranslate:
    """
    Classe para processamento completo de vídeos YouTube Shorts.
    Gerencia download, extração de áudio, detecção de intervalos e geração de vídeo final.
    """

    def __init__(self, url):
        """
        Inicializa o processador com a URL do YouTube Shorts.
        
        Args:
            url (str): URL do vídeo YouTube Shorts
        """
        self.url = url

    def check(self):
        """
        Verifica se a URL é válida para download.
        
        Returns:
            bool: True se a URL for válida, False caso contrário
        """
        return shorts_url_ok(self.url)

    def get_video_path(self):
        """
        Gera o caminho do arquivo de vídeo baseado na URL.
        
        Returns:
            str: Caminho completo do arquivo de vídeo
        """
        match = re.search(r"shorts/([\w-]+)", self.url)
        video_id = match.group(1) if match else "video"
        return os.path.join("downloads", f"{video_id}.mp4")

    def download(self):
        """
        Baixa o vídeo do YouTube Shorts se ainda não existir.
        
        Returns:
            str: Caminho do arquivo baixado ou None se falhar
        """
        video_path = self.get_video_path()
        
        if os.path.exists(video_path):
            print(Fore.YELLOW + f"Arquivo já existe: {video_path}" + Style.RESET_ALL)
            return video_path
            
        if self.check():
            print("Baixando o vídeo...")
            resultado = download_shorts(self.url)
            print(resultado)
            return resultado
        else:
            print("URL inválida. Não é possível baixar.")
            return None

    def extcaud(self):
        """
        Extrai áudio do vídeo e converte para formato compatível com Vosk.
        
        Returns:
            str: Caminho do arquivo de áudio convertido
        """
        video_path = self.get_video_path()
        existe, audio_path = audio_ja_existe(video_path)
        
        if existe:
            print(f"Áudio já existe: {audio_path}")
        else:
            resultado = extrair_audio_mp4(video_path)
            print(resultado)
            audio_path = resultado
        
        # Converte para WAV mono 16kHz compatível com Vosk
        wav_path = os.path.splitext(audio_path)[0] + "_vosk.wav"
        subprocess.run([
            "ffmpeg", "-y", "-i", audio_path,
            "-ac", "1", "-ar", "16000", wav_path
        ], check=True)
        
        print(f"Áudio convertido para Vosk: {wav_path}")
        return wav_path

    def mostrar_intervalos(self):
        """
        Detecta intervalos de fala no áudio e salva em JSON.
        Executa o fluxo de processamento de áudio e vídeo.
        """
        from utils.intervals import mostrar_intervalos_fala
        
        video_path = self.get_video_path()
        _, audio_path_original = audio_ja_existe(video_path)
        audio_path = os.path.splitext(audio_path_original)[0] + "_vosk.wav"
        
        # Executa detecção de intervalos
        mostrar_intervalos_fala(audio_path)
        
        # Lê intervalos do arquivo gerado
        json_path = os.path.splitext(audio_path)[0] + "_intervals.json"
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                intervalos = json.load(f)
            print(f"Intervalos lidos de {json_path}: {intervalos}")
        else:
            print(f"Arquivo de intervalos não encontrado: {json_path}")
            intervalos = []
        
        self.salvar_intervalos_json(intervalos)

    def salvar_intervalos_json(self, intervalos):
        """
        Salva intervalos de fala em arquivo JSON e executa processamento.
        
        Args:
            intervalos (list): Lista de intervalos de fala detectados
        """
        match = re.search(r"shorts/([\w-]+)", self.url)
        video_id = match.group(1) if match else "video"
        json_path = os.path.join("downloads", f"{video_id}.json")
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(intervalos, f, ensure_ascii=False, indent=2)
        
        print(f"Intervalos salvos em: {json_path}")
        
        # Executa fluxo de recorte e processamento de áudio
        self._executar_man_aud(json_path)
        
        # Executa processamento de recortes e áudio
        self._executar_json_form()

    def _executar_man_aud(self, json_path):
        """
        Executa o módulo de manipulação de áudio.
        
        Args:
            json_path (str): Caminho do arquivo JSON com intervalos
        """
        caminho_man_aud = os.path.join(os.path.dirname(__file__), "man_aud", "man_aud.py")
        spec_man_aud = importlib.util.spec_from_file_location("man_aud", caminho_man_aud)
        man_aud = importlib.util.module_from_spec(spec_man_aud)
        sys.modules["man_aud"] = man_aud
        spec_man_aud.loader.exec_module(man_aud)
        
        audio_file = self.extcaud()
        man_aud.recortar_audio(audio_file, json_path)

    def _executar_json_form(self):
        """
        Executa o módulo de formatação JSON e preparação de ambiente.
        """
        caminho_json_form = os.path.join(os.path.dirname(__file__), 'man_vid', 'json_form.py')
        spec_json = importlib.util.spec_from_file_location('json_form', caminho_json_form)
        json_form_mod = importlib.util.module_from_spec(spec_json)
        spec_json.loader.exec_module(json_form_mod)
        
        json_form_mod.json_form()
        json_form_mod.preparar_ambiente()

    def gerar_video_final(self):
        """
        Gera vídeo final combinando vídeo MP4 com áudio processado.
        
        Returns:
            str: Caminho do vídeo final gerado
        """
        match = re.search(r"shorts/([\w-]+)", self.url)
        video_id = match.group(1) if match else "video"
        
        video_mp4 = os.path.join("downloads", f"{video_id}.mp4")
        audio_final_wav = os.path.join("man_vid", "base_finalizado.wav")
        output_video_avi = os.path.join("downloads", f"{video_id}_final.avi")
        
        if os.path.exists(video_mp4) and os.path.exists(audio_final_wav):
            cmd_mux = [
                "ffmpeg", "-y",
                "-i", video_mp4,
                "-i", audio_final_wav,
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:v", "copy",
                "-c:a", "pcm_s16le",
                "-shortest",
                output_video_avi
            ]
            subprocess.run(cmd_mux, check=True)
            print(f"Vídeo final gerado em: {output_video_avi}")
            return output_video_avi
        else:
            print("Arquivo de vídeo ou áudio final não encontrado para substituição.")
            return None


def main():
    """
    Função principal que executa o fluxo completo de processamento.
    """
    url = input("Digite a URL do YouTube Shorts: ")
    checker = Shortstranslate(url)
    
    checker.download()
    checker.extcaud()
    checker.mostrar_intervalos()
    checker.gerar_video_final()


if __name__ == "__main__":
    main()



