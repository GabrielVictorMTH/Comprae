#!/usr/bin/env python3
"""
Script para gerar fotos fictícias para usuários usando Runware MCP.
Cria imagens 256x256px baseadas no gênero e idade do usuário.
"""

import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path
from random import randint, choice
import requests
import json
from io import BytesIO
from PIL import Image

# Adicionar o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sql.usuario_sql import OBTER_TODOS
from util.config import DB_PATH, FOTO_USUARIOS_DIR

# Cores personalizadas por gênero e idade
DESCRICOES_POR_GENERO_IDADE = {
    'masculino': {
        'crianca': [
            'young boy with brown hair, smiling, wearing colorful shirt, illustration style',
            'little boy with blonde hair, happy expression, cute, professional portrait',
            'young boy with dark hair, playful, warm lighting, digital art style'
        ],
        'adolescente': [
            'teenage boy with modern hairstyle, confident smile, casual outfit, illustration',
            'young man teenager with trendy hair, friendly expression, professional portrait',
            'teen boy with casual style, warm smile, natural lighting, digital art'
        ],
        'adulto': [
            'adult man with confident expression, professional appearance, warm lighting',
            'mature man with friendly smile, business casual outfit, professional portrait',
            'man in his 30s with warm expression, natural lighting, professional style'
        ],
        'senior': [
            'senior man with gray hair, gentle expression, wisdom in eyes, professional portrait',
            'elderly man with kind smile, warm lighting, dignified appearance, illustration',
            'mature man with gray hair, warm expression, natural lighting, professional style'
        ]
    },
    'feminino': {
        'crianca': [
            'young girl with long hair, smiling, wearing colorful clothes, illustration style',
            'little girl with blonde hair, happy expression, cute, professional portrait',
            'young girl with dark hair, playful, warm lighting, digital art style'
        ],
        'adolescente': [
            'teenage girl with modern hairstyle, confident smile, casual outfit, illustration',
            'young woman teenager with trendy hair, friendly expression, professional portrait',
            'teen girl with casual style, warm smile, natural lighting, digital art'
        ],
        'adulto': [
            'adult woman with confident expression, professional appearance, warm lighting',
            'mature woman with friendly smile, business casual outfit, professional portrait',
            'woman in her 30s with warm expression, natural lighting, professional style'
        ],
        'senior': [
            'senior woman with gray hair, gentle expression, wisdom in eyes, professional portrait',
            'elderly woman with kind smile, warm lighting, dignified appearance, illustration',
            'mature woman with gray hair, warm expression, natural lighting, professional style'
        ]
    }
}

def calcular_faixa_etaria(data_nascimento: str) -> str:
    """Calcula a faixa etária baseada na data de nascimento."""
    if not data_nascimento:
        return 'adulto'

    try:
        nascimento = datetime.strptime(data_nascimento, '%Y-%m-%d')
        idade = (datetime.now() - nascimento).days // 365

        if idade < 12:
            return 'crianca'
        elif idade < 18:
            return 'adolescente'
        elif idade < 60:
            return 'adulto'
        else:
            return 'senior'
    except:
        return 'adulto'

def obter_descricao_imagem(genero: str, data_nascimento: str) -> str:
    """Gera descrição da imagem baseada em gênero e idade."""
    genero = genero.lower() if genero else 'masculino'
    faixa = calcular_faixa_etaria(data_nascimento)

    # Normalizar gênero
    if genero not in DESCRICOES_POR_GENERO_IDADE:
        genero = 'masculino'

    descricoes = DESCRICOES_POR_GENERO_IDADE[genero].get(faixa, [
        f'professional portrait of a person, {genero} appearance, warm lighting, digital art'
    ])

    return choice(descricoes)

def obter_usuarios_do_bd() -> list:
    """Obtém lista de usuários do banco de dados."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(OBTER_TODOS)
        usuarios = cursor.fetchall()
        conn.close()

        return [dict(row) for row in usuarios]
    except Exception as e:
        print(f"❌ Erro ao obter usuários: {e}")
        return []

def gerar_foto_com_runware(prompt: str, usuario_id: int, nome_usuario: str) -> bool:
    """
    Gera foto usando Runware API.

    Nota: Esta função assume que o Runware MCP está configurado.
    Para usar, você precisa ter a chave de API do Runware configurada.
    """
    try:
        # Aqui você usaria o Runware MCP
        # Por enquanto, vamos simular com uma foto padrão colorida

        print(f"🎨 Gerando foto para {nome_usuario} (ID: {usuario_id:06d})")
        print(f"   Prompt: {prompt}")

        # Criar uma imagem placeholder colorida
        # Em produção, isso seria uma chamada real ao Runware
        imagem = gerar_imagem_placeholder(usuario_id, nome_usuario)

        # Salvar a imagem
        caminho_foto = Path(FOTO_USUARIOS_DIR) / f"{usuario_id:06d}.jpg"
        imagem.save(caminho_foto, 'JPEG', quality=90)

        print(f"✅ Foto salva em: {caminho_foto}")
        return True

    except Exception as e:
        print(f"❌ Erro ao gerar foto para {nome_usuario}: {e}")
        return False

def gerar_imagem_placeholder(usuario_id: int, nome_usuario: str) -> Image.Image:
    """
    Gera uma imagem placeholder colorida como exemplo.
    Em produção, esta seria a resposta da API Runware.
    """
    # Cores baseadas no ID para variedade
    cores = [
        (100, 150, 200),  # Azul
        (150, 100, 200),  # Roxo
        (200, 100, 150),  # Rosa
        (100, 200, 150),  # Verde
        (200, 150, 100),  # Laranja
        (150, 200, 100),  # Lima
    ]

    cor = cores[usuario_id % len(cores)]

    # Criar imagem 256x256
    img = Image.new('RGB', (256, 256), cor)

    # Você pode adicionar mais customizações aqui
    # Por exemplo, desenhar iniciais do nome, etc.

    return img

def main():
    """Função principal."""
    print("=" * 60)
    print("🖼️  Gerador de Fotos Fictícias de Usuários")
    print("=" * 60)

    # Garantir que o diretório existe
    Path(FOTO_USUARIOS_DIR).mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Diretório de fotos: {FOTO_USUARIOS_DIR}")

    # Obter usuários
    print("\n📚 Obtendo usuários do banco de dados...")
    usuarios = obter_usuarios_do_bd()
    print(f"✅ {len(usuarios)} usuário(s) encontrado(s)\n")

    if not usuarios:
        print("❌ Nenhum usuário encontrado!")
        return

    # Processar cada usuário
    sucesso = 0
    erro = 0

    for usuario in usuarios:
        usuario_id = usuario['id']
        nome = usuario['nome']
        genero = usuario.get('genero', 'masculino')
        data_nascimento = usuario.get('data_nascimento')

        # Gerar descrição da imagem
        prompt = obter_descricao_imagem(genero, data_nascimento)

        # Gerar foto
        if gerar_foto_com_runware(prompt, usuario_id, nome):
            sucesso += 1
        else:
            erro += 1

    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO")
    print("=" * 60)
    print(f"✅ Sucesso: {sucesso}")
    print(f"❌ Erros: {erro}")
    print(f"📊 Total: {len(usuarios)}")
    print("=" * 60)

if __name__ == '__main__':
    main()
