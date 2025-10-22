import re
from typing import Tuple

def validar_forca_senha(senha: str) -> Tuple[bool, str]:
    """
    Valida força da senha
    Retorna: (é_válida, mensagem)
    """
    if len(senha) < 8:
        return False, "Senha deve ter no mínimo 8 caracteres"

    if not re.search(r"[A-Z]", senha):
        return False, "Senha deve conter pelo menos uma letra maiúscula"

    if not re.search(r"[a-z]", senha):
        return False, "Senha deve conter pelo menos uma letra minúscula"

    if not re.search(r"\d", senha):
        return False, "Senha deve conter pelo menos um número"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):
        return False, "Senha deve conter pelo menos um caractere especial"

    return True, "Senha válida"

def calcular_nivel_senha(senha: str) -> str:
    """Retorna: fraca, média, forte"""
    pontos = 0

    if len(senha) >= 8: pontos += 1
    if len(senha) >= 12: pontos += 1
    if re.search(r"[A-Z]", senha): pontos += 1
    if re.search(r"[a-z]", senha): pontos += 1
    if re.search(r"\d", senha): pontos += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha): pontos += 1

    if pontos <= 2: return "fraca"
    if pontos <= 4: return "média"
    return "forte"
