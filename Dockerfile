# Usa a imagem oficial do Python como imagem base
FROM python:3.12-slim
# Evita geração de .pyc e buffer no stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
# Instala dependências do projeto
# Garanta que seu projeto tenha um requirements.txt no diretório raiz
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# Copia o restante do código
COPY . .
# Porta interna onde o Uvicorn escutará
EXPOSE 8000
# Módulo ASGI do projeto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
