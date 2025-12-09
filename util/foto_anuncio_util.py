"""
Utilitário para gerenciamento de fotos de anúncios.

Este módulo fornece funções para:
- Obter caminhos de fotos de anúncios (padrão: {id:06d}.jpg)
- Salvar foto do upload
- Verificar se foto existe
"""

import base64
import binascii
import io
from pathlib import Path
from typing import Optional

from PIL import Image, UnidentifiedImageError

from util.logger_config import logger


# Configurações
PASTA_FOTO_DEFAULT = Path("static/img")
FOTO_DEFAULT_ANUNCIO = PASTA_FOTO_DEFAULT / "produto-sem-foto.jpg"
PASTA_FOTOS_ANUNCIOS = PASTA_FOTO_DEFAULT / "anuncios"
FORMATO_FOTO = "JPEG"
QUALIDADE_FOTO = 90
TAMANHO_MAX_ANUNCIO = 800  # pixels


def obter_caminho_foto_anuncio(id: int) -> str:
    """
    Retorna o caminho absoluto da foto do anúncio para uso em templates.

    Args:
        id: ID do anúncio

    Returns:
        String com caminho absoluto (ex: /static/img/anuncios/000001.jpg)
    """
    path = obter_path_absoluto_foto_anuncio(id)
    if path.exists():
        return f"/{PASTA_FOTOS_ANUNCIOS}/{id:06d}.jpg"
    # Retorna imagem padrão se não existe foto
    return f"/{FOTO_DEFAULT_ANUNCIO}"


def obter_path_absoluto_foto_anuncio(id: int) -> Path:
    """
    Retorna o Path absoluto do arquivo de foto do anúncio.

    Args:
        id: ID do anúncio

    Returns:
        Path do arquivo de foto
    """
    PASTA_FOTOS_ANUNCIOS.mkdir(parents=True, exist_ok=True)
    return PASTA_FOTOS_ANUNCIOS / f"{id:06d}.jpg"


def salvar_foto_anuncio(id: int, conteudo_base64: str) -> bool:
    """
    Salva a foto do anúncio enviada do frontend.

    Recebe imagem em base64, decodifica, processa e salva como JPG.

    Args:
        id: ID do anúncio
        conteudo_base64: String base64 da imagem (pode incluir prefixo data:image/...)

    Returns:
        True se salvou com sucesso, False caso contrário
    """
    try:
        # Remover prefixo data:image/...;base64, se existir
        if "," in conteudo_base64:
            conteudo_base64 = conteudo_base64.split(",", 1)[1]

        # Decodificar base64
        image_data = base64.b64decode(conteudo_base64)

        # Abrir imagem com Pillow
        imagem = Image.open(io.BytesIO(image_data))

        # Converter para RGB se necessário (remove canal alpha)
        if imagem.mode in ("RGBA", "LA", "P"):
            # Criar fundo branco
            fundo: Image.Image = Image.new("RGB", imagem.size, (255, 255, 255))
            if imagem.mode == "P":
                imagem = imagem.convert("RGBA")
            fundo.paste(imagem, mask=imagem.split()[-1] if "A" in imagem.mode else None)
            imagem = fundo
        elif imagem.mode != "RGB":
            imagem = imagem.convert("RGB")

        # Redimensionar se necessário (mantendo aspect ratio)
        if imagem.width > TAMANHO_MAX_ANUNCIO or imagem.height > TAMANHO_MAX_ANUNCIO:
            imagem.thumbnail((TAMANHO_MAX_ANUNCIO, TAMANHO_MAX_ANUNCIO), Image.Resampling.LANCZOS)
            logger.info(f"Imagem do anúncio redimensionada para {imagem.width}x{imagem.height}px")

        # Salvar como JPG
        destino = obter_path_absoluto_foto_anuncio(id)
        imagem.save(destino, format=FORMATO_FOTO, quality=QUALIDADE_FOTO, optimize=True)

        logger.info(f"Foto salva para anúncio ID: {id}")
        return True

    except (OSError, binascii.Error, UnidentifiedImageError, ValueError) as e:
        logger.error(f"Erro ao salvar foto para anúncio {id}: {e}")
        return False


def foto_anuncio_existe(id: int) -> bool:
    """
    Verifica se a foto do anúncio existe no filesystem.

    Args:
        id: ID do anúncio

    Returns:
        True se a foto existe, False caso contrário
    """
    return obter_path_absoluto_foto_anuncio(id).exists()


def excluir_foto_anuncio(id: int) -> bool:
    """
    Exclui a foto do anúncio do filesystem.

    Args:
        id: ID do anúncio

    Returns:
        True se excluiu com sucesso ou foto não existia, False em caso de erro
    """
    try:
        path = obter_path_absoluto_foto_anuncio(id)
        if path.exists():
            path.unlink()
            logger.info(f"Foto excluída para anúncio ID: {id}")
        return True
    except OSError as e:
        logger.error(f"Erro ao excluir foto do anúncio {id}: {e}")
        return False


def obter_tamanho_foto_anuncio(id: int) -> Optional[int]:
    """
    Retorna o tamanho da foto do anúncio em bytes.

    Args:
        id: ID do anúncio

    Returns:
        Tamanho em bytes ou None se foto não existe
    """
    path = obter_path_absoluto_foto_anuncio(id)
    return path.stat().st_size if path.exists() else None
