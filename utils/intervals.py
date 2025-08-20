"""
Módulo de Detecção de Intervalos de Fala
Este módulo fornece funcionalidades para detectar intervalos de fala em arquivos de áudio
utilizando o script de processamento Python externo.
"""

import subprocess
import sys


def mostrar_intervalos_fala(audio_path, formato='console', gap=0.5, min_duration=0.1):
    """
    Executa o script main.py para detectar e mostrar intervalos de fala.
    
    Args:
        audio_path (str): Caminho do arquivo de áudio
        formato (str): Formato de saída ('console', 'json', 'csv')
        gap (float): Threshold para mesclar intervalos próximos
        min_duration (float): Duração mínima do intervalo
        
    Returns:
        str: Saída do script de detecção ou string vazia se falhar
    """
    cmd = [sys.executable, r'C:\Users\Gabriel\Documents\pydub\utils\python\main.py', audio_path]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.stdout
    except Exception as e:
        print(f'Erro ao executar main.py: {e}', file=sys.stderr)
        return ""
