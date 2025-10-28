# Sistema de Chat Privado 1-para-1 com Widget Retrátil (Estilo WhatsApp)

## 📋 Visão Geral

Este documento fornece um guia completo e detalhado para implementar um sistema de **chat privado em tempo real** no DefaultWebApp usando **Server-Sent Events (SSE)** para recebimento de mensagens e **HTTP POST** para envio.

### Características Principais

- 💬 **Chats Privados 1-para-1**: Conversas entre exatamente 2 usuários
- 📱 **Widget Retrátil**: Interface flutuante no canto inferior direito (estilo WhatsApp Web)
- 🔄 **Tempo Real**: Mensagens instantâneas via SSE
- 🔍 **Busca Inteligente**: Autocomplete para encontrar usuários por ID, nome ou email
- ✨ **Formatação de Texto**: Suporte a **negrito**, *itálico* e ***ambos***
- 📊 **Lista de Conversas**: Mostra últimas 12 conversas com paginação
- 🔔 **Notificações**: Badge com contador de mensagens não lidas
- ⌨️ **Atalhos**: Enter para enviar, Shift+Enter para quebra de linha

### Por que SSE + HTTP POST?

**Server-Sent Events (SSE)** é uma tecnologia nativa do navegador ideal para o DefaultWebApp:

- ✅ **Simplicidade**: Usa HTTP padrão, integração direta com FastAPI
- ✅ **Compatibilidade**: 98% de suporte em navegadores, funciona com firewalls corporativos
- ✅ **Arquitetura HTTP**: Funciona perfeitamente com session-based auth existente
- ✅ **Reconexão Automática**: EventSource reconecta automaticamente se cair
- ✅ **Debugging**: Mensagens visíveis no Network tab do DevTools
- ✅ **Infraestrutura**: Não requer configuração especial de load balancer

**Limitação**: SSE é unidirecional (servidor → cliente). Por isso, usamos **HTTP POST** padrão para enviar mensagens (cliente → servidor). Esta combinação é perfeita para chat.

### Arquitetura de Alto Nível

```
┌───────────────────────────────────────────────────────────────────┐
│                   FRONTEND (Widget Retrátil)                       │
│                                                                    │
│  Estado Retraído:        Estado Expandido:                        │
│  ┌─────────┐            ┌─────────────────────────────────┐      │
│  │ 💬 [5]  │ ──────────>│ Lista │ Chat Ativo              │      │
│  └─────────┘            │ (30%) │ (70%)                   │      │
│                         │       │                         │      │
│                         │ João  │ ┌─────────────┐         │      │
│                         │ Maria │ │ Mensagens   │         │      │
│                         │ Pedro │ └─────────────┘         │      │
│                         │       │ [Digite...] [Enviar]    │      │
│                         └─────────────────────────────────┘      │
│                                                                    │
│  ┌──────────────┐              ┌─────────────────────────┐       │
│  │ EventSource  │              │   fetch() POST          │       │
│  │ /chat/stream │◄─────────────┤   /chat/enviar          │       │
│  └──────┬───────┘              └───────────┬─────────────┘       │
└─────────┼────────────────────────────────────┼────────────────────┘
          │                                     │
          │ SSE (Todas as salas do usuário)     │ HTTP POST
          │                                     │
          ▼                                     ▼
┌───────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                             │
│                                                                    │
│  ┌──────────────────┐              ┌─────────────────────────┐   │
│  │  GET /stream     │              │   POST /enviar          │   │
│  │  (multi-sala)    │              │   (sala específica)      │   │
│  └────────┬─────────┘              └───────────┬─────────────┘   │
│           │                                     │                 │
│           ▼                                     ▼                 │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │         ChatManager (util/chat_manager.py)                │    │
│  │  - Gerencia conexões SSE por usuário (não por sala)      │    │
│  │  - Notifica mensagens de TODAS as salas do usuário       │    │
│  │  - broadcast_para_sala(sala_id, msg) notifica 2 users    │    │
│  └────────────────────┬──────────────────────────────────────┘    │
│                       │                                           │
│                       ▼                                           │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │         Repositories (repo/chat_*_repo.py)                │    │
│  │  - chat_sala: Gerencia salas 1-para-1                    │    │
│  │  - chat_participante: Relaciona usuários com salas       │    │
│  │  - chat_mensagem: CRUD de mensagens                      │    │
│  └────────────────────┬──────────────────────────────────────┘    │
│                       │                                           │
│                       ▼                                           │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                SQLite Database                            │    │
│  │  - chat_sala (id, criada_em, ultima_atividade)           │    │
│  │  - chat_participante (sala_id, usuario_id, ultima_leitura)│   │
│  │  - chat_mensagem (sala_id, usuario_id, mensagem, ...)    │    │
│  └──────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
```

### Fluxo de Criação de Sala e Envio de Mensagem

**1. Usuário busca outro usuário (Autocomplete)**
```
Usuário digita "joão" → GET /chat/buscar-usuarios?q=joão
→ Backend retorna [{id: 5, nome: "João Silva", email: "joao@..."}]
→ Frontend exibe sugestões
→ Usuário seleciona João (ID 5)
```

**2. Sistema cria/abre sala automaticamente**
```
Frontend envia POST /chat/iniciar {outro_usuario_id: 5}
→ Backend calcula sala_id = f"{min(user_logado_id, 5)}_{max(user_logado_id, 5)}"
→ Exemplo: usuário logado é 3 → sala_id = "3_5"
→ Verifica se sala "3_5" existe, senão cria
→ Retorna sala_id e últimas mensagens
→ Frontend carrega conversa
```

**3. SSE conecta e aguarda mensagens**
```
EventSource conecta em GET /chat/stream
→ Backend registra conexão para o usuário (não para sala específica)
→ Aguarda mensagens de QUALQUER sala que o usuário participa
→ Quando mensagem chega, envia com sala_id no JSON
→ Frontend roteia para conversa correta
```

**4. Usuário envia mensagem**
```
Usuário digita "Olá!" e pressiona Enter
→ POST /chat/enviar {sala_id: "3_5", mensagem: "Olá!"}
→ Backend valida, salva no banco
→ ChatManager.broadcast_para_sala("3_5", mensagem)
→ Notifica usuário 3 E usuário 5 via SSE
→ Ambos recebem mensagem em tempo real
```

### ID de Sala Determinístico

Para garantir que 2 usuários sempre usem a mesma sala, o `sala_id` é gerado deterministicamente:

```python
def gerar_sala_id(usuario1_id: int, usuario2_id: int) -> str:
    """
    Gera ID único e determinístico para sala entre 2 usuários.

    Exemplos:
    - gerar_sala_id(3, 7) → "3_7"
    - gerar_sala_id(7, 3) → "3_7"  (mesma sala!)
    - gerar_sala_id(1, 100) → "1_100"

    Returns:
        String no formato "menor_id_maior_id"
    """
    ids_ordenados = sorted([usuario1_id, usuario2_id])
    return f"{ids_ordenados[0]}_{ids_ordenados[1]}"
```

**Por que este formato?**
- ✅ **Determinístico**: Mesma combinação de usuários = mesmo ID
- ✅ **Único**: Garante que não haja salas duplicadas
- ✅ **Simples**: Não precisa consultar banco para verificar existência
- ✅ **Legível**: Fácil de debugar (sala "3_7" é entre usuários 3 e 7)

---

## 🗄️ Camada 1: Banco de Dados

### Estrutura de Tabelas

O sistema usa **3 tabelas** para gerenciar chats privados:

1. **`chat_sala`**: Metadados das salas de chat
2. **`chat_participante`**: Relaciona usuários com salas (sempre 2 usuários)
3. **`chat_mensagem`**: Mensagens enviadas nas salas

### SQL Schema

#### Arquivo `sql/chat_sala_sql.py`

```python
"""
Queries SQL para gerenciamento de salas de chat.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS chat_sala (
    id TEXT PRIMARY KEY,  -- Formato: "menor_id_maior_id" (ex: "3_7")
    criada_em TIMESTAMP NOT NULL,
    ultima_atividade TIMESTAMP NOT NULL
)
"""

CRIAR_INDICES = """
CREATE INDEX IF NOT EXISTS idx_chat_sala_ultima_atividade
ON chat_sala(ultima_atividade DESC);
"""

INSERIR = """
INSERT INTO chat_sala (id, criada_em, ultima_atividade)
VALUES (?, ?, ?)
"""

OBTER_POR_ID = """
SELECT
    id,
    criada_em as "criada_em [timestamp]",
    ultima_atividade as "ultima_atividade [timestamp]"
FROM chat_sala
WHERE id = ?
"""

ATUALIZAR_ULTIMA_ATIVIDADE = """
UPDATE chat_sala
SET ultima_atividade = ?
WHERE id = ?
"""

EXCLUIR = """
DELETE FROM chat_sala WHERE id = ?
"""
```

#### Arquivo `sql/chat_participante_sql.py`

```python
"""
Queries SQL para participantes de salas de chat.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS chat_participante (
    sala_id TEXT NOT NULL,
    usuario_id INTEGER NOT NULL,
    ultima_leitura TIMESTAMP,

    PRIMARY KEY (sala_id, usuario_id),
    FOREIGN KEY (sala_id) REFERENCES chat_sala(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
)
"""

CRIAR_INDICES = """
CREATE INDEX IF NOT EXISTS idx_chat_participante_usuario
ON chat_participante(usuario_id);

CREATE INDEX IF NOT EXISTS idx_chat_participante_sala
ON chat_participante(sala_id);
"""

INSERIR = """
INSERT INTO chat_participante (sala_id, usuario_id, ultima_leitura)
VALUES (?, ?, ?)
"""

OBTER_PARTICIPANTES_SALA = """
SELECT
    cp.sala_id,
    cp.usuario_id,
    cp.ultima_leitura as "ultima_leitura [timestamp]",
    u.nome as usuario_nome,
    u.email as usuario_email
FROM chat_participante cp
INNER JOIN usuario u ON cp.usuario_id = u.id
WHERE cp.sala_id = ?
"""

OBTER_SALAS_USUARIO = """
SELECT DISTINCT
    cp.sala_id,
    cs.criada_em as "criada_em [timestamp]",
    cs.ultima_atividade as "ultima_atividade [timestamp]",
    cp.ultima_leitura as "ultima_leitura [timestamp]"
FROM chat_participante cp
INNER JOIN chat_sala cs ON cp.sala_id = cs.id
WHERE cp.usuario_id = ?
ORDER BY cs.ultima_atividade DESC
LIMIT ? OFFSET ?
"""

ATUALIZAR_ULTIMA_LEITURA = """
UPDATE chat_participante
SET ultima_leitura = ?
WHERE sala_id = ? AND usuario_id = ?
"""

VERIFICAR_USUARIO_NA_SALA = """
SELECT COUNT(*) as total
FROM chat_participante
WHERE sala_id = ? AND usuario_id = ?
"""

EXCLUIR_PARTICIPANTE = """
DELETE FROM chat_participante
WHERE sala_id = ? AND usuario_id = ?
"""
```

#### Arquivo `sql/chat_mensagem_sql.py`

```python
"""
Queries SQL para mensagens de chat.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS chat_mensagem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala_id TEXT NOT NULL,
    usuario_id INTEGER NOT NULL,
    mensagem TEXT NOT NULL,
    data_envio TIMESTAMP NOT NULL,
    lida_em TIMESTAMP,

    FOREIGN KEY (sala_id) REFERENCES chat_sala(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
)
"""

CRIAR_INDICES = """
CREATE INDEX IF NOT EXISTS idx_chat_mensagem_sala_data
ON chat_mensagem(sala_id, data_envio DESC);

CREATE INDEX IF NOT EXISTS idx_chat_mensagem_usuario
ON chat_mensagem(usuario_id);
"""

INSERIR = """
INSERT INTO chat_mensagem (sala_id, usuario_id, mensagem, data_envio)
VALUES (?, ?, ?, ?)
"""

OBTER_MENSAGENS_SALA = """
SELECT
    cm.id,
    cm.sala_id,
    cm.usuario_id,
    cm.mensagem,
    cm.data_envio as "data_envio [timestamp]",
    cm.lida_em as "lida_em [timestamp]",
    u.nome as usuario_nome,
    u.email as usuario_email
FROM chat_mensagem cm
INNER JOIN usuario u ON cm.usuario_id = u.id
WHERE cm.sala_id = ?
ORDER BY cm.data_envio ASC
LIMIT ? OFFSET ?
"""

OBTER_ULTIMA_MENSAGEM_SALA = """
SELECT
    cm.id,
    cm.sala_id,
    cm.usuario_id,
    cm.mensagem,
    cm.data_envio as "data_envio [timestamp]",
    cm.lida_em as "lida_em [timestamp]",
    u.nome as usuario_nome
FROM chat_mensagem cm
INNER JOIN usuario u ON cm.usuario_id = u.id
WHERE cm.sala_id = ?
ORDER BY cm.data_envio DESC
LIMIT 1
"""

CONTAR_NAO_LIDAS_SALA = """
SELECT COUNT(*) as total
FROM chat_mensagem cm
INNER JOIN chat_participante cp ON cm.sala_id = cp.sala_id
WHERE cm.sala_id = ?
  AND cp.usuario_id = ?
  AND cm.usuario_id != ?
  AND (cp.ultima_leitura IS NULL OR cm.data_envio > cp.ultima_leitura)
"""

CONTAR_NAO_LIDAS_USUARIO = """
SELECT COUNT(*) as total
FROM chat_mensagem cm
INNER JOIN chat_participante cp ON cm.sala_id = cp.sala_id
WHERE cp.usuario_id = ?
  AND cm.usuario_id != ?
  AND (cp.ultima_leitura IS NULL OR cm.data_envio > cp.ultima_leitura)
"""

MARCAR_COMO_LIDA = """
UPDATE chat_mensagem
SET lida_em = ?
WHERE sala_id = ?
  AND usuario_id != ?
  AND lida_em IS NULL
"""

EXCLUIR_MENSAGEM = """
DELETE FROM chat_mensagem WHERE id = ?
"""

EXCLUIR_MENSAGENS_SALA = """
DELETE FROM chat_mensagem WHERE sala_id = ?
"""
```

**Explicação dos Campos:**

**`chat_sala`:**
- `id` (TEXT): ID determinístico no formato "menor_id_maior_id"
- `criada_em` (TIMESTAMP): Data/hora de criação da sala
- `ultima_atividade` (TIMESTAMP): Data/hora da última mensagem (usado para ordenar conversas)

**`chat_participante`:**
- `sala_id` (TEXT): Referência para chat_sala
- `usuario_id` (INTEGER): Referência para usuario
- `ultima_leitura` (TIMESTAMP): Data/hora da última leitura pelo usuário (para calcular não lidas)

**`chat_mensagem`:**
- `id` (INTEGER): ID único da mensagem
- `sala_id` (TEXT): Referência para chat_sala
- `usuario_id` (INTEGER): Quem enviou a mensagem
- `mensagem` (TEXT): Conteúdo textual
- `data_envio` (TIMESTAMP): Data/hora de envio
- `lida_em` (TIMESTAMP): Data/hora em que foi lida (NULL = não lida)

---

## 📦 Camada 2: Models

### Model de Sala (`model/chat_sala_model.py`)

```python
"""
Model para salas de chat.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChatSala:
    """
    Representa uma sala de chat entre 2 usuários.

    Attributes:
        id: Identificador único no formato "menor_id_maior_id"
        criada_em: Data e hora de criação da sala
        ultima_atividade: Data e hora da última mensagem
    """
    id: str
    criada_em: datetime
    ultima_atividade: datetime

    def to_dict(self) -> dict:
        """Converte para dicionário (útil para JSON)."""
        return {
            "id": self.id,
            "criada_em": self.criada_em.isoformat(),
            "ultima_atividade": self.ultima_atividade.isoformat()
        }
```

