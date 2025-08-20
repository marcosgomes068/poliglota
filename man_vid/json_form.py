"""
Módulo de Formatação JSON e Processamento de Áudio
Este módulo fornece funcionalidades para processar arquivos JSON de intervalos,
gerar estrutura de recortes e preparar ambiente para processamento de áudio.
"""

import json
import os

from pydub import AudioSegment
from pydub.utils import mediainfo


def json_form():
    """
    Processa arquivo de intervalos e gera JSON de recortes organizados.
    Busca por arquivo *_vosk_intervals.json e cria estrutura de recortes.
    """
    # Caminho absoluto para downloads
    downloads_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'downloads')

    # Procura arquivo *_vosk_intervals.json em downloads
    intervals_json = _encontrar_arquivo_intervalos(downloads_path)
    if not intervals_json:
        print('Arquivo *_vosk_intervals.json não encontrado.')
        return

    # Lê intervalos e processa recortes
    intervals = _ler_intervalos(intervals_json)
    recortes = _listar_recortes(downloads_path)
    resultado = _montar_estrutura_recortes(intervals, recortes, downloads_path)
    
    # Salva JSON final
    _salvar_json_recortes(resultado, downloads_path)


def preparar_ambiente():
    """
    Prepara ambiente de trabalho criando diretórios necessários
    e processando áudio base para colagem de recortes.
    
    Returns:
        str: Caminho do arquivo de áudio base processado
    """
    _criar_diretorios()
    
    # Busca arquivo de áudio em downloads
    downloads_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'downloads')
    audio_path = _encontrar_arquivo_audio(downloads_path)
    if not audio_path:
        print("Nenhum arquivo .wav encontrado na pasta downloads.")
        return None
    
    print(f"Usando arquivo de áudio: {audio_path}")
    audio = AudioSegment.from_file(audio_path)
    print(f"Duração do áudio: {len(audio) / 1000} segundos")

    # Cria áudio base para colagem
    audio_base = _criar_audio_base(audio)
    
    # Processa colagem de recortes
    _colar_recortes_no_audio(audio_base, downloads_path)
    
    return audio_base


def _encontrar_arquivo_intervalos(downloads_path):
    """
    Encontra arquivo de intervalos no diretório de downloads.
    
    Args:
        downloads_path (str): Caminho do diretório de downloads
        
    Returns:
        str: Caminho do arquivo de intervalos ou None
    """
    for item in os.listdir(downloads_path):
        if item.endswith('_vosk_intervals.json'):
            return os.path.join(downloads_path, item)
    return None


def _ler_intervalos(intervals_json):
    """
    Lê arquivo JSON de intervalos.
    
    Args:
        intervals_json (str): Caminho do arquivo JSON
        
    Returns:
        list: Lista de intervalos de tempo
    """
    with open(intervals_json, 'r', encoding='utf-8') as f:
        return json.load(f)


def _listar_recortes(downloads_path):
    """
    Lista arquivos de recortes na pasta aud_recort.
    
    Args:
        downloads_path (str): Caminho do diretório de downloads
        
    Returns:
        list: Lista ordenada de arquivos de recortes
    """
    aud_recort_path = os.path.join(downloads_path, 'aud_recort')
    recortes = [f for f in os.listdir(aud_recort_path) 
                if f.startswith('recorte_') and f.endswith('.wav')]
    recortes.sort()  # Garante ordem recorte_1, recorte_2, ...
    return recortes


def _montar_estrutura_recortes(intervals, recortes, downloads_path):
    """
    Monta estrutura final de recortes combinando intervalos e arquivos.
    
    Args:
        intervals (list): Lista de intervalos de tempo
        recortes (list): Lista de arquivos de recortes
        downloads_path (str): Caminho do diretório de downloads
        
    Returns:
        list: Estrutura de recortes organizada
    """
    aud_recort_path = os.path.join(downloads_path, 'aud_recort')
    resultado = []
    
    for idx, intervalo in enumerate(intervals):
        # Garante que só pega o número de recortes disponíveis
        if idx < len(recortes):
            recorte_abspath = os.path.join(aud_recort_path, recortes[idx])
            resultado.append({
                'start': intervalo['start'],
                'end': intervalo['end'],
                'file': recorte_abspath
            })
    
    return resultado


