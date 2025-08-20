"""
Módulo de Manipulação de Áudio
Este módulo fornece funcionalidades para recortar áudio em intervalos específicos,
transcrever trechos, traduzir conteúdo e gerar áudios em inglês usando ElevenLabs.
"""

import os
import json
import importlib.util
import sys

from pydub import AudioSegment


def recortar_audio(audio_file, json_file):
    """
    Recorta áudio em trechos baseados em intervalos JSON e processa cada trecho.
    
    Args:
        audio_file (str): Caminho do arquivo de áudio de entrada
        json_file (str): Caminho do arquivo JSON com intervalos de tempo
    """
    # Cria pasta de saída para os recortes
    base_dir = os.path.dirname(json_file)
    pasta_saida = os.path.join(base_dir, 'aud_recort')
    os.makedirs(pasta_saida, exist_ok=True)

    # Carrega áudio e intervalos
    audio = AudioSegment.from_file(audio_file)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        intervals = json.load(f)

    # Salva áudio original como base
    caminho_base = os.path.join(pasta_saida, 'base.wav')
    audio.export(caminho_base, format='wav')
    print(f'Áudio original salvo: {caminho_base}')

    # Recorta e salva cada trecho
    for idx, intervalo in enumerate(intervals, 1):
        start_ms = int(intervalo['start'] * 1000)
        end_ms = int(intervalo['end'] * 1000)
        trecho = audio[start_ms:end_ms]
        nome_saida = f'recorte_{idx}.wav'
        caminho_saida = os.path.join(pasta_saida, nome_saida)
        trecho.export(caminho_saida, format='wav')
        print(f'Recorte salvo: {caminho_saida}')

    # Executa transcrição dos áudios recortados
    _executar_transcricao(pasta_saida)
    
    # Executa tradução das transcrições
    caminho_json = os.path.join(pasta_saida, 'transcricoes.json')
    _executar_traducao(caminho_json)
    
    # Gera áudios em inglês com ElevenLabs
    _executar_geracao_audio()

def _executar_transcricao(pasta_saida):
    """
    Executa transcrição dos áudios recortados.
    
    Args:
        pasta_saida (str): Pasta onde estão os recortes de áudio
    """
    caminho_transcribe = os.path.join(os.path.dirname(__file__), 'elabs', 'transcribe.py')
    spec = importlib.util.spec_from_file_location('transcribe', caminho_transcribe)
    transcribe = importlib.util.module_from_spec(spec)
    sys.modules['transcribe'] = transcribe
    spec.loader.exec_module(transcribe)
    
    resultados = transcribe.transcrever_audios_pasta()
    
    # Salva transcrições em JSON
    caminho_json = os.path.join(pasta_saida, 'transcricoes.json')
    transcricoes = {}
    
    for arquivo, transcricao in resultados.items():
        # Extrai apenas o texto dos resultados JSON
        textos = []
        for trecho in transcricao:
            try:
                obj = json.loads(trecho)
                textos.append(obj.get('text', ''))
            except Exception:
                textos.append(str(trecho))
        transcricoes[arquivo] = textos
    
    with open(caminho_json, 'w', encoding='utf-8') as f:
        json.dump(transcricoes, f, ensure_ascii=False, indent=2)
    
    print(f'Transcrições salvas em: {caminho_json}')

def _executar_traducao(caminho_json):
    """
    Executa tradução das transcrições para inglês.
    
    Args:
        caminho_json (str): Caminho do arquivo JSON com transcrições
    """
    caminho_traduct = os.path.join(os.path.dirname(__file__), 'elabs', 'traduct.py')
    spec_traduct = importlib.util.spec_from_file_location('traduct', caminho_traduct)
    traduct = importlib.util.module_from_spec(spec_traduct)
    sys.modules['traduct'] = traduct
    spec_traduct.loader.exec_module(traduct)
    
    traduct.traduzir_json_google(caminho_json)

def _executar_geracao_audio():
    """
    Executa geração de áudios em inglês usando ElevenLabs.
    """
    caminho_labs = os.path.join(os.path.dirname(__file__), 'elabs', 'labs.py')
    spec_labs = importlib.util.spec_from_file_location('labs', caminho_labs)
    labs = importlib.util.module_from_spec(spec_labs)
    sys.modules['labs'] = labs
    spec_labs.loader.exec_module(labs)
    
    # Usa voz padrão "EXAVITQu4vr4xnSDxMaL" (Rachel, narradora padrão da ElevenLabs)
    voice_id_padrao = "EXAVITQu4vr4xnSDxMaL"
    labs.gerar_audios_ingles_elevenlabs(voice_id=voice_id_padrao)

def man_aud(audio_file, json_file):
    """
    Função principal para manipulação de áudio.
    
    Args:
        audio_file (str): Caminho do arquivo de áudio
        json_file (str): Caminho do arquivo JSON com intervalos
    """
    recortar_audio(audio_file, json_file)


if __name__ == '__main__':
    man_aud()