### Model de Participante (`model/chat_participante_model.py`)

```python
"""
Model para participantes de salas de chat.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ChatParticipante:
    """
    Representa um participante de uma sala de chat.

    Attributes:
        sala_id: ID da sala
        usuario_id: ID do usuário
        ultima_leitura: Data e hora da última leitura
        usuario_nome: Nome do usuário (campo de JOIN)
        usuario_email: Email do usuário (campo de JOIN)
    """
    sala_id: str
    usuario_id: int
    ultima_leitura: Optional[datetime] = None
    usuario_nome: Optional[str] = None
    usuario_email: Optional[str] = None

    def to_dict(self) -> dict:
        """Converte para dicionário (útil para JSON)."""
        return {
            "sala_id": self.sala_id,
            "usuario_id": self.usuario_id,
            "ultima_leitura": self.ultima_leitura.isoformat() if self.ultima_leitura else None,
            "usuario_nome": self.usuario_nome,
            "usuario_email": self.usuario_email
        }
```

### Model de Mensagem (`model/chat_mensagem_model.py`)

```python
"""
Model para mensagens de chat.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ChatMensagem:
    """
    Representa uma mensagem de chat.

    Attributes:
        id: Identificador único da mensagem
        sala_id: ID da sala onde foi enviada
        usuario_id: ID do usuário que enviou
        mensagem: Conteúdo textual
        data_envio: Data e hora de envio
        lida_em: Data e hora em que foi lida (None = não lida)
        usuario_nome: Nome do remetente (campo de JOIN)
        usuario_email: Email do remetente (campo de JOIN)
    """
    id: int
    sala_id: str
    usuario_id: int
    mensagem: str
    data_envio: datetime
    lida_em: Optional[datetime] = None
    usuario_nome: Optional[str] = None
    usuario_email: Optional[str] = None

    def to_dict(self) -> dict:
        """Converte para dicionário (útil para JSON/SSE)."""
        return {
            "id": self.id,
            "sala_id": self.sala_id,
            "usuario_id": self.usuario_id,
            "mensagem": self.mensagem,
            "data_envio": self.data_envio.isoformat(),
            "lida_em": self.lida_em.isoformat() if self.lida_em else None,
            "usuario_nome": self.usuario_nome,
            "usuario_email": self.usuario_email
        }

    def foi_lida(self) -> bool:
        """Verifica se mensagem foi lida."""
        return self.lida_em is not None
```

---

## 🗃️ Camada 3: Repositories

### Repository de Sala (`repo/chat_sala_repo.py`)

```python
"""
Repository para operações de salas de chat.
"""
from typing import Optional, List
from model.chat_sala_model import ChatSala
from sql.chat_sala_sql import *
from util.db_util import get_connection
from util.datetime_util import agora


def _row_to_chat_sala(row) -> ChatSala:
    """Converte row do banco para ChatSala."""
    return ChatSala(
        id=row["id"],
        criada_em=row["criada_em"],
        ultima_atividade=row["ultima_atividade"]
    )


def criar_tabela() -> bool:
    """Cria tabela de salas e índices."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_INDICES)
        return True


def gerar_sala_id(usuario1_id: int, usuario2_id: int) -> str:
    """
    Gera ID único e determinístico para sala entre 2 usuários.

    Args:
        usuario1_id: ID do primeiro usuário
        usuario2_id: ID do segundo usuário

    Returns:
        String no formato "menor_id_maior_id"

    Examples:
        >>> gerar_sala_id(3, 7)
        "3_7"
        >>> gerar_sala_id(7, 3)
        "3_7"
    """
    ids_ordenados = sorted([usuario1_id, usuario2_id])
    return f"{ids_ordenados[0]}_{ids_ordenados[1]}"


def inserir(sala: ChatSala) -> Optional[str]:
    """Insere nova sala no banco."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            sala.id,
            sala.criada_em,
            sala.ultima_atividade
        ))
        return sala.id


def obter_por_id(sala_id: str) -> Optional[ChatSala]:
    """Obtém sala por ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (sala_id,))
        row = cursor.fetchone()
        return _row_to_chat_sala(row) if row else None


def obter_ou_criar(usuario1_id: int, usuario2_id: int) -> ChatSala:
    """
    Obtém sala existente ou cria nova se não existir.

    Args:
        usuario1_id: ID do primeiro usuário
        usuario2_id: ID do segundo usuário

    Returns:
        ChatSala existente ou recém-criada
    """
    sala_id = gerar_sala_id(usuario1_id, usuario2_id)
    sala_existente = obter_por_id(sala_id)

    if sala_existente:
        return sala_existente

    # Criar nova sala
    nova_sala = ChatSala(
        id=sala_id,
        criada_em=agora(),
        ultima_atividade=agora()
    )
    inserir(nova_sala)

    return nova_sala


def atualizar_ultima_atividade(sala_id: str) -> bool:
    """Atualiza timestamp de última atividade."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_ULTIMA_ATIVIDADE, (agora(), sala_id))
        return cursor.rowcount > 0


def excluir(sala_id: str) -> bool:
    """Exclui sala (CASCADE exclui participantes e mensagens)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (sala_id,))
        return cursor.rowcount > 0
```

### Repository de Participante (`repo/chat_participante_repo.py`)

```python
"""
Repository para participantes de salas de chat.
"""
from typing import List, Optional
from model.chat_participante_model import ChatParticipante
from model.chat_sala_model import ChatSala
from sql.chat_participante_sql import *
from util.db_util import get_connection
from util.datetime_util import agora


def _row_to_chat_participante(row) -> ChatParticipante:
    """Converte row do banco para ChatParticipante."""
    usuario_nome = row.get("usuario_nome")
    usuario_email = row.get("usuario_email")

    return ChatParticipante(
        sala_id=row["sala_id"],
        usuario_id=row["usuario_id"],
        ultima_leitura=row.get("ultima_leitura"),
        usuario_nome=usuario_nome,
        usuario_email=usuario_email
    )


def criar_tabela() -> bool:
    """Cria tabela de participantes e índices."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_INDICES)
        return True


def inserir(participante: ChatParticipante) -> bool:
    """Insere novo participante na sala."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            participante.sala_id,
            participante.usuario_id,
            participante.ultima_leitura
        ))
        return cursor.rowcount > 0


def adicionar_participantes_sala(sala_id: str, usuario1_id: int, usuario2_id: int) -> bool:
    """
    Adiciona 2 usuários como participantes de uma sala.

    Args:
        sala_id: ID da sala
        usuario1_id: ID do primeiro usuário
        usuario2_id: ID do segundo usuário

    Returns:
        True se ambos foram adicionados com sucesso
    """
    p1 = ChatParticipante(sala_id=sala_id, usuario_id=usuario1_id)
    p2 = ChatParticipante(sala_id=sala_id, usuario_id=usuario2_id)

    return inserir(p1) and inserir(p2)


def obter_participantes_sala(sala_id: str) -> List[ChatParticipante]:
    """Obtém todos os participantes de uma sala."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_PARTICIPANTES_SALA, (sala_id,))
        rows = cursor.fetchall()
        return [_row_to_chat_participante(row) for row in rows]


def obter_outro_participante(sala_id: str, usuario_id: int) -> Optional[ChatParticipante]:
    """
    Obtém o outro participante da sala (não o usuário especificado).

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário atual

    Returns:
        ChatParticipante do outro usuário ou None
    """
    participantes = obter_participantes_sala(sala_id)
    for p in participantes:
        if p.usuario_id != usuario_id:
            return p
    return None


def obter_conversas_usuario(
    usuario_id: int,
    limit: int = 12,
    offset: int = 0
) -> List[dict]:
    """
    Obtém conversas de um usuário com informações completas.

    Returns:
        Lista de dicionários com:
        - sala_id
        - outro_usuario_id
        - outro_usuario_nome
        - outro_usuario_email
        - ultima_atividade
        - nao_lidas
        - ultima_mensagem
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_SALAS_USUARIO, (usuario_id, limit, offset))
        salas = cursor.fetchall()

        conversas = []
        for sala in salas:
            # Obter o outro participante
            outro = obter_outro_participante(sala["sala_id"], usuario_id)
            if not outro:
                continue

            # Importar aqui para evitar circular import
            from repo import chat_mensagem_repo

            # Obter última mensagem
            ultima_msg = chat_mensagem_repo.obter_ultima_mensagem_sala(sala["sala_id"])

            # Contar não lidas
            nao_lidas = chat_mensagem_repo.contar_nao_lidas_sala(
                sala["sala_id"],
                usuario_id
            )

            conversas.append({
                "sala_id": sala["sala_id"],
                "outro_usuario_id": outro.usuario_id,
                "outro_usuario_nome": outro.usuario_nome,
                "outro_usuario_email": outro.usuario_email,
                "ultima_atividade": sala["ultima_atividade"],
                "nao_lidas": nao_lidas,
                "ultima_mensagem": ultima_msg.mensagem if ultima_msg else None,
                "ultima_mensagem_data": ultima_msg.data_envio if ultima_msg else None
            })

        return conversas


def atualizar_ultima_leitura(sala_id: str, usuario_id: int) -> bool:
    """Atualiza timestamp de última leitura do usuário na sala."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_ULTIMA_LEITURA, (agora(), sala_id, usuario_id))
        return cursor.rowcount > 0


def usuario_esta_na_sala(sala_id: str, usuario_id: int) -> bool:
    """Verifica se usuário é participante da sala."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(VERIFICAR_USUARIO_NA_SALA, (sala_id, usuario_id))
        row = cursor.fetchone()
        return row["total"] > 0 if row else False


def excluir_participante(sala_id: str, usuario_id: int) -> bool:
    """Remove participante da sala."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR_PARTICIPANTE, (sala_id, usuario_id))
        return cursor.rowcount > 0
```

### Repository de Mensagem (`repo/chat_mensagem_repo.py`)

```python
"""
Repository para mensagens de chat.
"""
from typing import Optional, List
from model.chat_mensagem_model import ChatMensagem
from sql.chat_mensagem_sql import *
from util.db_util import get_connection
from util.datetime_util import agora


def _row_to_chat_mensagem(row) -> ChatMensagem:
    """Converte row do banco para ChatMensagem."""
    usuario_nome = row.get("usuario_nome")
    usuario_email = row.get("usuario_email")

    return ChatMensagem(
        id=row["id"],
        sala_id=row["sala_id"],
        usuario_id=row["usuario_id"],
        mensagem=row["mensagem"],
        data_envio=row["data_envio"],
        lida_em=row.get("lida_em"),
        usuario_nome=usuario_nome,
        usuario_email=usuario_email
    )


def criar_tabela() -> bool:
    """Cria tabela de mensagens e índices."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_INDICES)
        return True


def inserir(mensagem: ChatMensagem) -> Optional[int]:
    """Insere nova mensagem no banco."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            mensagem.sala_id,
            mensagem.usuario_id,
            mensagem.mensagem,
            agora()  # Sistema de timezone automático
        ))
        return cursor.lastrowid


def obter_mensagens_sala(
    sala_id: str,
    limit: int = 50,
    offset: int = 0
) -> List[ChatMensagem]:
    """
    Obtém mensagens de uma sala com paginação.

    Args:
        sala_id: ID da sala
        limit: Número máximo de mensagens
        offset: Deslocamento para paginação

    Returns:
        Lista de ChatMensagem ordenadas cronologicamente
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_MENSAGENS_SALA, (sala_id, limit, offset))
        rows = cursor.fetchall()
        return [_row_to_chat_mensagem(row) for row in rows]


def obter_ultima_mensagem_sala(sala_id: str) -> Optional[ChatMensagem]:
    """Obtém a última mensagem enviada na sala."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_ULTIMA_MENSAGEM_SALA, (sala_id,))
        row = cursor.fetchone()
        return _row_to_chat_mensagem(row) if row else None


def contar_nao_lidas_sala(sala_id: str, usuario_id: int) -> int:
    """
    Conta mensagens não lidas na sala para um usuário.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário

    Returns:
        Número de mensagens não lidas
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_NAO_LIDAS_SALA, (sala_id, usuario_id, usuario_id))
        row = cursor.fetchone()
        return row["total"] if row else 0


def contar_nao_lidas_usuario(usuario_id: int) -> int:
    """
    Conta total de mensagens não lidas do usuário em TODAS as salas.

    Args:
        usuario_id: ID do usuário

    Returns:
        Total de mensagens não lidas
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_NAO_LIDAS_USUARIO, (usuario_id, usuario_id))
        row = cursor.fetchone()
        return row["total"] if row else 0


def marcar_como_lida(sala_id: str, usuario_id: int) -> bool:
    """
    Marca todas as mensagens da sala como lidas para o usuário.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário que leu

    Returns:
        True se marcou com sucesso
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        # Marca mensagens como lidas
        cursor.execute(MARCAR_COMO_LIDA, (agora(), sala_id, usuario_id))

        # Atualiza ultima_leitura do participante
        from repo import chat_participante_repo
        chat_participante_repo.atualizar_ultima_leitura(sala_id, usuario_id)

        return True


def excluir_mensagem(id: int) -> bool:
    """Exclui uma mensagem específica."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR_MENSAGEM, (id,))
        return cursor.rowcount > 0


def excluir_mensagens_sala(sala_id: str) -> bool:
    """Exclui todas as mensagens de uma sala."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR_MENSAGENS_SALA, (sala_id,))
        return True
```

---

## ✅ Camada 4: DTOs e Validação

### DTOs (`dtos/chat_dto.py`)

