"""
Módulo de Transcrição de Áudio
Este módulo fornece funcionalidades para transcrever arquivos de áudio WAV
utilizando o modelo Vosk para reconhecimento de fala em português.
"""

import os
import wave

from vosk import Model, KaldiRecognizer


def transcrever_audios_pasta(model_path=None):
    """
    Transcreve todos os arquivos de áudio WAV da pasta downloads/aud_recort usando Vosk.
    
    Args:
        model_path (str, optional): Caminho para o modelo Vosk. 
                                   Se não informado, usa o modelo padrão da pasta.
        
    Returns:
        dict: Dicionário com nome do arquivo e lista de resultados de transcrição (JSON).
    """
    # Caminho fixo para a pasta de áudios
    pasta_audios = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        '..', '..', 'downloads', 'aud_recort'
    ))
    
    if model_path is None:
        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(pasta_atual, '..', 'vosk-model-small-pt-0.3')
        model_path = os.path.normpath(model_path)
    
    model = Model(model_path)
    resultados_por_arquivo = {}
    
    for nome_arquivo in os.listdir(pasta_audios):
        caminho_arquivo = os.path.join(pasta_audios, nome_arquivo)
        
        if not nome_arquivo.lower().endswith('.wav'):
            continue
        
        try:
            resultados_por_arquivo[nome_arquivo] = _transcrever_arquivo(
                caminho_arquivo, model
            )
        except Exception as e:
            resultados_por_arquivo[nome_arquivo] = [f"Erro: {str(e)}"]
    
    return resultados_por_arquivo


def _transcrever_arquivo(caminho_arquivo, model):
    """
    Transcreve um arquivo de áudio individual usando o modelo Vosk.
    
    Args:
        caminho_arquivo (str): Caminho completo do arquivo de áudio
        model (Model): Modelo Vosk carregado
        
    Returns:
        list: Lista de resultados de transcrição
    """
    with wave.open(caminho_arquivo, "rb") as wf:
        # Verifica formato do áudio
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [16000, 8000]:
            return ["Formato inválido"]
        
        rec = KaldiRecognizer(model, wf.getframerate())
        resultados = []
        
        # Processa frames do áudio
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            
            if rec.AcceptWaveform(data):
                res = rec.Result()
                resultados.append(res)
            else:
                res = rec.PartialResult()
        
        # Adiciona resultado final
        final = rec.FinalResult()
        resultados.append(final)
        
        return resultados

