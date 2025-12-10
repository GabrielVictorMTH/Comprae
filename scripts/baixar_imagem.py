#!/usr/bin/env python3
"""
Script auxiliar para baixar e salvar imagens geradas pelo Runware.
"""

import requests
from PIL import Image
from io import BytesIO
import os
import sys


def baixar_e_salvar_imagem(url: str, output_path: str, size: tuple = (256, 256)) -> bool:
    """
    Baixa uma imagem de uma URL e salva no caminho especificado.

    Args:
        url: URL da imagem a ser baixada
        output_path: Caminho onde a imagem será salva
        size: Tupla (largura, altura) para redimensionar a imagem

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        # Baixar a imagem
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Abrir a imagem
        img = Image.open(BytesIO(response.content))

        # Converter para RGB se necessário (para salvar como JPEG)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Redimensionar se necessário
        if img.size != size:
            img = img.resize(size, Image.Resampling.LANCZOS)

        # Criar diretório se não existir
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Salvar como JPEG
        img.save(output_path, 'JPEG', quality=90)

        return True

    except Exception as e:
        print(f"Erro ao baixar/salvar imagem: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python baixar_imagem.py <url> <output_path>")
        sys.exit(1)

    url = sys.argv[1]
    output_path = sys.argv[2]

    if baixar_e_salvar_imagem(url, output_path):
        print(f"Imagem salva em: {output_path}")
    else:
        sys.exit(1)