```python
"""
DTOs para validação de dados do sistema de chat.
"""
from pydantic import BaseModel, field_validator


class IniciarChatDTO(BaseModel):
    """
    DTO para iniciar chat com outro usuário.

    Attributes:
        outro_usuario_id: ID do usuário para conversar
    """
    outro_usuario_id: int

    @field_validator("outro_usuario_id")
    @classmethod
    def validar_outro_usuario_id(cls, v):
        """Valida que ID é positivo."""
        if v <= 0:
            raise ValueError("ID do usuário deve ser positivo")
        return v


class EnviarMensagemDTO(BaseModel):
    """
    DTO para enviar mensagem em uma sala.

    Attributes:
        sala_id: ID da sala (formato "menor_id_maior_id")
        mensagem: Conteúdo da mensagem
    """
    sala_id: str
    mensagem: str

    @field_validator("sala_id")
    @classmethod
    def validar_sala_id(cls, v):
        """Valida formato do sala_id."""
        if not v or "_" not in v:
            raise ValueError("ID da sala inválido (esperado formato 'id1_id2')")

        partes = v.split("_")
        if len(partes) != 2:
            raise ValueError("ID da sala inválido (esperado formato 'id1_id2')")

        try:
            id1, id2 = int(partes[0]), int(partes[1])
            if id1 <= 0 or id2 <= 0:
                raise ValueError("IDs dos usuários devem ser positivos")
            if id1 >= id2:
                raise ValueError("sala_id deve estar ordenado (menor_id primeiro)")
        except ValueError as e:
            raise ValueError(f"sala_id inválido: {str(e)}")

        return v

    @field_validator("mensagem")
    @classmethod
    def validar_mensagem(cls, v):
        """Valida mensagem."""
        v = v.strip()
        if not v:
            raise ValueError("Mensagem não pode estar vazia")
        if len(v) > 1000:
            raise ValueError("Mensagem muito longa (máx. 1000 caracteres)")
        return v


class CarregarMensagensDTO(BaseModel):
    """
    DTO para carregar mensagens de uma sala.

    Attributes:
        sala_id: ID da sala
        limit: Número máximo de mensagens
        offset: Deslocamento para paginação
    """
    sala_id: str
    limit: int = 50
    offset: int = 0

    @field_validator("limit")
    @classmethod
    def validar_limit(cls, v):
        """Valida limit."""
        if v < 1 or v > 200:
            raise ValueError("Limite deve estar entre 1 e 200")
        return v

    @field_validator("offset")
    @classmethod
    def validar_offset(cls, v):
        """Valida offset."""
        if v < 0:
            raise ValueError("Offset não pode ser negativo")
        return v


class BuscarUsuariosDTO(BaseModel):
    """
    DTO para buscar usuários (autocomplete).

    Attributes:
        query: Termo de busca (ID, nome ou email)
        limit: Número máximo de resultados
    """
    query: str
    limit: int = 5

    @field_validator("query")
    @classmethod
    def validar_query(cls, v):
        """Valida query."""
        v = v.strip()
        if not v:
            raise ValueError("Termo de busca não pode estar vazio")
        if len(v) < 2:
            raise ValueError("Termo de busca deve ter no mínimo 2 caracteres")
        return v

    @field_validator("limit")
    @classmethod
    def validar_limit(cls, v):
        """Valida limit."""
        if v < 1 or v > 20:
            raise ValueError("Limite deve estar entre 1 e 20")
        return v


class CarregarConversasDTO(BaseModel):
    """
    DTO para carregar lista de conversas.

    Attributes:
        limit: Número de conversas a carregar
        offset: Deslocamento para paginação
    """
    limit: int = 12
    offset: int = 0

    @field_validator("limit")
    @classmethod
    def validar_limit(cls, v):
        """Valida limit."""
        if v < 1 or v > 50:
            raise ValueError("Limite deve estar entre 1 e 50")
        return v

    @field_validator("offset")
    @classmethod
    def validar_offset(cls, v):
        """Valida offset."""
        if v < 0:
            raise ValueError("Offset não pode ser negativo")
        return v
```

---

## ⚙️ Camada 5: Gerenciador de Conexões SSE

### Chat Manager (`util/chat_manager.py`)

Este é o **coração do sistema SSE**, gerenciando conexões **por usuário** (não por sala).

```python
"""
Gerenciador de conexões SSE para chat privado 1-para-1.

Este módulo é responsável por:
- Gerenciar conexões EventSource ativas POR USUÁRIO (não por sala)
- Notificar mensagens de TODAS as salas do usuário
- Broadcast para os 2 participantes de uma sala
- Controlar timeouts e cleanup
"""
import asyncio
from typing import Dict, Set
from collections import defaultdict
from util.logger_config import logger


class ChatManager:
    """
    Gerenciador singleton de conexões SSE do chat.

    Estrutura interna:
    {
        usuario_id: asyncio.Queue,  # Uma queue por usuário
        usuario_id: asyncio.Queue,
        ...
    }

    Cada usuário tem UMA conexão SSE que recebe mensagens de TODAS as salas.
    """

    def __init__(self):
        """Inicializa o gerenciador com dicionários vazios."""
        # Dicionário: usuario_id -> Queue
        self._connections: Dict[int, asyncio.Queue] = {}
        # Controle de conexões ativas
        self._active_connections: Set[int] = set()

    async def connect(self, usuario_id: int) -> asyncio.Queue:
        """
        Registra uma nova conexão SSE para um usuário.

        Args:
            usuario_id: ID do usuário conectando

        Returns:
            Queue para receber mensagens
        """
        # Cria uma Queue para este usuário
        queue = asyncio.Queue()

        # Registra a conexão
        self._connections[usuario_id] = queue
        self._active_connections.add(usuario_id)

        logger.info(
            f"Usuário {usuario_id} conectou ao chat. "
            f"Total conectados: {len(self._active_connections)}"
        )

        return queue

    async def disconnect(self, usuario_id: int):
        """
        Remove uma conexão SSE.

        Args:
            usuario_id: ID do usuário desconectando
        """
        try:
            # Remove a queue do dicionário
            if usuario_id in self._connections:
                del self._connections[usuario_id]

            # Remove do set de conexões ativas
            self._active_connections.discard(usuario_id)

            logger.info(
                f"Usuário {usuario_id} desconectou do chat. "
                f"Total conectados: {len(self._active_connections)}"
            )
        except Exception as e:
            logger.error(f"Erro ao desconectar usuário {usuario_id}: {e}")

    async def broadcast_para_sala(self, sala_id: str, mensagem_dict: dict):
        """
        Envia uma mensagem para os 2 participantes de uma sala.

        Este método:
        1. Extrai os IDs dos usuários do sala_id (formato "id1_id2")
        2. Verifica quais estão conectados
        3. Envia mensagem para suas queues

        Args:
            sala_id: ID da sala no formato "menor_id_maior_id"
            mensagem_dict: Dicionário com dados da mensagem (incluindo sala_id)
        """
        try:
            # Extrair IDs dos participantes do sala_id
            partes = sala_id.split("_")
            if len(partes) != 2:
                logger.error(f"sala_id inválido: {sala_id}")
                return

            usuario1_id = int(partes[0])
            usuario2_id = int(partes[1])

            # Enviar para cada participante se estiver conectado
            for usuario_id in [usuario1_id, usuario2_id]:
                if usuario_id in self._connections:
                    queue = self._connections[usuario_id]
                    try:
                        await queue.put(mensagem_dict)
                        logger.debug(
                            f"Mensagem enviada para usuário {usuario_id} "
                            f"(sala {sala_id})"
                        )
                    except Exception as e:
                        logger.error(
                            f"Erro ao enviar para usuário {usuario_id}: {e}"
                        )
                        await self.disconnect(usuario_id)

        except Exception as e:
            logger.error(f"Erro no broadcast_para_sala: {e}")

    async def notificar_usuario(self, usuario_id: int, evento: dict):
        """
        Envia um evento específico para um usuário.

        Args:
            usuario_id: ID do usuário
            evento: Dicionário com dados do evento
        """
        if usuario_id in self._connections:
            queue = self._connections[usuario_id]
            try:
                await queue.put(evento)
                logger.debug(f"Evento enviado para usuário {usuario_id}")
            except Exception as e:
                logger.error(f"Erro ao notificar usuário {usuario_id}: {e}")
                await self.disconnect(usuario_id)

    def usuario_esta_conectado(self, usuario_id: int) -> bool:
        """
        Verifica se usuário está conectado via SSE.

        Args:
            usuario_id: ID do usuário

        Returns:
            True se está conectado
        """
        return usuario_id in self._active_connections

    def get_total_connections(self) -> int:
        """
        Retorna número total de usuários conectados.

        Returns:
            Número de conexões ativas
        """
        return len(self._active_connections)

    def get_connected_users(self) -> list:
        """
        Retorna lista de IDs de usuários conectados.

        Returns:
            Lista de IDs
        """
        return list(self._active_connections)


# Instância singleton global
chat_manager = ChatManager()
```

**Diferença Fundamental:**

- **Antes (sistema de salas públicas)**: Conexão SSE por sala, usuário recebe apenas mensagens daquela sala
- **Agora (chat 1-para-1)**: Conexão SSE por usuário, recebe mensagens de TODAS as salas que participa
- Frontend roteia mensagens baseado no `sala_id` contido no JSON

---

## 🌐 Camada 6: Routes e Endpoints

### Routes (`routes/chat_routes.py`)

```python
"""
Routes para sistema de chat privado 1-para-1 com widget retrátil.
"""
import json
import asyncio
from typing import Optional
from fastapi import APIRouter, Form, Request, Query, status
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import ValidationError

from dtos.chat_dto import (
    IniciarChatDTO,
    EnviarMensagemDTO,
    CarregarMensagensDTO,
    BuscarUsuariosDTO,
    CarregarConversasDTO
)
from model.chat_mensagem_model import ChatMensagem
from model.chat_sala_model import ChatSala
from repo import chat_sala_repo, chat_participante_repo, chat_mensagem_repo, usuario_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.logger_config import logger
from util.chat_manager import chat_manager
from util.datetime_util import agora

router = APIRouter(prefix="/chat")
templates = criar_templates("templates")


@router.get("/widget")
@requer_autenticacao()
async def widget(request: Request, usuario_logado: Optional[dict] = None):
    """
    Renderiza o componente de chat widget (para incluir em base_privada.html).

    Returns:
        HTML do widget retrátil
    """
    assert usuario_logado is not None

    # Conta total de não lidas
    total_nao_lidas = chat_mensagem_repo.contar_nao_lidas_usuario(
        usuario_logado["id"]
    )

    return templates.TemplateResponse(
        "components/chat_widget.html",
        {
            "request": request,
            "total_nao_lidas": total_nao_lidas
        }
    )


@router.get("/stream")
@requer_autenticacao()
async def stream_mensagens(
    request: Request,
    usuario_logado: Optional[dict] = None
):
    """
    Endpoint SSE que mantém conexão aberta e envia mensagens de TODAS as salas do usuário.

    Este endpoint:
    1. Registra conexão no ChatManager (por usuário, não por sala)
    2. Mantém conexão aberta indefinidamente
    3. Envia eventos SSE quando novas mensagens chegam em QUALQUER sala
    4. Desconecta automaticamente se cliente fechar

    Returns:
        StreamingResponse com eventos SSE
    """
    assert usuario_logado is not None

    async def event_generator():
        """Generator que produz eventos SSE."""
        # Registra conexão para o usuário
        queue = await chat_manager.connect(usuario_logado["id"])

        try:
            logger.info(
                f"SSE stream iniciado para usuário {usuario_logado['id']}"
            )

            # Loop infinito: enquanto cliente estiver conectado
            while True:
                # Aguarda próxima mensagem/evento na queue
                evento = await queue.get()

                # Formata como evento SSE
                # IMPORTANTE: formato SSE é "data: JSON\n\n"
                sse_data = f"data: {json.dumps(evento)}\n\n"

                yield sse_data

                # Pequeno delay para evitar sobrecarga
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            # Cliente desconectou (normal)
            logger.info(
                f"SSE stream cancelado para usuário {usuario_logado['id']}"
            )
        except Exception as e:
            # Erro inesperado
            logger.error(f"Erro no SSE stream: {e}")
        finally:
            # Sempre desconecta ao final
            await chat_manager.disconnect(usuario_logado["id"])

    # Retorna StreamingResponse com headers SSE
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Para NGINX
        }
    )


@router.post("/iniciar")
@requer_autenticacao()
async def iniciar_chat(
    request: Request,
    outro_usuario_id: int = Form(...),
    usuario_logado: Optional[dict] = None
):
    """
    Inicia chat com outro usuário (cria/abre sala).

    Args:
        outro_usuario_id: ID do usuário para conversar

    Returns:
        JSON com sala_id e últimas mensagens
    """
    assert usuario_logado is not None

    try:
        # Validação
        dto = IniciarChatDTO(outro_usuario_id=outro_usuario_id)

        # Verifica que não é o próprio usuário
        if dto.outro_usuario_id == usuario_logado["id"]:
            return JSONResponse(
                {"success": False, "erro": "Não é possível conversar consigo mesmo"},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Verifica que outro usuário existe
        outro_usuario = usuario_repo.obter_por_id(dto.outro_usuario_id)
        if not outro_usuario:
            return JSONResponse(
                {"success": False, "erro": "Usuário não encontrado"},
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Obtém ou cria sala
        sala = chat_sala_repo.obter_ou_criar(
            usuario_logado["id"],
            dto.outro_usuario_id
        )

        # Verifica se participantes já estão cadastrados
        participantes = chat_participante_repo.obter_participantes_sala(sala.id)
        if len(participantes) == 0:
            # Primeira vez: adicionar participantes
            chat_participante_repo.adicionar_participantes_sala(
                sala.id,
                usuario_logado["id"],
                dto.outro_usuario_id
            )

        # Carrega últimas 50 mensagens
        mensagens = chat_mensagem_repo.obter_mensagens_sala(sala.id, limit=50)

        # Marca como lida
        chat_participante_repo.atualizar_ultima_leitura(
            sala.id,
            usuario_logado["id"]
        )

        logger.info(
            f"Chat iniciado: sala={sala.id}, usuários={usuario_logado['id']} e {dto.outro_usuario_id}"
        )

        return {
            "success": True,
            "sala_id": sala.id,
            "outro_usuario": {
                "id": outro_usuario.id,
                "nome": outro_usuario.nome,
                "email": outro_usuario.email
            },
            "mensagens": [msg.to_dict() for msg in mensagens]
        }

    except ValidationError as e:
        erros = {}
        for erro in e.errors():
            campo = erro["loc"][0] if erro["loc"] else "geral"
            erros[campo] = erro["msg"]
        return JSONResponse(
            {"success": False, "erros": erros},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        logger.error(f"Erro ao iniciar chat: {e}")
        return JSONResponse(
            {"success": False, "erro": "Erro interno do servidor"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/conversas")
@requer_autenticacao()
async def listar_conversas(
    request: Request,
    limit: int = Query(12, ge=1, le=50),
    offset: int = Query(0, ge=0),
    usuario_logado: Optional[dict] = None
):
    """
    Lista conversas do usuário com paginação.

    Args:
        limit: Número de conversas (default: 12)
        offset: Deslocamento para paginação

    Returns:
        JSON com lista de conversas
    """
    assert usuario_logado is not None

    try:
        # Validação
        dto = CarregarConversasDTO(limit=limit, offset=offset)

        # Obtém conversas
        conversas = chat_participante_repo.obter_conversas_usuario(
            usuario_logado["id"],
            dto.limit,
            dto.offset
        )

        return {
            "success": True,
            "conversas": conversas,
            "total": len(conversas),
            "limit": dto.limit,
            "offset": dto.offset
        }

    except Exception as e:
        logger.error(f"Erro ao listar conversas: {e}")
        return JSONResponse(
            {"success": False, "erro": "Erro interno do servidor"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/mensagens/{sala_id}")
@requer_autenticacao()
async def carregar_mensagens(
    request: Request,
    sala_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    usuario_logado: Optional[dict] = None
):
    """
    Carrega mensagens de uma sala com paginação.

    Args:
        sala_id: ID da sala
        limit: Número de mensagens
        offset: Deslocamento

    Returns:
        JSON com mensagens
    """
    assert usuario_logado is not None

    try:
        # Validação
        dto = CarregarMensagensDTO(sala_id=sala_id, limit=limit, offset=offset)

        # Verifica que usuário é participante da sala
        if not chat_participante_repo.usuario_esta_na_sala(sala_id, usuario_logado["id"]):
            return JSONResponse(
                {"success": False, "erro": "Acesso negado a esta sala"},
                status_code=status.HTTP_403_FORBIDDEN
            )

        # Carrega mensagens
        mensagens = chat_mensagem_repo.obter_mensagens_sala(
            sala_id,
            dto.limit,
            dto.offset
        )

        return {
            "success": True,
            "mensagens": [msg.to_dict() for msg in mensagens],
            "total": len(mensagens)
        }

    except Exception as e:
        logger.error(f"Erro ao carregar mensagens: {e}")
        return JSONResponse(
            {"success": False, "erro": "Erro interno do servidor"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/enviar")
@requer_autenticacao()
async def enviar_mensagem(
    request: Request,
    sala_id: str = Form(...),
    mensagem: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """
    Envia mensagem em uma sala.

    Args:
        sala_id: ID da sala
        mensagem: Texto da mensagem

    Returns:
        JSON com sucesso ou erro
    """
    assert usuario_logado is not None

    try:
        # Validação
        dto = EnviarMensagemDTO(sala_id=sala_id, mensagem=mensagem)

        # Verifica que usuário é participante da sala
        if not chat_participante_repo.usuario_esta_na_sala(dto.sala_id, usuario_logado["id"]):
            return JSONResponse(
                {"success": False, "erro": "Acesso negado a esta sala"},
                status_code=status.HTTP_403_FORBIDDEN
            )

        # Cria objeto de mensagem
        nova_mensagem = ChatMensagem(
            id=0,  # Será preenchido pelo banco
            sala_id=dto.sala_id,
            usuario_id=usuario_logado["id"],
            mensagem=dto.mensagem,
            data_envio=agora(),
            lida_em=None,
            usuario_nome=usuario_logado.get("nome"),
            usuario_email=usuario_logado.get("email")
        )

        # Salva no banco
        mensagem_id = chat_mensagem_repo.inserir(nova_mensagem)

        if not mensagem_id:
            return JSONResponse(
                {"success": False, "erro": "Erro ao salvar mensagem"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Atualiza ID e timestamp de última atividade
        nova_mensagem.id = mensagem_id
        chat_sala_repo.atualizar_ultima_atividade(dto.sala_id)

        # CRITICAL: Notifica os 2 participantes da sala via SSE
        await chat_manager.broadcast_para_sala(dto.sala_id, nova_mensagem.to_dict())

        logger.info(
            f"Mensagem enviada: sala={dto.sala_id}, usuario={usuario_logado['id']}, id={mensagem_id}"
        )

        return {
            "success": True,
            "mensagem_id": mensagem_id,
            "data_envio": nova_mensagem.data_envio.isoformat()
        }

    except ValidationError as e:
        erros = {}
        for erro in e.errors():
            campo = erro["loc"][0] if erro["loc"] else "geral"
            erros[campo] = erro["msg"]
        return JSONResponse(
            {"success": False, "erros": erros},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")
        return JSONResponse(
            {"success": False, "erro": "Erro interno do servidor"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/buscar-usuarios")
@requer_autenticacao()
async def buscar_usuarios(
    request: Request,
    q: str = Query(..., min_length=2),
    limit: int = Query(5, ge=1, le=20),
    usuario_logado: Optional[dict] = None
):
    """
    Busca usuários para autocomplete.

    Args:
        q: Termo de busca (ID, nome ou email)
        limit: Número máximo de resultados

    Returns:
        JSON com lista de usuários
    """
    assert usuario_logado is not None

    try:
        # Validação
        dto = BuscarUsuariosDTO(query=q, limit=limit)

        # Busca usuários
        usuarios = usuario_repo.buscar_usuarios(dto.query, dto.limit)

        # Remove o próprio usuário dos resultados
        usuarios = [u for u in usuarios if u.id != usuario_logado["id"]]

        return {
            "success": True,
            "usuarios": [
                {
                    "id": u.id,
                    "nome": u.nome,
                    "email": u.email
                }
                for u in usuarios
            ]
        }

    except Exception as e:
        logger.error(f"Erro ao buscar usuários: {e}")
        return JSONResponse(
            {"success": False, "erro": "Erro interno do servidor"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/marcar-lida/{sala_id}")
@requer_autenticacao()
async def marcar_como_lida(
    request: Request,
    sala_id: str,
    usuario_logado: Optional[dict] = None
):
    """
    Marca todas as mensagens da sala como lidas.

    Args:
        sala_id: ID da sala

    Returns:
        JSON com sucesso
    """
    assert usuario_logado is not None

    try:
        # Verifica que usuário é participante
        if not chat_participante_repo.usuario_esta_na_sala(sala_id, usuario_logado["id"]):
            return JSONResponse(
                {"success": False, "erro": "Acesso negado a esta sala"},
                status_code=status.HTTP_403_FORBIDDEN
            )

        # Marca como lida
        chat_mensagem_repo.marcar_como_lida(sala_id, usuario_logado["id"])

        return {"success": True}

    except Exception as e:
        logger.error(f"Erro ao marcar como lida: {e}")
        return JSONResponse(
            {"success": False, "erro": "Erro interno do servidor"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

**Endpoints Implementados:**

1. **`GET /chat/widget`**: Renderiza componente HTML do widget
2. **`GET /chat/stream`**: SSE para receber mensagens (todas as salas)
3. **`POST /chat/iniciar`**: Cria/abre sala com outro usuário
4. **`GET /chat/conversas`**: Lista conversas com paginação
5. **`GET /chat/mensagens/{sala_id}`**: Carrega mensagens de uma sala
6. **`POST /chat/enviar`**: Envia mensagem
7. **`GET /chat/buscar-usuarios`**: Autocomplete de usuários
8. **`POST /chat/marcar-lida/{sala_id}`**: Marca sala como lida

---

## 🎨 Camada 7: Frontend - Widget Retrátil

### Componente HTML (`templates/components/chat_widget.html`)

```html
<!--
Componente de Chat Widget Retrátil (Estilo WhatsApp)

