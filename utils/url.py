"""
Módulo de Validação de URLs
Este módulo fornece funcionalidades para validar URLs do YouTube Shorts
e fornecer feedback visual sobre a validade das URLs.
"""

import re

from colorama import init, Fore

# Inicializa colorama para reset automático de cores
init(autoreset=True)


def shorts_url_ok(url):
    """
    Valida se a URL fornecida é um YouTube Shorts válido.
    
    Args:
        url (str): URL a ser validada
        
    Returns:
        bool: True se a URL for válida, False caso contrário
    """
    shorts_pattern = r"^(https?://)?(www\.)?youtube\.com/shorts/[\w-]+/?$"
    
    if re.match(shorts_pattern, url):
        print(Fore.GREEN + f"URL válida: {url}")
        return True
    else:
        print(Fore.RED + f"URL inválida: {url}")
        return False
