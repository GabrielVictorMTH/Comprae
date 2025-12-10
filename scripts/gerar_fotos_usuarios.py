#!/usr/bin/env python3
"""
Script para gerar fotos fictícias para usuários usando Runware API.
Cria imagens 256x256px baseadas no gênero e idade do usuário.
"""

import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path
from random import choice
import requests
import json
from io import BytesIO
from PIL import Image

# Adicionar o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sql.usuario_sql import OBTER_TODOS
from util.config import DATABASE_PATH

# Configuração de Diretórios
FOTO_USUARIOS_DIR = Path(__file__).parent.parent / "static" / "img" / "usuarios"

# Configuração da API Runware
RUNWARE_API_KEY = os.getenv('RUNWARE_API_KEY', 'Q6SBxRqeiPTgCleUq2bjjjwvzE5vu1Az')
RUNWARE_API_URL = "https://api.runwayml.com/v1/generate"

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
        conn = sqlite3.connect(DATABASE_PATH)
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
    """
    try:
        print(f"🎨 Gerando foto para {nome_usuario} (ID: {usuario_id:06d})")
        print(f"   Prompt: {prompt}")

        # Preparar requisição para a API Runware
        headers = {
            'Authorization': f'Bearer {RUNWARE_API_KEY}',
            'Content-Type': 'application/json'
        }

        payload = {
            'prompt': prompt,
            'width': 256,
            'height': 256,
            'num_inference_steps': 30,
            'guidance_scale': 7.5,
            'num_images': 1
        }

        # Fazer requisição à API
        print(f"   Chamando API Runware...")
        response = requests.post(RUNWARE_API_URL, headers=headers, json=payload, timeout=120)

        if response.status_code != 200:
            print(f"   ⚠️  Erro da API ({response.status_code}): {response.text}")
            # Usar imagem placeholder em caso de erro
            imagem = gerar_imagem_placeholder(usuario_id, nome_usuario)
        else:
            # Processar resposta
            dados = response.json()

            if 'images' in dados and len(dados['images']) > 0:
                # Obter URL da imagem gerada
                image_url = dados['images'][0]['url']

                # Baixar a imagem
                print(f"   Baixando imagem...")
                img_response = requests.get(image_url, timeout=30)

                if img_response.status_code == 200:
                    # Converter para PIL Image
                    imagem = Image.open(BytesIO(img_response.content))

                    # Garantir que seja 256x256
                    if imagem.size != (256, 256):
                        imagem = imagem.resize((256, 256), Image.Resampling.LANCZOS)
                else:
                    print(f"   ⚠️  Erro ao baixar imagem: {img_response.status_code}")
                    imagem = gerar_imagem_placeholder(usuario_id, nome_usuario)
            else:
                print(f"   ⚠️  Resposta da API sem imagens")
                imagem = gerar_imagem_placeholder(usuario_id, nome_usuario)

        # Salvar a imagem
        caminho_foto = Path(FOTO_USUARIOS_DIR) / f"{usuario_id:06d}.jpg"
        imagem.save(caminho_foto, 'JPEG', quality=90)

        print(f"✅ Foto salva em: {caminho_foto}")
        return True

    except requests.exceptions.Timeout:
        print(f"❌ Timeout ao gerar foto para {nome_usuario}")
        return False
    except Exception as e:
        print(f"❌ Erro ao gerar foto para {nome_usuario}: {e}")
        # Criar imagem placeholder em caso de erro
        try:
            imagem = gerar_imagem_placeholder(usuario_id, nome_usuario)
            caminho_foto = Path(FOTO_USUARIOS_DIR) / f"{usuario_id:06d}.jpg"
            imagem.save(caminho_foto, 'JPEG', quality=90)
            print(f"   (Usando imagem placeholder)")
            return True
        except:
            return False

def gerar_imagem_placeholder(usuario_id: int, nome_usuario: str) -> Image.Image:
    """
    Gera uma imagem placeholder colorida como fallback.
    Usado quando a API Runware não está disponível ou falha.
    """
    from PIL import ImageDraw, ImageFont

    # Cores gradientes baseadas no ID
    cores_gradiente = [
        [(100, 150, 200), (150, 100, 200)],  # Azul-Roxo
        [(150, 100, 200), (200, 100, 150)],  # Roxo-Rosa
        [(200, 100, 150), (100, 200, 150)],  # Rosa-Verde
        [(100, 200, 150), (200, 150, 100)],  # Verde-Laranja
        [(200, 150, 100), (150, 200, 100)],  # Laranja-Lima
        [(150, 200, 100), (100, 150, 200)],  # Lima-Azul
    ]

    cores = cores_gradiente[usuario_id % len(cores_gradiente)]

    # Criar imagem com gradiente
    img = Image.new('RGB', (256, 256), cores[0])
    pixels = img.load()

    # Desenhar gradiente simples
    for y in range(256):
        r = int(cores[0][0] + (cores[1][0] - cores[0][0]) * (y / 256))
        g = int(cores[0][1] + (cores[1][1] - cores[0][1]) * (y / 256))
        b = int(cores[0][2] + (cores[1][2] - cores[0][2]) * (y / 256))

        for x in range(256):
            pixels[x, y] = (r, g, b)

    # Adicionar iniciais do nome
    draw = ImageDraw.Draw(img)
    iniciais = ''.join([palavra[0].upper() for palavra in nome_usuario.split() if palavra])

    try:
        # Tentar usar fonte grande
        fonte = ImageFont.load_default()
    except:
        fonte = ImageFont.load_default()

    # Desenhar iniciais no centro
    text_bbox = draw.textbbox((0, 0), iniciais, font=fonte)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    x = (256 - text_width) // 2
    y = (256 - text_height) // 2

    # Desenhar sombra
    draw.text((x + 2, y + 2), iniciais, fill=(0, 0, 0, 128), font=fonte)
    # Desenhar texto
    draw.text((x, y), iniciais, fill=(255, 255, 255), font=fonte)

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