Para incluir em templates:
{% include 'components/chat_widget.html' %}

Este componente deve ser incluído em base_privada.html para estar disponível
em todas as páginas privadas.
-->

<!-- Botão flutuante retraído -->
<div id="chat-widget-button" class="chat-widget-button" onclick="toggleChatWidget()">
    <i class="bi bi-chat-dots-fill"></i>
    <span id="chat-badge" class="chat-badge {% if total_nao_lidas > 0 %}show{% endif %}">
        {{ total_nao_lidas if total_nao_lidas > 0 else '' }}
    </span>
</div>

<!-- Painel expandido -->
<div id="chat-widget-panel" class="chat-widget-panel">
    <!-- Header -->
    <div class="chat-widget-header">
        <h5 class="mb-0">
            <i class="bi bi-chat-dots-fill"></i> Mensagens
        </h5>
        <button class="btn btn-sm btn-link text-white" onclick="toggleChatWidget()">
            <i class="bi bi-x-lg"></i>
        </button>
    </div>

    <!-- Conteúdo: 2 colunas -->
    <div class="chat-widget-content">
        <!-- Coluna Esquerda: Lista de Conversas -->
        <div class="chat-conversations-panel">
            <!-- Busca de usuários -->
            <div class="chat-search-box">
                <input
                    type="text"
                    id="chat-user-search"
                    class="form-control form-control-sm"
                    placeholder="Buscar usuário..."
                    autocomplete="off"
                >
                <!-- Sugestões de autocomplete -->
                <div id="chat-search-suggestions" class="chat-search-suggestions"></div>
            </div>

            <!-- Lista de conversas -->
            <div id="chat-conversations-list" class="chat-conversations-list">
                <!-- Será preenchido via JavaScript -->
                <div class="text-center text-muted p-3">
                    <i class="bi bi-chat-dots"></i>
                    <p class="mb-0 small">Nenhuma conversa ainda</p>
                </div>
            </div>

            <!-- Botão carregar mais -->
            <div id="chat-load-more-container" class="text-center p-2" style="display: none;">
                <button
                    id="chat-load-more-btn"
                    class="btn btn-sm btn-outline-secondary btn-block"
                    onclick="carregarMaisConversas()"
                >
                    Carregar mais...
                </button>
            </div>
        </div>

        <!-- Coluna Direita: Área de Chat -->
        <div class="chat-messages-panel">
            <!-- Estado vazio: nenhuma conversa selecionada -->
            <div id="chat-empty-state" class="chat-empty-state">
                <i class="bi bi-chat-text"></i>
                <p>Selecione uma conversa ou busque um usuário</p>
            </div>

            <!-- Estado ativo: conversa selecionada -->
            <div id="chat-active-state" class="chat-active-state" style="display: none;">
                <!-- Header do chat ativo -->
                <div class="chat-active-header">
                    <div>
                        <strong id="chat-active-user-name">Nome do Usuário</strong>
                        <small class="text-muted d-block" id="chat-active-user-email">
                            email@exemplo.com
                        </small>
                    </div>
                    <button
                        class="btn btn-sm btn-link text-dark"
                        onclick="fecharChatAtivo()"
                        title="Voltar para lista"
                    >
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>

                <!-- Área de mensagens -->
                <div id="chat-messages-container" class="chat-messages-container">
                    <!-- Mensagens serão inseridas aqui via JavaScript -->
                </div>

                <!-- Campo de envio -->
                <div class="chat-input-container">
                    <form id="chat-send-form" onsubmit="enviarMensagem(event)">
                        <input type="hidden" id="chat-current-sala-id" value="">
                        <textarea
                            id="chat-message-input"
                            class="form-control form-control-sm"
                            placeholder="Digite uma mensagem..."
                            rows="1"
                            autocomplete="off"
                            maxlength="1000"
                        ></textarea>
                        <button type="submit" class="btn btn-primary btn-sm">
                            <i class="bi bi-send-fill"></i>
                        </button>
                    </form>
                    <small class="text-muted">Enter = enviar / Shift+Enter = nova linha</small>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- CSS do Widget -->
<link rel="stylesheet" href="/static/css/chat-widget.css">

<!-- JavaScript do Widget -->
<script src="/static/js/chat-widget.js"></script>
<script>
    // Inicializa widget quando página carregar
    document.addEventListener('DOMContentLoaded', () => {
        const usuarioId = {{ usuario_logado.id }};
        const usuarioNome = "{{ usuario_logado.nome }}";

        window.chatWidget.init(usuarioId, usuarioNome);
    });
</script>
```

### CSS do Widget (`static/css/chat-widget.css`)

```css
/**
 * Chat Widget Retrátil - Estilo WhatsApp
 */

/* ========================================
   Botão Flutuante Retraído
   ======================================== */

.chat-widget-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 60px;
    height: 60px;
    background-color: #0d6efd;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
    z-index: 9998;
}