def _salvar_json_recortes(resultado, downloads_path):
    """
    Salva JSON final de recortes.
    
    Args:
        resultado (list): Estrutura de recortes organizada
        downloads_path (str): Caminho do diretório de downloads
    """
    output_path = os.path.join(downloads_path, 'recortes.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    print(f'JSON de recortes gerado em {output_path}')


def _criar_diretorios():
    """
    Cria diretórios necessários para o processamento.
    """
    os.makedirs('downloads', exist_ok=True)
    os.makedirs('spleeter_temp', exist_ok=True)
    print("Ambiente preparado.")


def _encontrar_arquivo_audio(downloads_path):
    """
    Encontra primeiro arquivo .wav no diretório de downloads.
    
    Args:
        downloads_path (str): Caminho do diretório de downloads
        
    Returns:
        str: Caminho do arquivo de áudio ou None
    """
    wav_files = [f for f in os.listdir(downloads_path) 
                 if f.lower().endswith('.wav')]
    if not wav_files:
        return None
    return os.path.join(downloads_path, wav_files[0])


def _criar_audio_base(audio):
    """
    Cria arquivo de áudio base para colagem de recortes.
    
    Args:
        audio (AudioSegment): Áudio de referência para duração
        
    Returns:
        str: Caminho do arquivo de áudio base criado
    """
    ambiente_path = os.path.join('man_vid', 'ambiente.wav')
    base_path = os.path.join('man_vid', 'base.wav')
    os.makedirs('man_vid', exist_ok=True)
    
    if os.path.exists(ambiente_path):
        ambiente_audio = AudioSegment.from_file(ambiente_path)
        ambiente_audio = ambiente_audio[:len(audio)]  # Garante mesma duração
        ambiente_audio.export(base_path, format="wav")
        print(f"Cópia criada: {base_path}")
    else:
        # Se ambiente.wav não existe, usa o .wav encontrado em downloads
        print(f"Arquivo ambiente.wav não encontrado em {ambiente_path}, usando o .wav encontrado em downloads.")
        ambiente_audio = audio[:len(audio)]
        ambiente_audio.export(base_path, format="wav")
        print(f"Cópia criada: {base_path}")
    
    return base_path


def _colar_recortes_no_audio(audio_base, downloads_path):
    """
    Cola recortes no áudio base conforme informações do JSON.
    
    Args:
        audio_base (str): Caminho do arquivo de áudio base
        downloads_path (str): Caminho do diretório de downloads
    """
    recortes_json_path = os.path.join(downloads_path, 'recortes.json')
    
    if not audio_base or not os.path.exists(recortes_json_path):
        print('Não foi possível colar recortes: base.wav ou recortes.json não encontrado.')
        return
    
    with open(recortes_json_path, 'r', encoding='utf-8') as f:
        recortes_info = json.load(f)
    
    base_audio = AudioSegment.from_file(audio_base)
    
    # Cola cada recorte no tempo especificado
    for recorte in recortes_info:
        start_ms = int(recorte['start'] * 1000)
        end_ms = int(recorte['end'] * 1000)
        recorte_audio = AudioSegment.from_file(recorte['file'])
        # Substitui o trecho no áudio base pelo recorte
        base_audio = base_audio[:start_ms] + recorte_audio + base_audio[end_ms:]
    
    # Ajusta duração final e salva resultado
    _ajustar_duracao_final(base_audio, downloads_path)


def _ajustar_duracao_final(base_audio, downloads_path):
    """
    Ajusta duração final do áudio e salva resultado.
    
    Args:
        base_audio (AudioSegment): Áudio processado com recortes
        downloads_path (str): Caminho do diretório de downloads
    """
    final_path = os.path.join('man_vid', 'base_finalizado.wav')
    
    # Busca arquivo MP3 original para referência de duração
    mp3_files = [f for f in os.listdir(downloads_path) 
                 if f.lower().endswith('.mp3')]
    
    if mp3_files:
        mp3_path = os.path.join(downloads_path, mp3_files[0])
        info = mediainfo(mp3_path)
        duracao_ms = int(float(info['duration']) * 1000)
        base_audio = base_audio[:duracao_ms]
        print(f'Áudio final cortado para {duracao_ms/1000:.2f} segundos (igual ao original mp3)')
    
    base_audio.export(final_path, format='wav')
    print(f'Recortes colados conforme JSON em {final_path}')


if __name__ == '__main__':
    json_form()