.chat-widget-button:hover {
    background-color: #0b5ed7;
    transform: scale(1.1);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

/* Badge de mensagens não lidas */
.chat-badge {
    position: absolute;
    top: -5px;
    right: -5px;
    background-color: #dc3545;
    color: white;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: none;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: bold;
    border: 2px solid white;
}

.chat-badge.show {
    display: flex;
}

/* ========================================
   Painel Expandido
   ======================================== */

.chat-widget-panel {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 700px;
    height: 600px;
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    display: none;
    flex-direction: column;
    z-index: 9999;
    overflow: hidden;
}

.chat-widget-panel.show {
    display: flex;
    animation: slideUp 0.3s ease;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Header do painel */
.chat-widget-header {
    background-color: #0d6efd;
    color: white;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Conteúdo: 2 colunas */
.chat-widget-content {
    display: flex;
    flex: 1;
    overflow: hidden;
}

/* ========================================
   Coluna Esquerda: Lista de Conversas
   ======================================== */

.chat-conversations-panel {
    width: 35%;
    border-right: 1px solid #dee2e6;
    display: flex;
    flex-direction: column;
    background-color: #f8f9fa;
}

/* Busca de usuários */
.chat-search-box {
    padding: 0.75rem;
    border-bottom: 1px solid #dee2e6;
    position: relative;
}

.chat-search-suggestions {
    position: absolute;
    top: 100%;
    left: 0.75rem;
    right: 0.75rem;
    background-color: white;
    border: 1px solid #dee2e6;
    border-radius: 0.375rem;
    max-height: 200px;
    overflow-y: auto;
    display: none;
    z-index: 10;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.chat-search-suggestions.show {
    display: block;
}

.chat-search-suggestion-item {
    padding: 0.75rem;
    cursor: pointer;
    border-bottom: 1px solid #f8f9fa;
    transition: background-color 0.2s;
}

.chat-search-suggestion-item:hover {
    background-color: #f8f9fa;
}

.chat-search-suggestion-item:last-child {
    border-bottom: none;
}

/* Lista de conversas */
.chat-conversations-list {
    flex: 1;
    overflow-y: auto;
}

.chat-conversation-item {
    padding: 0.75rem;
    cursor: pointer;
    border-bottom: 1px solid #e9ecef;
    transition: background-color 0.2s;
    display: flex;
    justify-content: space-between;
    align-items: start;
}

.chat-conversation-item:hover {
    background-color: #e9ecef;
}

.chat-conversation-item.active {
    background-color: #e7f1ff;
    border-left: 3px solid #0d6efd;
}

.chat-conversation-info {
    flex: 1;
    overflow: hidden;
}

.chat-conversation-name {
    font-weight: 600;
    font-size: 0.875rem;
    margin-bottom: 0.25rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.chat-conversation-preview {
    font-size: 0.75rem;
    color: #6c757d;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.chat-conversation-meta {
    text-align: right;
    font-size: 0.7rem;
    color: #6c757d;
}

.chat-conversation-badge {
    background-color: #0d6efd;
    color: white;
    border-radius: 50%;
    padding: 0.15rem 0.4rem;
    font-size: 0.7rem;
    font-weight: bold;
    display: inline-block;
    margin-top: 0.25rem;
}

/* ========================================
   Coluna Direita: Área de Chat
   ======================================== */

.chat-messages-panel {
    width: 65%;
    display: flex;
    flex-direction: column;
    background-color: #f0f2f5;
}

/* Estado vazio */
.chat-empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #6c757d;
    padding: 2rem;
    text-align: center;
}

.chat-empty-state i {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.3;
}

/* Estado ativo */
.chat-active-state {
    flex: 1;
    display: flex;
    flex-direction: column;
}

/* Header do chat ativo */
.chat-active-header {
    background-color: white;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #dee2e6;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Área de mensagens */
.chat-messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

/* Bolhas de mensagens */
.chat-message {
    max-width: 70%;
    padding: 0.75rem 1rem;
    border-radius: 12px;
    position: relative;
    word-wrap: break-word;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Mensagem do próprio usuário (direita, azul) */
.chat-message.own {
    align-self: flex-end;
    background-color: #dcf8c6;
    color: #000;
}

/* Mensagem de outros usuários (esquerda, branco) */
.chat-message.other {
    align-self: flex-start;
    background-color: white;
}

.chat-message-text {
    margin-bottom: 0.25rem;
    line-height: 1.4;
}

/* Formatação markdown */
.chat-message-text strong {
    font-weight: 700;
}

.chat-message-text em {
    font-style: italic;
}

.chat-message-time {
    font-size: 0.7rem;
    color: #667781;
    text-align: right;
    margin-top: 0.25rem;
}

/* Campo de envio */
.chat-input-container {
    background-color: white;
    padding: 0.75rem 1rem;
    border-top: 1px solid #dee2e6;
}

.chat-input-container form {
    display: flex;
    gap: 0.5rem;
    align-items: flex-end;
}

.chat-input-container textarea {
    flex: 1;
    resize: none;
    border-radius: 20px;
    padding: 0.5rem 0.75rem;
    max-height: 100px;
    font-size: 0.875rem;
}

.chat-input-container button[type="submit"] {
    border-radius: 50%;
    width: 36px;
    height: 36px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

.chat-input-container small {
    display: block;
    margin-top: 0.25rem;
    font-size: 0.7rem;
}

/* ========================================
   Scrollbars
   ======================================== */

.chat-conversations-list::-webkit-scrollbar,
.chat-messages-container::-webkit-scrollbar {
    width: 6px;
}

.chat-conversations-list::-webkit-scrollbar-track,
.chat-messages-container::-webkit-scrollbar-track {
    background: #f1f1f1;
}

.chat-conversations-list::-webkit-scrollbar-thumb,
.chat-messages-container::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 3px;
}

.chat-conversations-list::-webkit-scrollbar-thumb:hover,
.chat-messages-container::-webkit-scrollbar-thumb:hover {
    background: #555;
}

/* ========================================
   Responsivo: Mobile
   ======================================== */

@media (max-width: 768px) {
    .chat-widget-panel {
        width: 100%;
        height: 100%;
        bottom: 0;
        right: 0;
        border-radius: 0;
    }

    .chat-conversations-panel {
        width: 100%;
    }

    .chat-messages-panel {
        width: 100%;
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        display: none;
    }

    .chat-messages-panel.show-mobile {
        display: flex;
    }
}
```

### JavaScript do Widget (`static/js/chat-widget.js`)

Devido ao tamanho extenso do JavaScript (~800 linhas), vou criar a estrutura principal com os recursos-chave:

```javascript
/**
 * Chat Widget Retrátil - Estilo WhatsApp
 *
 * Funcionalidades:
 * - SSE para receber mensagens em tempo real
 * - Autocomplete de usuários
 * - Formatação markdown (negrito, itálico)
 * - Lista de conversas com paginação
 * - Enter = enviar / Shift+Enter = quebra de linha
 */

const chatWidget = (() => {
    // Estado privado
    let eventSource = null;
    let usuarioId = null;
    let usuarioNome = null;
    let conversaAtual = null;  // {sala_id, outro_usuario_id, outro_usuario_nome}
    let conversas = [];  // Lista de conversas carregadas
    let conversasOffset = 0;
    let searchTimeout = null;

    // Elementos DOM (cachear para performance)
    const elementos = {
        widgetButton: null,
        widgetPanel: null,
        badge: null,
        searchInput: null,
        searchSuggestions: null,
        conversationsList: null,
        loadMoreContainer: null,
        loadMoreBtn: null,
        emptyState: null,
        activeState: null,
        activeUserName: null,
        activeUserEmail: null,
        messagesContainer: null,
        currentSalaIdInput: null,
        messageInput: null,
        sendForm: null
    };

    /**
     * Inicializa o widget
     */
    function init(userId, userName) {
        usuarioId = userId;
        usuarioNome = userName;

        // Cachear elementos DOM
        cachearElementos();

        // Configurar event listeners
        setupEventListeners();

        // Conectar ao SSE
        conectarSSE();

        // Carregar conversas iniciais
        carregarConversas();
    }

    /**
     * Cacheia referências dos elementos DOM
     */
    function cachearElementos() {
        elementos.widgetButton = document.getElementById('chat-widget-button');
        elementos.widgetPanel = document.getElementById('chat-widget-panel');
        elementos.badge = document.getElementById('chat-badge');
        elementos.searchInput = document.getElementById('chat-user-search');
        elementos.searchSuggestions = document.getElementById('chat-search-suggestions');
        elementos.conversationsList = document.getElementById('chat-conversations-list');
        elementos.loadMoreContainer = document.getElementById('chat-load-more-container');
        elementos.loadMoreBtn = document.getElementById('chat-load-more-btn');
        elementos.emptyState = document.getElementById('chat-empty-state');
        elementos.activeState = document.getElementById('chat-active-state');
        elementos.activeUserName = document.getElementById('chat-active-user-name');
        elementos.activeUserEmail = document.getElementById('chat-active-user-email');
        elementos.messagesContainer = document.getElementById('chat-messages-container');
        elementos.currentSalaIdInput = document.getElementById('chat-current-sala-id');
        elementos.messageInput = document.getElementById('chat-message-input');
        elementos.sendForm = document.getElementById('chat-send-form');
    }

    /**
     * Configura event listeners
     */
    function setupEventListeners() {
        // Busca de usuários com debounce
        elementos.searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();

            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    buscarUsuarios(query);
                }, 300);
            } else {
                esconderSugestoes();
            }
        });

        // Auto-resize do textarea
        elementos.messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 100) + 'px';
        });

        // Enter = enviar / Shift+Enter = nova linha
        elementos.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                elementos.sendForm.dispatchEvent(new Event('submit'));
            }
        });
    }

    /**
     * Conecta ao endpoint SSE
     */
    function conectarSSE() {
        if (eventSource) {
            eventSource.close();
        }

        const url = `/chat/stream`;
        eventSource = new EventSource(url);

        eventSource.onopen = () => {
            console.log('[Chat Widget] SSE conectado');
        };

        eventSource.onmessage = (event) => {
            try {
                const mensagem = JSON.parse(event.data);
                console.log('[Chat Widget] Mensagem recebida:', mensagem);

                // Processar mensagem
                processarMensagemSSE(mensagem);
            } catch (erro) {
                console.error('[Chat Widget] Erro ao processar mensagem:', erro);
            }
        };

        eventSource.onerror = (erro) => {
            console.error('[Chat Widget] Erro SSE:', erro);
        };
    }

    /**
     * Processa mensagem recebida via SSE
     */
    function processarMensagemSSE(mensagem) {
        // Se é mensagem da conversa atual, adicionar na UI
        if (conversaAtual && mensagem.sala_id === conversaAtual.sala_id) {
            adicionarMensagemUI(mensagem);
        }

        // Atualizar preview na lista de conversas
        atualizarPreviewConversa(mensagem.sala_id, mensagem);

        // Atualizar badge se não for mensagem própria
        if (mensagem.usuario_id !== usuarioId) {
            incrementarBadge();

            // Mostrar notificação se widget estiver fechado
            if (!elementos.widgetPanel.classList.contains('show')) {
                mostrarNotificacao(mensagem);
            }
        }
    }

    /**
     * Carrega lista de conversas
     */
    async function carregarConversas(offset = 0) {
        try {
            const response = await fetch(`/chat/conversas?limit=12&offset=${offset}`);
            const data = await response.json();

            if (data.success) {
                if (offset === 0) {
                    conversas = data.conversas;
                    renderizarConversas();
                } else {
                    conversas = conversas.concat(data.conversas);
                    adicionarConversasNaLista(data.conversas);
                }

                conversasOffset = offset + data.conversas.length;

                // Mostrar/esconder botão "Carregar mais"
                if (data.conversas.length === 12) {
                    elementos.loadMoreContainer.style.display = 'block';
                } else {
                    elementos.loadMoreContainer.style.display = 'none';
                }
            }
        } catch (erro) {
            console.error('[Chat Widget] Erro ao carregar conversas:', erro);
        }
    }

    /**
     * Renderiza lista completa de conversas
     */
    function renderizarConversas() {
        elementos.conversationsList.innerHTML = '';

        if (conversas.length === 0) {
            elementos.conversationsList.innerHTML = `
                <div class="text-center text-muted p-3">
                    <i class="bi bi-chat-dots"></i>
                    <p class="mb-0 small">Nenhuma conversa ainda</p>
                </div>
            `;
            return;
        }

        adicionarConversasNaLista(conversas);
    }

    /**
     * Adiciona conversas na lista
     */
    function adicionarConversasNaLista(listaConversas) {
        listaConversas.forEach(conversa => {
            const div = document.createElement('div');
            div.className = 'chat-conversation-item';
            div.setAttribute('data-sala-id', conversa.sala_id);
            div.onclick = () => abrirConversa(conversa);

            const badgeHtml = conversa.nao_lidas > 0
                ? `<span class="chat-conversation-badge">${conversa.nao_lidas}</span>`
                : '';

            const preview = conversa.ultima_mensagem
                ? escapeHtml(conversa.ultima_mensagem).substring(0, 30) + '...'
                : 'Nenhuma mensagem ainda';

            const tempo = conversa.ultima_mensagem_data
                ? formatarTempoRelativo(conversa.ultima_mensagem_data)
                : '';

            div.innerHTML = `
                <div class="chat-conversation-info">
                    <div class="chat-conversation-name">
                        ${escapeHtml(conversa.outro_usuario_nome)}
                    </div>
                    <div class="chat-conversation-preview">
                        ${preview}
                    </div>
                </div>
                <div class="chat-conversation-meta">
                    <div>${tempo}</div>
                    ${badgeHtml}
                </div>
            `;

            elementos.conversationsList.appendChild(div);
        });
    }

    /**
     * Abre conversa com usuário
     */
    async function abrirConversa(conversa) {
        conversaAtual = {
            sala_id: conversa.sala_id,
            outro_usuario_id: conversa.outro_usuario_id,
            outro_usuario_nome: conversa.outro_usuario_nome,
            outro_usuario_email: conversa.outro_usuario_email
        };

        // Atualiza UI
        elementos.emptyState.style.display = 'none';
        elementos.activeState.style.display = 'flex';
        elementos.activeUserName.textContent = conversa.outro_usuario_nome;
        elementos.activeUserEmail.textContent = conversa.outro_usuario_email || '';
        elementos.currentSalaIdInput.value = conversa.sala_id;

        // Marca item como ativo na lista
        document.querySelectorAll('.chat-conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-sala-id="${conversa.sala_id}"]`)?.classList.add('active');

        // Carrega mensagens
        await carregarMensagens(conversa.sala_id);

        // Marca como lida
        marcarComoLida(conversa.sala_id);

        // Foca no input
        elementos.messageInput.focus();
    }

    /**
     * Carrega mensagens de uma sala
     */
    async function carregarMensagens(salaId) {
        try {
            const response = await fetch(`/chat/mensagens/${salaId}?limit=50`);
            const data = await response.json();

            if (data.success) {
                elementos.messagesContainer.innerHTML = '';
                data.mensagens.forEach(msg => {
                    adicionarMensagemUI(msg, false);
                });
                scrollToBottom();
            }
        } catch (erro) {
            console.error('[Chat Widget] Erro ao carregar mensagens:', erro);
        }
    }

    /**
     * Adiciona mensagem na UI
     */
    function adicionarMensagemUI(mensagem, animate = true) {
        // Verificar duplicatas
        const existe = document.querySelector(`[data-message-id="${mensagem.id}"]`);
        if (existe) return;

        const div = document.createElement('div');
        div.className = mensagem.usuario_id === usuarioId ? 'chat-message own' : 'chat-message other';
        div.setAttribute('data-message-id', mensagem.id);

        // Aplicar formatação markdown
        const textoFormatado = aplicarFormatacaoMarkdown(escapeHtml(mensagem.mensagem));

        div.innerHTML = `
            <div class="chat-message-text">${textoFormatado}</div>
            <div class="chat-message-time">${formatarHora(mensagem.data_envio)}</div>
        `;

        elementos.messagesContainer.appendChild(div);

        if (animate) {
            scrollToBottom();
        }
    }

    /**
     * Aplica formatação markdown lite
     */
    function aplicarFormatacaoMarkdown(texto) {
        // ***texto*** = negrito + itálico
        texto = texto.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');

        // **texto** = negrito
        texto = texto.replace(/\*\*(.+?)\*\*\/g, '<strong>$1</strong>');

        // *texto* = itálico
        texto = texto.replace(/\*(.+?)\*/g, '<em>$1</em>');

        return texto;
    }

    /**
     * Envia mensagem
     */
    async function enviarMensagem(event) {
        event.preventDefault();

        const mensagem = elementos.messageInput.value.trim();
        const salaId = elementos.currentSalaIdInput.value;

        if (!mensagem || !salaId) return;

        try {
            const response = await fetch('/chat/enviar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    sala_id: salaId,
                    mensagem: mensagem
                })
            });

            const data = await response.json();

            if (data.success) {
                // Limpar input
                elementos.messageInput.value = '';
                elementos.messageInput.style.height = 'auto';

                // Foca novamente
                elementos.messageInput.focus();

                // Nota: Mensagem chegará via SSE e será adicionada automaticamente
            } else {
                if (window.exibirToast) {
                    const erro = data.erros ? Object.values(data.erros).join(', ') : data.erro;
                    window.exibirToast(erro, 'danger');
                }
            }
        } catch (erro) {
            console.error('[Chat Widget] Erro ao enviar mensagem:', erro);
            if (window.exibirToast) {
                window.exibirToast('Erro ao enviar mensagem', 'danger');
            }
        }
    }

    /**
     * Busca usuários (autocomplete)
     */
    async function buscarUsuarios(query) {
        try {
            const response = await fetch(`/chat/buscar-usuarios?q=${encodeURIComponent(query)}&limit=5`);
            const data = await response.json();

            if (data.success && data.usuarios.length > 0) {
                mostrarSugestoes(data.usuarios);
            } else {
                esconderSugestoes();
            }
        } catch (erro) {
            console.error('[Chat Widget] Erro ao buscar usuários:', erro);
        }
    }

    /**
     * Mostra sugestões de autocomplete
     */
    function mostrarSugestoes(usuarios) {
        elementos.searchSuggestions.innerHTML = '';

        usuarios.forEach(usuario => {
            const div = document.createElement('div');
            div.className = 'chat-search-suggestion-item';
            div.onclick = () => iniciarChatComUsuario(usuario.id);

            div.innerHTML = `
                <div><strong>${escapeHtml(usuario.nome)}</strong></div>
                <small class="text-muted">${escapeHtml(usuario.email)}</small>
            `;

            elementos.searchSuggestions.appendChild(div);
        });

        elementos.searchSuggestions.classList.add('show');
    }

    /**
     * Esconde sugestões
     */
    function esconderSugestoes() {
        elementos.searchSuggestions.classList.remove('show');
    }

    /**
     * Inicia chat com usuário
     */
    async function iniciarChatComUsuario(outroUsuarioId) {
        esconderSugestoes();
        elementos.searchInput.value = '';

        try {
            const response = await fetch('/chat/iniciar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    outro_usuario_id: outroUsuarioId
                })
            });

            const data = await response.json();

            if (data.success) {
                // Adicionar na lista se não existir
                const existeNaLista = conversas.find(c => c.sala_id === data.sala_id);
                if (!existeNaLista) {
                    conversas.unshift({
                        sala_id: data.sala_id,
                        outro_usuario_id: data.outro_usuario.id,
                        outro_usuario_nome: data.outro_usuario.nome,
                        outro_usuario_email: data.outro_usuario.email,
                        nao_lidas: 0,
                        ultima_mensagem: null,
                        ultima_mensagem_data: null
                    });
                    renderizarConversas();
                }

                // Abrir conversa
                abrirConversa({
                    sala_id: data.sala_id,
                    outro_usuario_id: data.outro_usuario.id,
                    outro_usuario_nome: data.outro_usuario.nome,
                    outro_usuario_email: data.outro_usuario.email
                });
            }
        } catch (erro) {
            console.error('[Chat Widget] Erro ao iniciar chat:', erro);
        }
    }

    /**
     * Marca sala como lida
     */
    async function marcarComoLida(salaId) {
        try {
            await fetch(`/chat/marcar-lida/${salaId}`, {
                method: 'POST'
            });

            // Atualizar badge da conversa
            const conversa = conversas.find(c => c.sala_id === salaId);
            if (conversa) {
                conversa.nao_lidas = 0;
                renderizarConversas();
            }

            // Recalcular badge total
            recalcularBadgeTotal();
        } catch (erro) {
            console.error('[Chat Widget] Erro ao marcar como lida:', erro);
        }
    }

    /**
     * Utilitários
     */

    function scrollToBottom() {
        elementos.messagesContainer.scrollTop = elementos.messagesContainer.scrollHeight;
    }

    function escapeHtml(texto) {
        const div = document.createElement('div');
        div.textContent = texto;
        return div.innerHTML;
    }

    function formatarHora(isoString) {
        const data = new Date(isoString);
        return data.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function formatarTempoRelativo(isoString) {
        const data = new Date(isoString);
        const agora = new Date();
        const diffMs = agora - data;
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 1) return 'Agora';
        if (diffMins < 60) return `${diffMins}m`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h`;
        return data.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' });
    }

    function incrementarBadge() {
        const total = parseInt(elementos.badge.textContent || '0') + 1;
        elementos.badge.textContent = total;
        elementos.badge.classList.add('show');
    }

    function recalcularBadgeTotal() {
        const total = conversas.reduce((sum, c) => sum + c.nao_lidas, 0);
        if (total > 0) {
            elementos.badge.textContent = total;
            elementos.badge.classList.add('show');
        } else {
            elementos.badge.textContent = '';
            elementos.badge.classList.remove('show');
        }
    }

    function atualizarPreviewConversa(salaId, mensagem) {
        const conversa = conversas.find(c => c.sala_id === salaId);
        if (conversa) {
            conversa.ultima_mensagem = mensagem.mensagem;
            conversa.ultima_mensagem_data = mensagem.data_envio;

            // Se não é do usuário atual, incrementar não lidas
            if (mensagem.usuario_id !== usuarioId && (!conversaAtual || conversaAtual.sala_id !== salaId)) {
                conversa.nao_lidas = (conversa.nao_lidas || 0) + 1;
            }

            renderizarConversas();
        }
    }

    function mostrarNotificacao(mensagem) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Nova mensagem', {
                body: `${mensagem.usuario_nome}: ${mensagem.mensagem.substring(0, 50)}`,
                icon: '/static/img/chat-icon.png'
            });
        }
    }

    function fecharChatAtivo() {
        conversaAtual = null;
        elementos.activeState.style.display = 'none';
        elementos.emptyState.style.display = 'flex';
        elementos.messagesContainer.innerHTML = '';

        // Remove active da lista
        document.querySelectorAll('.chat-conversation-item').forEach(item => {
            item.classList.remove('active');
        });
    }

    function destruir() {
        if (eventSource) {
            eventSource.close();
        }
    }

    // Cleanup ao sair da página
    window.addEventListener('beforeunload', destruir);

    // API pública
    return {
        init,
        destruir,
        enviarMensagem,
        carregarMaisConversas: () => carregarConversas(conversasOffset),
        fecharChatAtivo
    };
})();

// Expor globalmente
window.chatWidget = chatWidget;

/**
 * Funções globais chamadas pelo HTML
 */

function toggleChatWidget() {
    const panel = document.getElementById('chat-widget-panel');
    const button = document.getElementById('chat-widget-button');

    if (panel.classList.contains('show')) {
        panel.classList.remove('show');
        button.style.display = 'flex';
    } else {
        panel.classList.add('show');
        button.style.display = 'none';

        // Pedir permissão de notificações
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
}

function carregarMaisConversas() {
    window.chatWidget.carregarMaisConversas();
}

function enviarMensagem(event) {
    window.chatWidget.enviarMensagem(event);
}

function fecharChatAtivo() {
    window.chatWidget.fecharChatAtivo();
}
```

---

## 🧪 Camada 8: Testes

### 8.1 Fixtures de Teste (`tests/conftest.py`)

Adicionar fixtures específicas para chat ao arquivo existente:

```python
import pytest
from datetime import datetime
from repo import chat_sala_repo, chat_participante_repo, chat_mensagem_repo
from util.datetime_util import agora

@pytest.fixture
def sala_teste(cliente_autenticado, admin_autenticado, criar_usuario):
    """Cria uma sala de chat entre dois usuários para testes."""
    # Criar segundo usuário de teste
    usuario2 = criar_usuario("maria@teste.com", "Maria", "Maria@123")

    # Criar sala entre admin (id=1) e usuario2
    sala_id = chat_sala_repo.gerar_sala_id(1, usuario2["id"])
    sala = chat_sala_repo.criar_ou_obter_sala(1, usuario2["id"])

    yield {
        "sala_id": sala_id,
        "sala": sala,
        "usuario1_id": 1,  # admin
        "usuario2_id": usuario2["id"]
    }

    # Cleanup: remover sala (cascade deleta participantes e mensagens)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_sala WHERE id = ?", (sala_id,))

@pytest.fixture
def mensagens_teste(sala_teste):
    """Cria mensagens de teste em uma sala."""
    mensagens = []

    # Mensagem do usuario1
    msg1 = chat_mensagem_repo.inserir(
        sala_id=sala_teste["sala_id"],
        usuario_id=sala_teste["usuario1_id"],
        mensagem="Olá, tudo bem?"
    )
    mensagens.append(msg1)

    # Mensagem do usuario2
    msg2 = chat_mensagem_repo.inserir(
        sala_id=sala_teste["sala_id"],
        usuario_id=sala_teste["usuario2_id"],
        mensagem="Tudo sim, e você?"
    )
    mensagens.append(msg2)

    # Mensagem com formatação
    msg3 = chat_mensagem_repo.inserir(
        sala_id=sala_teste["sala_id"],
        usuario_id=sala_teste["usuario1_id"],
        mensagem="Isso é **negrito**, isso é *itálico* e isso é ***ambos***!"
    )
    mensagens.append(msg3)

    return mensagens
```

### 8.2 Testes de Repositório (`tests/test_chat_repo.py`)

```python
import pytest
from repo import chat_sala_repo, chat_participante_repo, chat_mensagem_repo
from util.datetime_util import agora

@pytest.mark.chat
class TestChatSalaRepo:

    def test_gerar_sala_id_deterministico(self):
        """Testa se sala_id é sempre o mesmo independente da ordem."""
        sala_id_1 = chat_sala_repo.gerar_sala_id(3, 7)
        sala_id_2 = chat_sala_repo.gerar_sala_id(7, 3)

        assert sala_id_1 == sala_id_2
        assert sala_id_1 == "3_7"

    def test_criar_ou_obter_sala_nova(self, admin_autenticado, criar_usuario):
        """Testa criação de nova sala."""
        usuario2 = criar_usuario("joao@teste.com", "João", "Joao@123")

        sala = chat_sala_repo.criar_ou_obter_sala(1, usuario2["id"])

        assert sala is not None
        assert sala.id == chat_sala_repo.gerar_sala_id(1, usuario2["id"])
        assert sala.criada_em is not None
        assert sala.ultima_atividade is not None

    def test_criar_ou_obter_sala_existente(self, sala_teste):
        """Testa que obter_ou_criar retorna sala existente."""
        sala = chat_sala_repo.criar_ou_obter_sala(
            sala_teste["usuario1_id"],
            sala_teste["usuario2_id"]
        )

        assert sala.id == sala_teste["sala_id"]

    def test_obter_por_id(self, sala_teste):
        """Testa obtenção de sala por ID."""
        sala = chat_sala_repo.obter_por_id(sala_teste["sala_id"])

        assert sala is not None
        assert sala.id == sala_teste["sala_id"]

    def test_atualizar_ultima_atividade(self, sala_teste):
        """Testa atualização do timestamp de última atividade."""
        import time
        time.sleep(0.1)  # Garantir timestamp diferente

        sucesso = chat_sala_repo.atualizar_ultima_atividade(sala_teste["sala_id"])

        assert sucesso is True
        sala_atualizada = chat_sala_repo.obter_por_id(sala_teste["sala_id"])
        assert sala_atualizada.ultima_atividade > sala_teste["sala"].ultima_atividade


@pytest.mark.chat
class TestChatParticipanteRepo:

    def test_adicionar_participante(self, sala_teste):
        """Testa adição de participante."""
        participante = chat_participante_repo.obter_por_sala_e_usuario(
            sala_teste["sala_id"],
            sala_teste["usuario1_id"]
        )

        assert participante is not None
        assert participante.sala_id == sala_teste["sala_id"]
        assert participante.usuario_id == sala_teste["usuario1_id"]

    def test_listar_participantes(self, sala_teste):
        """Testa listagem de participantes de uma sala."""
        participantes = chat_participante_repo.listar_por_sala(sala_teste["sala_id"])

        assert len(participantes) == 2
        ids = [p.usuario_id for p in participantes]
        assert sala_teste["usuario1_id"] in ids
        assert sala_teste["usuario2_id"] in ids

    def test_atualizar_ultima_leitura(self, sala_teste):
        """Testa atualização de última leitura."""
        sucesso = chat_participante_repo.atualizar_ultima_leitura(
            sala_teste["sala_id"],
            sala_teste["usuario1_id"]
        )

        assert sucesso is True
        participante = chat_participante_repo.obter_por_sala_e_usuario(
            sala_teste["sala_id"],
            sala_teste["usuario1_id"]
        )
        assert participante.ultima_leitura is not None

    def test_contar_mensagens_nao_lidas(self, sala_teste, mensagens_teste):
        """Testa contagem de mensagens não lidas."""
        # Marcar primeira mensagem como lida
        chat_participante_repo.atualizar_ultima_leitura(
            sala_teste["sala_id"],
            sala_teste["usuario2_id"]
        )

        # Deve ter mensagens não lidas do usuario1 para usuario2
        nao_lidas = chat_participante_repo.contar_mensagens_nao_lidas(
            sala_teste["sala_id"],
            sala_teste["usuario2_id"]
        )

        assert nao_lidas > 0


@pytest.mark.chat
class TestChatMensagemRepo:

    def test_inserir_mensagem(self, sala_teste):
        """Testa inserção de mensagem."""
        mensagem = chat_mensagem_repo.inserir(
            sala_id=sala_teste["sala_id"],
            usuario_id=sala_teste["usuario1_id"],
            mensagem="Teste de mensagem"
        )

        assert mensagem is not None
        assert mensagem.id > 0
        assert mensagem.mensagem == "Teste de mensagem"
        assert mensagem.sala_id == sala_teste["sala_id"]
        assert mensagem.usuario_id == sala_teste["usuario1_id"]
        assert mensagem.data_envio is not None
        assert mensagem.lida_em is None

    def test_listar_mensagens_por_sala(self, sala_teste, mensagens_teste):
        """Testa listagem de mensagens de uma sala."""
        mensagens = chat_mensagem_repo.listar_por_sala(
            sala_id=sala_teste["sala_id"],
            limit=50,
            offset=0
        )

        assert len(mensagens) == 3
        assert mensagens[0].id < mensagens[1].id  # Ordem crescente

    def test_listar_mensagens_com_paginacao(self, sala_teste, mensagens_teste):
        """Testa paginação de mensagens."""
        # Primeira página
        mensagens_p1 = chat_mensagem_repo.listar_por_sala(
            sala_id=sala_teste["sala_id"],
            limit=2,
            offset=0
        )

        # Segunda página
        mensagens_p2 = chat_mensagem_repo.listar_por_sala(
            sala_id=sala_teste["sala_id"],
            limit=2,
            offset=2
        )

        assert len(mensagens_p1) == 2
        assert len(mensagens_p2) == 1
        assert mensagens_p1[0].id != mensagens_p2[0].id

    def test_marcar_mensagens_como_lidas(self, sala_teste, mensagens_teste):
        """Testa marcação de mensagens como lidas."""
        sucesso = chat_mensagem_repo.marcar_como_lidas(
            sala_id=sala_teste["sala_id"],
            usuario_id=sala_teste["usuario2_id"]
        )

        assert sucesso is True

        # Verificar que mensagens foram marcadas
        mensagens = chat_mensagem_repo.listar_por_sala(
            sala_id=sala_teste["sala_id"],
            limit=50,
            offset=0
        )

        for msg in mensagens:
            if msg.usuario_id != sala_teste["usuario2_id"]:
                assert msg.lida_em is not None


### 8.3 Testes de Rotas (`tests/test_chat_routes.py`)

```python
import pytest
import json
from fastapi import status

@pytest.mark.chat
class TestChatRoutes:

    def test_criar_ou_obter_sala_sucesso(self, cliente_autenticado, criar_usuario):
        """Testa criação de sala via API."""
        usuario2 = criar_usuario("pedro@teste.com", "Pedro", "Pedro@123")

        response = cliente_autenticado.post(
            "/chat/salas",
            data={"outro_usuario_id": usuario2["id"]}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "sala_id" in data
        assert data["sala_id"] == f"1_{usuario2['id']}"

    def test_criar_sala_usuario_invalido(self, cliente_autenticado):
        """Testa criação de sala com usuário inexistente."""
        response = cliente_autenticado.post(
            "/chat/salas",
            data={"outro_usuario_id": 99999}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_criar_sala_consigo_mesmo(self, cliente_autenticado):
        """Testa que não é possível criar sala consigo mesmo."""
        response = cliente_autenticado.post(
            "/chat/salas",
            data={"outro_usuario_id": 1}  # ID do próprio usuário logado
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_listar_conversas(self, cliente_autenticado, sala_teste, mensagens_teste):
        """Testa listagem de conversas do usuário."""
        response = cliente_autenticado.get("/chat/conversas?limit=12&offset=0")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "sala_id" in data[0]
        assert "outro_usuario" in data[0]
        assert "ultima_mensagem" in data[0]
        assert "nao_lidas" in data[0]

    def test_listar_mensagens_sala(self, cliente_autenticado, sala_teste, mensagens_teste):
        """Testa listagem de mensagens de uma sala."""
        response = cliente_autenticado.get(
            f"/chat/mensagens/{sala_teste['sala_id']}?limit=50&offset=0"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert "id" in data[0]
        assert "mensagem" in data[0]
        assert "usuario_id" in data[0]
        assert "data_envio" in data[0]

    def test_enviar_mensagem_sucesso(self, cliente_autenticado, sala_teste):
        """Testa envio de mensagem."""
        response = cliente_autenticado.post(
            "/chat/mensagens",
            data={
                "sala_id": sala_teste["sala_id"],
                "mensagem": "Nova mensagem de teste"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["mensagem"] == "Nova mensagem de teste"

    def test_enviar_mensagem_sala_inexistente(self, cliente_autenticado):
        """Testa envio para sala inexistente."""
        response = cliente_autenticado.post(
            "/chat/mensagens",
            data={
                "sala_id": "999_1000",
                "mensagem": "Teste"
            }
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_marcar_como_lidas(self, cliente_autenticado, sala_teste, mensagens_teste):
        """Testa marcação de mensagens como lidas."""
        response = cliente_autenticado.post(
            f"/chat/mensagens/lidas/{sala_teste['sala_id']}"
        )

        assert response.status_code == status.HTTP_200_OK

    def test_buscar_usuarios(self, cliente_autenticado, criar_usuario):
        """Testa busca de usuários por termo."""
        criar_usuario("carlos@teste.com", "Carlos Silva", "Carlos@123")
        criar_usuario("carla@teste.com", "Carla Santos", "Carla@123")

        response = cliente_autenticado.get("/chat/usuarios/buscar?q=carl")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        assert "id" in data[0]
        assert "nome" in data[0]
        assert "email" in data[0]

    def test_contar_nao_lidas_total(self, cliente_autenticado, sala_teste, mensagens_teste):
        """Testa contagem total de mensagens não lidas."""
        response = cliente_autenticado.get("/chat/mensagens/nao-lidas/total")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert data["total"] >= 0

    def test_stream_sse(self, cliente_autenticado):
        """Testa conexão SSE (apenas verifica que endpoint existe e retorna stream)."""
        response = cliente_autenticado.get("/chat/stream", stream=True)

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"


### 8.4 Testes de ChatManager (`tests/test_chat_manager.py`)

```python
import pytest
import asyncio
from util.chat_manager import ChatManager

@pytest.mark.chat
@pytest.mark.asyncio
class TestChatManager:

    async def test_conectar_usuario(self):
        """Testa conexão de usuário ao ChatManager."""
        manager = ChatManager()
        queue = await manager.connect(1)

        assert queue is not None
        assert 1 in manager._connections
        assert 1 in manager._active_connections

        await manager.disconnect(1)

    async def test_desconectar_usuario(self):
        """Testa desconexão de usuário."""
        manager = ChatManager()
        await manager.connect(1)
        await manager.disconnect(1)

        assert 1 not in manager._active_connections

    async def test_broadcast_para_sala(self):
        """Testa broadcast de mensagem para sala."""
        manager = ChatManager()

        # Conectar dois usuários
        queue1 = await manager.connect(3)
        queue2 = await manager.connect(7)

        # Enviar mensagem para sala "3_7"
        mensagem = {
            "tipo": "nova_mensagem",
            "sala_id": "3_7",
            "mensagem": "Teste",
            "usuario_id": 3
        }

        await manager.broadcast_para_sala("3_7", mensagem)

        # Verificar que ambos receberam
        msg1 = await asyncio.wait_for(queue1.get(), timeout=1.0)
        msg2 = await asyncio.wait_for(queue2.get(), timeout=1.0)

        assert msg1 == mensagem
        assert msg2 == mensagem

        await manager.disconnect(3)
        await manager.disconnect(7)

    async def test_broadcast_usuario_desconectado(self):
        """Testa que broadcast não falha se usuário desconectado."""
        manager = ChatManager()

        # Conectar apenas usuário 3
        queue3 = await manager.connect(3)

        # Tentar broadcast para sala "3_7" (usuário 7 não conectado)
        mensagem = {"tipo": "teste", "conteudo": "Teste"}

        await manager.broadcast_para_sala("3_7", mensagem)

        # Usuário 3 deve receber normalmente
        msg = await asyncio.wait_for(queue3.get(), timeout=1.0)
        assert msg == mensagem

        await manager.disconnect(3)


### 8.5 Executar Testes

```bash
# Executar todos os testes de chat
pytest -m chat -v

# Executar testes de um arquivo específico
pytest tests/test_chat_repo.py -v

# Executar teste específico
pytest tests/test_chat_routes.py::TestChatRoutes::test_criar_ou_obter_sala_sucesso -v

# Executar com cobertura
pytest --cov=repo --cov=routes --cov=util -m chat --cov-report=html
```

---

## ✅ Camada 9: Checklist de Implementação

Siga esta ordem rigorosa para implementação:

### Fase 1: Estrutura Base (20 min)

- [ ] **1.1** Criar arquivo `sql/chat_sala_sql.py`
- [ ] **1.2** Criar arquivo `sql/chat_participante_sql.py`
- [ ] **1.3** Criar arquivo `sql/chat_mensagem_sql.py`
- [ ] **1.4** Criar arquivo `model/chat_sala_model.py`
- [ ] **1.5** Criar arquivo `model/chat_participante_model.py`
- [ ] **1.6** Criar arquivo `model/chat_mensagem_model.py`

### Fase 2: Camada de Dados (30 min)

- [ ] **2.1** Criar arquivo `repo/chat_sala_repo.py`
  - [ ] Implementar `criar_tabela()`
  - [ ] Implementar `gerar_sala_id()`
  - [ ] Implementar `criar_ou_obter_sala()`
  - [ ] Implementar `obter_por_id()`
  - [ ] Implementar `atualizar_ultima_atividade()`
  - [ ] Implementar `_row_to_sala()`

- [ ] **2.2** Criar arquivo `repo/chat_participante_repo.py`
  - [ ] Implementar `criar_tabela()`
  - [ ] Implementar `adicionar_participante()`
  - [ ] Implementar `listar_por_sala()`
  - [ ] Implementar `obter_por_sala_e_usuario()`
  - [ ] Implementar `atualizar_ultima_leitura()`
  - [ ] Implementar `contar_mensagens_nao_lidas()`
  - [ ] Implementar `_row_to_participante()`

- [ ] **2.3** Criar arquivo `repo/chat_mensagem_repo.py`
  - [ ] Implementar `criar_tabela()`
  - [ ] Implementar `inserir()`
  - [ ] Implementar `listar_por_sala()`
  - [ ] Implementar `marcar_como_lidas()`
  - [ ] Implementar `contar_por_sala()`
  - [ ] Implementar `_row_to_mensagem()`

### Fase 3: DTOs (15 min)

- [ ] **3.1** Criar arquivo `dtos/chat_dto.py`
  - [ ] Implementar `CriarSalaDTO`
  - [ ] Implementar `EnviarMensagemDTO`
  - [ ] Implementar `ConversaResumoDTO`
  - [ ] Implementar `UsuarioBuscaDTO`

### Fase 4: ChatManager (25 min)

- [ ] **4.1** Criar arquivo `util/chat_manager.py`
  - [ ] Implementar `__init__()`
  - [ ] Implementar `connect()`
  - [ ] Implementar `disconnect()`
  - [ ] Implementar `broadcast_para_sala()`
  - [ ] Implementar `is_connected()`
  - [ ] Criar instância singleton global

### Fase 5: Rotas Backend (40 min)

- [ ] **5.1** Criar arquivo `routes/chat_routes.py`
  - [ ] Configurar `APIRouter` com prefix `/chat`
  - [ ] Implementar `GET /stream` (SSE)
  - [ ] Implementar `POST /salas` (criar/obter sala)
  - [ ] Implementar `GET /conversas` (listar conversas)
  - [ ] Implementar `GET /mensagens/{sala_id}` (listar mensagens)
  - [ ] Implementar `POST /mensagens` (enviar mensagem)
  - [ ] Implementar `POST /mensagens/lidas/{sala_id}` (marcar lidas)
  - [ ] Implementar `GET /usuarios/buscar` (buscar usuários)
  - [ ] Implementar `GET /mensagens/nao-lidas/total` (contar não lidas)

- [ ] **5.2** Registrar router em `main.py`
  - [ ] Importar `chat_routes`
  - [ ] `app.include_router(chat_routes.router)`
  - [ ] Chamar `criar_tabela()` dos 3 repos no startup

### Fase 6: Frontend - HTML (30 min)

- [ ] **6.1** Criar arquivo `templates/components/chat_widget.html`
  - [ ] Estrutura HTML do botão flutuante
  - [ ] Estrutura do painel expansível
  - [ ] Painel de conversas (esquerda 30%)
  - [ ] Campo de busca de usuários
  - [ ] Lista de conversas
  - [ ] Painel de mensagens (direita 70%)
  - [ ] Cabeçalho do chat ativo
  - [ ] Container de mensagens
  - [ ] Campo de entrada de mensagem
  - [ ] Botão "Carregar mais conversas"

### Fase 7: Frontend - CSS (40 min)

- [ ] **7.1** Criar arquivo `static/css/chat-widget.css`
  - [ ] Estilos do botão flutuante
  - [ ] Estilos do painel expansível
  - [ ] Estilos do painel de conversas
  - [ ] Estilos de cada item de conversa
  - [ ] Estilos do painel de mensagens
  - [ ] Estilos das bolhas de mensagem (enviada/recebida)
  - [ ] Estilos do campo de entrada
  - [ ] Estados vazios e loading
  - [ ] Responsividade mobile

- [ ] **7.2** Incluir CSS em `base_privada.html`
  - [ ] `<link rel="stylesheet" href="{{ url_for('static', path='/css/chat-widget.css') }}">`

### Fase 8: Frontend - JavaScript (60 min)

- [ ] **8.1** Criar arquivo `static/js/chat-widget.js`
  - [ ] Definir estrutura de módulo IIFE
  - [ ] Implementar `init()`
  - [ ] Implementar `conectarSSE()`
  - [ ] Implementar `carregarConversas()`
  - [ ] Implementar `renderizarConversas()`
  - [ ] Implementar `buscarUsuarios()` com debounce
  - [ ] Implementar `abrirChat()`
  - [ ] Implementar `carregarMensagens()`
  - [ ] Implementar `renderizarMensagens()`
  - [ ] Implementar `enviarMensagem()`
  - [ ] Implementar `aplicarFormatacaoMarkdown()`
  - [ ] Implementar `marcarComoLidas()`
  - [ ] Implementar `atualizarContadorNaoLidas()`
  - [ ] Implementar `processarMensagemSSE()`
  - [ ] Implementar `fecharChatAtivo()`
  - [ ] Implementar `destruir()`
  - [ ] Expor API pública

- [ ] **8.2** Implementar funções globais
  - [ ] `toggleChatWidget()`
  - [ ] `carregarMaisConversas()`
  - [ ] `enviarMensagem()`
  - [ ] `fecharChatAtivo()`

- [ ] **8.3** Incluir JS em `base_privada.html`
  - [ ] `<script src="{{ url_for('static', path='/js/chat-widget.js') }}" defer></script>`
  - [ ] `<script>document.addEventListener('DOMContentLoaded', () => chatWidget.init());</script>`

### Fase 9: Integração (20 min)

- [ ] **9.1** Incluir widget em `base_privada.html`
  - [ ] `{% include 'components/chat_widget.html' %}`

- [ ] **9.2** Verificar dependências
  - [ ] Bootstrap Icons carregado
  - [ ] Toasts funcionando
  - [ ] Modal de alerta disponível

### Fase 10: Testes (60 min)

- [ ] **10.1** Criar fixtures em `tests/conftest.py`
  - [ ] Fixture `sala_teste`
  - [ ] Fixture `mensagens_teste`

- [ ] **10.2** Criar `tests/test_chat_repo.py`
  - [ ] Testes de `chat_sala_repo`
  - [ ] Testes de `chat_participante_repo`
  - [ ] Testes de `chat_mensagem_repo`

- [ ] **10.3** Criar `tests/test_chat_routes.py`
  - [ ] Testes de todas as rotas
  - [ ] Testes de validação
  - [ ] Testes de autorização

- [ ] **10.4** Criar `tests/test_chat_manager.py`
  - [ ] Testes de conexão/desconexão
  - [ ] Testes de broadcast

- [ ] **10.5** Executar testes
  - [ ] `pytest -m chat -v`
  - [ ] Verificar 100% dos testes passando

### Fase 11: Ajustes Finais (30 min)

- [ ] **11.1** Testar no navegador
  - [ ] Abrir painel do chat
  - [ ] Buscar usuário
  - [ ] Criar nova conversa
  - [ ] Enviar mensagens
  - [ ] Testar formatação markdown
  - [ ] Testar Shift+Enter (quebra linha)
  - [ ] Testar Enter (envia mensagem)
  - [ ] Carregar mais conversas
  - [ ] Marcar como lidas
  - [ ] Fechar chat ativo
  - [ ] Verificar contador de não lidas
  - [ ] Testar em abas múltiplas (SSE)

- [ ] **11.2** Testar responsividade
  - [ ] Desktop (1920px)
  - [ ] Tablet (768px)
  - [ ] Mobile (375px)

- [ ] **11.3** Verificar logs
  - [ ] Nenhum erro no console do navegador
  - [ ] Nenhum erro nos logs do servidor

---

## 🚀 Camada 10: Deploy e Produção

### 10.1 Configurações de Produção

**Variáveis de Ambiente (.env.production):**

```bash
# Modo de execução
RUNNING_MODE=Production

# SSE Settings
SSE_RETRY_TIMEOUT=5000  # ms
SSE_PING_INTERVAL=30000  # ms

# Chat Settings
CHAT_MENSAGENS_POR_PAGINA=50
CHAT_CONVERSAS_POR_PAGINA=12
CHAT_MAX_CARACTERES_MENSAGEM=5000

# Rate Limiting (recomendado adicionar)
CHAT_RATE_LIMIT_MENSAGENS=30  # msgs por minuto por usuário
```

### 10.2 Nginx Configuration

**Configuração para SSE com proxy reverso:**

```nginx
server {
    listen 80;
    server_name seudominio.com;

    # Configurações gerais
    client_max_body_size 10M;

    # SSE specific - CRITICAL
    location /chat/stream {
        proxy_pass http://127.0.0.1:8400;
        proxy_http_version 1.1;

        # Configurações SSE
        proxy_set_header Connection '';
        proxy_set_header Cache-Control 'no-cache';

        # Headers padrão
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts longos para SSE
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;

        # Buffering DESLIGADO (crítico para SSE)
        proxy_buffering off;
        proxy_cache off;

        # Chunked transfer encoding
        chunked_transfer_encoding on;

        # Flush imediato
        gzip off;
    }

    # Outras rotas do chat
    location /chat {
        proxy_pass http://127.0.0.1:8400;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Aplicação geral
    location / {
        proxy_pass http://127.0.0.1:8400;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 10.3 Systemd Service

**Arquivo: `/etc/systemd/system/defaultwebapp.service`**

```ini
[Unit]
Description=DefaultWebApp FastAPI Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/defaultwebapp
Environment="PATH=/var/www/defaultwebapp/venv/bin"
ExecStart=/var/www/defaultwebapp/venv/bin/python main.py
Restart=always
RestartSec=5

# Limites de recursos
LimitNOFILE=65536
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

**Comandos:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable defaultwebapp
sudo systemctl start defaultwebapp
sudo systemctl status defaultwebapp
```

### 10.4 Monitoramento

**Health Check do Chat:**

Adicionar endpoint de health check em `routes/chat_routes.py`:

```python
@router.get("/health")
async def chat_health():
    """Health check do sistema de chat."""
    from util.chat_manager import chat_manager

    conexoes_ativas = len(chat_manager._active_connections)

    return {
        "status": "healthy",
        "conexoes_ativas": conexoes_ativas,
        "timestamp": agora().isoformat()
    }
```

**Monitorar conexões SSE:**

```python
# Em util/chat_manager.py, adicionar método
def obter_estatisticas(self) -> dict:
    """Retorna estatísticas do chat."""
    return {
        "total_conexoes": len(self._connections),
        "usuarios_ativos": list(self._active_connections),
        "total_usuarios_ativos": len(self._active_connections)
    }
```

### 10.5 Backup do Banco

**Script de backup automático:**

```bash
#!/bin/bash
# /usr/local/bin/backup-chat.sh

BACKUP_DIR="/var/backups/defaultwebapp"
DB_PATH="/var/www/defaultwebapp/database.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup do banco
sqlite3 $DB_PATH ".backup $BACKUP_DIR/database_$DATE.db"

# Compactar
gzip $BACKUP_DIR/database_$DATE.db

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "database_*.db.gz" -mtime +7 -delete

echo "Backup concluído: database_$DATE.db.gz"
```

**Crontab:**
```bash
# Backup diário às 3h da manhã
0 3 * * * /usr/local/bin/backup-chat.sh >> /var/log/backup-chat.log 2>&1
```

### 10.6 Logs e Debug em Produção

**Configurar logging rotativo:**

```python
# util/logger_config.py - ajustar para produção
import logging
from logging.handlers import RotatingFileHandler

def configurar_logger_producao():
    logger = logging.getLogger("chat")
    logger.setLevel(logging.INFO)

    # Arquivo rotativo (10MB por arquivo, máximo 5 arquivos)
    handler = RotatingFileHandler(
        "logs/chat.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

chat_logger = configurar_logger_producao()
```

**Usar em util/chat_manager.py:**

```python
from util.logger_config import chat_logger

class ChatManager:
    async def connect(self, usuario_id: int):
        chat_logger.info(f"Usuário {usuario_id} conectado ao chat")
        # ...

    async def broadcast_para_sala(self, sala_id: str, mensagem: dict):
        chat_logger.info(f"Broadcast para sala {sala_id}: {mensagem.get('tipo')}")
        # ...
```

### 10.7 Segurança

**Rate Limiting por IP (opcional - requer middleware):**

```python
# util/rate_limiter.py
from fastapi import Request, HTTPException, status
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check_rate_limit(self, identifier: str):
        async with self._lock:
            now = datetime.now()
            window_start = now - timedelta(seconds=self.window_seconds)

            # Remover requisições antigas
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]

            # Verificar limite
            if len(self.requests[identifier]) >= self.max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Muitas requisições. Aguarde alguns segundos."
                )

            # Adicionar requisição atual
            self.requests[identifier].append(now)

# Instância global
mensagem_rate_limiter = RateLimiter(max_requests=30, window_seconds=60)
```

**Usar em routes/chat_routes.py:**

```python
@router.post("/mensagens")
@requer_autenticacao()
async def enviar_mensagem(request: Request, ...):
    # Rate limiting por usuário
    await mensagem_rate_limiter.check_rate_limit(f"user_{usuario_logado['id']}")
    # ... resto do código
```

### 10.8 Performance

**Otimizações recomendadas:**

1. **Índices no Banco de Dados:**

```sql
-- Índices para melhorar performance de consultas
CREATE INDEX IF NOT EXISTS idx_chat_mensagem_sala_data
ON chat_mensagem(sala_id, data_envio DESC);

CREATE INDEX IF NOT EXISTS idx_chat_mensagem_lida
ON chat_mensagem(sala_id, usuario_id, lida_em);

CREATE INDEX IF NOT EXISTS idx_chat_participante_usuario
ON chat_participante(usuario_id);

CREATE INDEX IF NOT EXISTS idx_chat_sala_atividade
ON chat_sala(ultima_atividade DESC);
```

2. **Cache de Conversas (Redis opcional):**

Se tiver muitos usuários, considere cachear a lista de conversas usando Redis:

```python
# util/cache_redis.py (opcional)
import redis
import json
from typing import Optional

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_conversas(usuario_id: int, conversas: list, ttl: int = 300):
    """Cacheia lista de conversas por 5 minutos."""
    key = f"conversas:{usuario_id}"
    redis_client.setex(key, ttl, json.dumps(conversas))

def obter_conversas_cache(usuario_id: int) -> Optional[list]:
    """Obtém conversas do cache."""
    key = f"conversas:{usuario_id}"
    data = redis_client.get(key)
    return json.loads(data) if data else None
```

---

## 🔧 Camada 11: Troubleshooting

### 11.1 SSE não está funcionando

**Sintomas:**
- EventSource fica em estado "connecting" infinitamente
- Mensagens não aparecem em tempo real
- Console mostra erro de conexão SSE

**Causas e Soluções:**

1. **Problema: Nginx com buffering ativado**
   ```bash
   # Verificar configuração
   sudo nginx -T | grep buffering
   ```
   **Solução:** Adicionar `proxy_buffering off;` na location `/chat/stream`

2. **Problema: Timeout muito curto**
   ```bash
   # Verificar timeouts
   sudo nginx -T | grep timeout
   ```
   **Solução:** Aumentar `proxy_read_timeout` e `proxy_send_timeout` para 86400s

3. **Problema: CORS bloqueando SSE**
   ```python
   # Em main.py, adicionar CORS
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:8400"],  # Ajustar conforme necessário
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

4. **Problema: Múltiplas instâncias da aplicação**

   SSE só funciona corretamente com uma única instância do FastAPI. Se usar múltiplos workers (gunicorn/uvicorn), use Redis Pub/Sub:

   ```python
   # util/chat_manager_redis.py
   import redis
   import asyncio
   import json

   redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
   pubsub = redis_client.pubsub()

   class ChatManagerRedis:
       def __init__(self):
           self._connections = {}
           self._active_connections = set()
           self._subscriber_task = None

       async def connect(self, usuario_id: int):
           queue = asyncio.Queue()
           self._connections[usuario_id] = queue
           self._active_connections.add(usuario_id)

           # Iniciar subscriber se necessário
           if not self._subscriber_task:
               self._subscriber_task = asyncio.create_task(self._redis_subscriber())

           return queue

       async def broadcast_para_sala(self, sala_id: str, mensagem: dict):
           # Publicar no Redis ao invés de broadcast direto
           redis_client.publish('chat_messages', json.dumps(mensagem))

       async def _redis_subscriber(self):
           pubsub.subscribe('chat_messages')
           while True:
               message = pubsub.get_message()
               if message and message['type'] == 'message':
                   data = json.loads(message['data'])
                   # Distribuir para conexões locais
                   for usuario_id in self._active_connections:
                       if usuario_id in self._connections:
                           await self._connections[usuario_id].put(data)
               await asyncio.sleep(0.1)
   ```

### 11.2 Mensagens não estão sendo entregues

**Sintomas:**
- Mensagem é enviada mas não aparece para o destinatário
- `POST /chat/mensagens` retorna sucesso mas SSE não recebe

**Diagnóstico:**

```python
# Adicionar logs em util/chat_manager.py
async def broadcast_para_sala(self, sala_id: str, mensagem_dict: dict):
    partes = sala_id.split("_")
    usuario1_id = int(partes[0])
    usuario2_id = int(partes[1])

    print(f"[DEBUG] Broadcasting para sala {sala_id}")
    print(f"[DEBUG] Usuários: {usuario1_id}, {usuario2_id}")
    print(f"[DEBUG] Conexões ativas: {self._active_connections}")

    for usuario_id in [usuario1_id, usuario2_id]:
        if usuario_id in self._connections:
            print(f"[DEBUG] Enviando para usuário {usuario_id}")
            await self._connections[usuario_id].put(mensagem_dict)
        else:
            print(f"[DEBUG] Usuário {usuario_id} NÃO está conectado")
```

**Soluções:**

1. Verificar que `sala_id` está no formato correto: `"menor_id_maior_id"`
2. Verificar que ambos os usuários têm conexão SSE ativa
3. Verificar que `broadcast_para_sala` está sendo chamado após `inserir()`

### 11.3 Formatação Markdown não está funcionando

**Sintomas:**
- Texto aparece com asteriscos (`**texto**`) ao invés de negrito

**Causa:** Função `aplicarFormatacaoMarkdown()` não está sendo chamada

**Solução:**

```javascript
// Em static/js/chat-widget.js, verificar função renderizarMensagens()
function renderizarMensagens(mensagens) {
    mensagens.forEach(msg => {
        const msgDiv = document.createElement('div');

        const textoDiv = document.createElement('div');
        textoDiv.className = 'chat-message-text';
        // APLICAR FORMATAÇÃO AQUI
        textoDiv.innerHTML = aplicarFormatacaoMarkdown(msg.mensagem);

        msgDiv.appendChild(textoDiv);
        // ...
    });
}
```

### 11.4 Widget não abre/fecha

**Sintomas:**
- Clicar no botão não expande o painel
- Console mostra erro "toggleChatWidget is not defined"

**Solução:**

1. Verificar que `chat-widget.js` está carregado:
   ```html
   <!-- Em base_privada.html -->
   <script src="{{ url_for('static', path='/js/chat-widget.js') }}" defer></script>
   ```

2. Verificar que função global existe:
   ```javascript
   // No final de static/js/chat-widget.js
   function toggleChatWidget() {
       // ... código
   }
   ```

3. Verificar que componente foi incluído:
   ```html
   <!-- Em base_privada.html -->
   {% include 'components/chat_widget.html' %}
   ```

### 11.5 Contador de não lidas não atualiza

**Sintomas:**
- Badge não mostra número correto
- Badge não desaparece após ler mensagens

**Diagnóstico:**

```javascript
// Adicionar log em atualizarContadorNaoLidas()
async function atualizarContadorNaoLidas() {
    const response = await fetch('/chat/mensagens/nao-lidas/total');
    const data = await response.json();
    console.log('[DEBUG] Total não lidas:', data.total);

    const badge = document.getElementById('chat-badge');
    // ...
}
```

**Soluções:**

1. Verificar que `marcar_como_lidas()` está sendo chamado ao abrir chat
2. Verificar que `atualizar_ultima_leitura()` está funcionando no backend
3. Verificar que SSE está enviando evento `"atualizar_contador"` após marcar como lidas

### 11.6 Performance lenta com muitas mensagens

**Sintomas:**
- Chat demora para carregar mensagens
- Scroll fica lento com muitas mensagens

**Soluções:**

1. **Implementar paginação inversa:**
   ```python
   # Em repo/chat_mensagem_repo.py
   def listar_por_sala(sala_id: str, limit: int = 50, antes_de_id: Optional[int] = None):
       """Lista mensagens com paginação por ID (mais eficiente)."""
       conn = get_connection()
       cursor = conn.cursor()

       if antes_de_id:
           cursor.execute(
               """SELECT * FROM chat_mensagem
                  WHERE sala_id = ? AND id < ?
                  ORDER BY id DESC LIMIT ?""",
               (sala_id, antes_de_id, limit)
           )
       else:
           cursor.execute(
               """SELECT * FROM chat_mensagem
                  WHERE sala_id = ?
                  ORDER BY id DESC LIMIT ?""",
               (sala_id, limit)
           )
       # ...
   ```

2. **Lazy loading de mensagens:**
   ```javascript
   // Carregar apenas últimas 50 mensagens inicialmente
   // Implementar scroll infinito para carregar mais antigas
   elementos.messagesContainer.addEventListener('scroll', async (e) => {
       if (e.target.scrollTop === 0) {
           // Usuário scrollou até o topo, carregar mensagens antigas
           await carregarMensagensAntigas();
       }
   });
   ```

3. **Virtualização de lista (biblioteca externa):**
   Usar biblioteca como `react-window` ou `vue-virtual-scroller` para renderizar apenas mensagens visíveis.

### 11.7 Usuário não encontrado na busca

**Sintomas:**
- Autocomplete não mostra resultados
- Busca retorna array vazio

**Diagnóstico:**

```python
# Em routes/chat_routes.py, adicionar log
@router.get("/usuarios/buscar")
async def buscar_usuarios(q: str, usuario_logado: dict):
    print(f"[DEBUG] Buscando usuários com termo: '{q}'")
    usuarios = usuario_repo.buscar_por_termo(q, limit=10)
    print(f"[DEBUG] Encontrados: {len(usuarios)} usuários")
    # ...
```

**Soluções:**

1. Verificar que `usuario_repo.buscar_por_termo()` está implementado corretamente
2. Verificar que termo de busca tem pelo menos 2 caracteres (limitar no frontend)
3. Adicionar busca case-insensitive no SQL:
   ```python
   cursor.execute(
       """SELECT * FROM usuario
          WHERE (LOWER(nome) LIKE LOWER(?)
                 OR LOWER(email) LIKE LOWER(?))
          LIMIT ?""",
       (f"%{termo}%", f"%{termo}%", limit)
   )
   ```

---

## 📚 Camada 12: Referências

### Documentação Oficial

- **FastAPI SSE**: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
- **EventSource API**: https://developer.mozilla.org/en-US/docs/Web/API/EventSource
- **Server-Sent Events Spec**: https://html.spec.whatwg.org/multipage/server-sent-events.html
- **SQLite**: https://www.sqlite.org/docs.html
- **Pydantic**: https://docs.pydantic.dev/

### Artigos e Tutoriais

- **Real-time Web with SSE**: https://www.smashingmagazine.com/2018/02/sse-websockets-data-flow-http2/
- **SSE vs WebSockets**: https://ably.com/blog/websockets-vs-sse
- **FastAPI Background Tasks**: https://fastapi.tiangolo.com/tutorial/background-tasks/

### Bibliotecas Utilizadas

- **FastAPI**: Framework web assíncrono Python
- **Starlette**: Base do FastAPI (inclui StreamingResponse)
- **asyncio**: Biblioteca padrão Python para programação assíncrona
- **Bootstrap 5**: Framework CSS para UI
- **Bootstrap Icons**: Ícones do chat

### Projetos de Referência

- **FastAPI Chat Example**: https://github.com/tiangolo/fastapi/discussions/3019
- **SSE with FastAPI**: https://github.com/sysid/sse-starlette
- **Django Channels**: https://channels.readthedocs.io/ (inspiração para arquitetura)

### Ferramentas de Desenvolvimento

- **Browser DevTools**: Para debugar SSE (aba Network → tipo EventStream)
- **SQLite Browser**: https://sqlitebrowser.org/ (visualizar banco de dados)
- **Postman**: Para testar endpoints REST (não funciona com SSE)
- **curl**: Para testar SSE via linha de comando:
  ```bash
  curl -N -H "Cookie: session=..." http://localhost:8400/chat/stream
  ```

### Alternativas Consideradas

- **WebSockets**: Mais complexo, bidirecional (não necessário para chat simples)
- **Long Polling**: Técnica legada, mais ineficiente que SSE
- **Firebase Realtime Database**: Solução SaaS (preferimos self-hosted)
- **Socket.IO**: Biblioteca JavaScript popular mas com overhead desnecessário

### Padrões de Arquitetura

- **Pub/Sub Pattern**: Usado no ChatManager para broadcast de mensagens
- **Repository Pattern**: Camada de abstração para acesso ao banco de dados
- **DTO Pattern**: Validação e serialização de dados de entrada/saída
- **Singleton Pattern**: ChatManager é instância única compartilhada

### Performance e Escalabilidade

Para sistemas com mais de 1000 usuários simultâneos, considere:

- **Redis Pub/Sub**: Para coordenar múltiplas instâncias da aplicação
- **PostgreSQL**: Banco relacional mais robusto que SQLite
- **Load Balancer com Sticky Sessions**: Nginx com `ip_hash` ou cookies
- **Horizontal Scaling**: Múltiplos servidores FastAPI + Redis central

### Segurança

- **Autenticação**: Sistema existente do DefaultWebApp (sessões)
- **Autorização**: Usuário só pode acessar suas próprias salas
- **Validação**: Pydantic DTOs validam todas as entradas
- **SQL Injection**: Prevenido com prepared statements (`?` placeholders)
- **XSS**: Prevenido com sanitização no frontend (escape de HTML)
- **Rate Limiting**: Implementar para prevenir spam de mensagens

---

## 🎯 Conclusão

Este documento fornece uma especificação completa para implementar um sistema de chat 1-to-1 em tempo real no projeto **DefaultWebApp** usando **Server-Sent Events (SSE)** e **HTTP POST**.

**Principais características:**

✅ Arquitetura simples e eficiente baseada em SSE
✅ Chat estilo WhatsApp Web com widget retrátil
✅ Conversas privadas 1-to-1 (máximo 2 usuários por sala)
✅ Busca de usuários com autocomplete
✅ Formatação markdown lite (**negrito**, *itálico*, ***ambos***)
✅ Lista de conversas com contador de não lidas
✅ Paginação de conversas e mensagens
✅ Testes automatizados completos
✅ Pronto para deploy em produção

**Tempo estimado de implementação:** 5-6 horas para desenvolvedor experiente.

**Próximos passos:**

1. Seguir o **Checklist de Implementação** (Camada 9) na ordem exata
2. Executar os **Testes** (Camada 8) para validar cada componente
3. Testar no navegador conforme **Fase 11** do checklist
4. Configurar para produção conforme **Camada 10**

**Suporte:**

- Para dúvidas sobre implementação, consulte o **Troubleshooting** (Camada 11)
- Para otimizações de performance, veja **Camada 10.8**
- Para escalabilidade, considere alternativas mencionadas em **Referências**

---

**Documento criado em:** 2025-10-28
**Versão:** 1.0
**Autor:** Claude Code
**Projeto:** DefaultWebApp
