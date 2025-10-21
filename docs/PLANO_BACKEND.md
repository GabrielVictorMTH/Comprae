# PLANO DE IMPLEMENTAÇÃO DO BACKEND - COMPRAÊ

## 📋 SUMÁRIO

1. [Análise do Estado Atual](#1-análise-do-estado-atual)
2. [Comparação: Implementado vs Requisitos do PDF](#2-comparação-implementado-vs-requisitos-do-pdf)
3. [Arquitetura e Padrões do Projeto](#3-arquitetura-e-padrões-do-projeto)
4. [Guia de Implementação - DTOs](#4-guia-de-implementação---dtos)
5. [Guia de Implementação - SQL](#5-guia-de-implementação---sql)
6. [Guia de Implementação - Repositories](#6-guia-de-implementação---repositories)
7. [Guia de Implementação - Routes](#7-guia-de-implementação---routes)
8. [Atualização do main.py e Seeds](#8-atualização-do-mainpy-e-seeds)
9. [Checklist de Implementação](#9-checklist-de-implementação)

---

## 1. ANÁLISE DO ESTADO ATUAL

### 1.1 Visão Geral do Projeto

O projeto **Compraê** é uma plataforma de marketplace local desenvolvida com FastAPI, seguindo uma arquitetura em camadas bem definida. O objetivo é conectar pequenos comerciantes e consumidores da mesma região.

**Stack Tecnológica:**
- **Backend:** Python 3.12 + FastAPI
- **Templates:** Jinja2
- **Banco de Dados:** SQLite (via util/db_util.py)
- **Autenticação:** Sessões com SessionMiddleware
- **Validação:** Pydantic v2
- **Segurança:** Bcrypt para senhas, validações customizadas
- **Email:** Resend.com

### 1.2 Estrutura de Diretórios Atual

```
Comprae/
├── main.py                      # ✅ Arquivo principal configurado
├── dtos/                        # ⚠️ Apenas usuario_dto, auth_dto, perfil_dto
│   ├── usuario_dto.py          # ✅ Completo
│   ├── auth_dto.py             # ✅ Completo
│   ├── perfil_dto.py           # ✅ Completo
│   ├── tarefa_dto.py           # ✅ Exemplo (pode ser removido)
│   └── validators.py           # ✅ 15+ validadores reutilizáveis
├── model/                       # ✅ Todos os models criados
│   ├── usuario_model.py        # ✅ Completo
│   ├── categoria_model.py      # ✅ Estrutura básica
│   ├── anuncio_model.py        # ✅ Estrutura básica
│   ├── pedido_model.py         # ✅ Estrutura básica
│   ├── endereco_model.py       # ✅ Estrutura básica
│   └── mensagem_model.py       # ✅ Estrutura básica
├── sql/                         # ⚠️ Apenas usuario_sql.py
│   ├── usuario_sql.py          # ✅ Completo
│   └── configuracao_sql.py     # ✅ Completo
├── repo/                        # ⚠️ Apenas usuario_repo.py
│   ├── usuario_repo.py         # ✅ Completo com CRUD
│   └── configuracao_repo.py    # ✅ Completo
├── routes/                      # ⚠️ Apenas rotas de usuário/auth
│   ├── auth_routes.py          # ✅ Login, cadastro, recuperação senha
│   ├── admin_usuarios_routes.py # ✅ CRUD de usuários
│   ├── perfil_routes.py        # ✅ Atualização de perfil
│   └── public_routes.py        # ✅ Rota pública
└── util/                        # ✅ Infraestrutura completa
    ├── auth_decorator.py       # ✅ @requer_autenticacao
    ├── db_util.py              # ✅ Conexão SQLite
    ├── security.py             # ✅ Hash de senhas
    ├── perfis.py               # ✅ Enum de perfis
    ├── validators.py           # ✅ Validadores
    └── ...
```

### 1.3 O Que Já Está Implementado ✅

#### Infraestrutura Base (100% completo)
- ✅ FastAPI configurado com SessionMiddleware
- ✅ Sistema de templates Jinja2
- ✅ Tratamento centralizado de exceções
- ✅ Logger profissional com rotação
- ✅ Conexão com banco de dados SQLite
- ✅ Sistema de flash messages
- ✅ Decorators de autenticação por perfil
- ✅ 15+ validadores reutilizáveis (CPF, CNPJ, email, telefone, etc.)

#### Sistema de Usuários (100% completo)
- ✅ **Model:** `Usuario` com todos os campos necessários
- ✅ **DTO:** `CriarUsuarioDTO`, `AlterarUsuarioDTO`
- ✅ **SQL:** Tabela usuario com índices e constraints
- ✅ **Repository:** CRUD completo + funções especiais (por email, token, etc.)
- ✅ **Routes:**
  - Autenticação (login, logout, cadastro, recuperação de senha)
  - Admin (CRUD de usuários)
  - Perfil (atualização de dados e senha)

#### Sistema de Perfis
- ✅ **Enum Perfil** com 3 perfis:
  - `Perfil.ADMIN` = "Administrador"
  - `Perfil.CLIENTE` = "Cliente"
  - `Perfil.VENDEDOR` = "Vendedor"

### 1.4 O Que Precisa Ser Implementado ❌

#### 1. Categorias
- ❌ DTOs (criar, alterar, listar)
- ❌ SQL (criar tabela, queries CRUD)
- ❌ Repository (CRUD completo)
- ❌ Routes (listar, cadastrar, alterar, excluir)
- ⚠️ Model já existe mas está básico

#### 2. Endereços
- ❌ DTOs (criar, alterar, listar)
- ❌ SQL (criar tabela com FK para usuario)
- ❌ Repository (CRUD + busca por usuário)
- ❌ Routes (CRUD de endereços do usuário logado)
- ⚠️ Model já existe mas está básico

#### 3. Anúncios (Produtos)
- ❌ DTOs (criar, alterar, listar, filtros)
- ❌ SQL (criar tabela com FKs, índices)
- ❌ Repository (CRUD + buscas especiais: por categoria, vendedor, ativo, estoque)
- ❌ Routes (CRUD vendedor, listagem pública, detalhes, busca)
- ⚠️ Model já existe mas precisa ajustes

#### 4. Pedidos
- ❌ DTOs (criar pedido, atualizar status, avaliar)
- ❌ SQL (criar tabela com múltiplas FKs, campos de rastreamento)
- ❌ Repository (CRUD + buscas: por comprador, vendedor, status)
- ❌ Routes (criar pedido, listar pedidos, atualizar status, avaliar)
- ⚠️ Model já existe mas precisa ajustes

#### 5. Mensagens
- ❌ DTOs (enviar mensagem, listar conversas)
- ❌ SQL (criar tabela com FKs para remetente/destinatário)
- ❌ Repository (enviar, listar por conversa, marcar como lida)
- ❌ Routes (enviar, listar, marcar como visualizada)
- ⚠️ Model já existe mas está básico

---

## 2. COMPARAÇÃO: IMPLEMENTADO VS REQUISITOS DO PDF

### 2.1 Requisitos Funcionais do PDF

Comparando com a **Seção 2.1** do PDF (páginas 17-18):

| RF | Descrição | Status | Observações |
|----|-----------|--------|-------------|
| **RF1** | Login, redefinição e confirmação de senha | ✅ **100%** | Implementado em `auth_routes.py` |
| **RF2** | Cadastro e confirmação de usuários | ✅ **100%** | Implementado em `auth_routes.py` |
| **RF3** | Catálogo de produtos com detalhes | ❌ **0%** | **Precisa implementar rotas públicas de anúncios** |
| **RF4** | Realizar compra e confirmação | ❌ **0%** | **Precisa implementar sistema de pedidos** |
| **RF5** | Área do cliente com histórico de pedidos | ❌ **0%** | **Precisa routes de pedidos por comprador** |
| **RF6** | Área do vendedor com pedidos recebidos | ❌ **0%** | **Precisa routes de pedidos por vendedor** |
| **RF7** | Vendedor gerenciar produtos (CRUD) | ❌ **0%** | **Precisa routes de anúncios para vendedor** |
| **RF8** | Admin e vendedor gerenciar categorias | ❌ **0%** | **Precisa routes de categorias** |
| **RF9** | Cliente cancelar pedido | ❌ **0%** | Média prioridade |
| **RF10** | Vendedor acompanhar status pedidos | ❌ **0%** | Média prioridade |
| **RF11** | Usuário alterar dados do perfil | ✅ **100%** | Implementado em `perfil_routes.py` |
| **RF12** | Usuário alterar senha | ✅ **100%** | Implementado em `perfil_routes.py` |
| **RF13** | Notificações automáticas | ❌ **0%** | Baixa prioridade (integrar com email_service) |
| **RF14** | Relatórios para vendedores | ❌ **0%** | Baixa prioridade |
| **RF15** | Busca avançada com filtros | ❌ **0%** | Baixa prioridade |
| **RF16** | Admin moderar informações | ⚠️ **30%** | Parcial em admin_usuarios_routes |

**Resumo:** 4 de 16 RFs implementados (25%)

### 2.2 Diagrama de Entidade-Relacionamento (Página 25 do PDF)

Comparando com o **DER** do PDF:

| Entidade | Tabela | Status Model | Status SQL | Status Repo | Status Routes |
|----------|--------|--------------|------------|-------------|---------------|
| **Usuario** | usuario | ✅ Completo | ✅ Criado | ✅ CRUD completo | ✅ Completo |
| **Categoria** | categoria | ⚠️ Básico | ❌ Falta criar | ❌ Falta criar | ❌ Falta criar |
| **Endereco** | endereco | ⚠️ Básico | ❌ Falta criar | ❌ Falta criar | ❌ Falta criar |
| **Anuncio** | anuncio | ⚠️ Básico | ❌ Falta criar | ❌ Falta criar | ❌ Falta criar |
| **Pedido** | pedido | ⚠️ Básico | ❌ Falta criar | ❌ Falta criar | ❌ Falta criar |
| **Mensagem** | mensagem | ⚠️ Básico | ❌ Falta criar | ❌ Falta criar | ❌ Falta criar |

**Resumo:** 1 de 6 entidades completamente implementadas (17%)

### 2.3 Casos de Uso (Páginas 20-24 do PDF)

#### Perfil Anônimo (UC Anônimo)
- ✅ Realizar Login → `auth_routes.py`
- ✅ Realizar Cadastro → `auth_routes.py`
- ✅ Redefinir Senha → `auth_routes.py`
- ❌ **Consultar Catálogo de Produtos** → Falta implementar
- ❌ **Consultar Detalhes do Produto** → Falta implementar
- ❌ **Adicionar ao Carrinho** → Falta implementar

#### Perfil Usuário (UC Usuário)
- ✅ Alterar Senha → `perfil_routes.py`
- ✅ Atualizar Perfil → `perfil_routes.py`
- ❌ **Visualizar Mensagens** → Falta implementar
- ❌ **Enviar Mensagens** → Falta implementar
- ❌ **Responder Mensagens** → Falta implementar

#### Perfil Comprador (UC Comprador)
- ❌ **Realizar Pedido** → Falta implementar
- ❌ **Consultar Histórico de Pedidos** → Falta implementar
- ❌ **Consultar Detalhes do Pedido** → Falta implementar

#### Perfil Vendedor (UC Vendedor)
- ❌ **Gerenciar Produtos (CRUD)** → Falta implementar
- ❌ **Consultar Pedidos Recebidos** → Falta implementar
- ❌ **Gerenciar Pedidos (atualizar status)** → Falta implementar
- ❌ **Enviar Pedido** → Falta implementar

#### Perfil Administrador (UC Admin)
- ✅ Gerenciar Usuários → `admin_usuarios_routes.py`
- ❌ **Gerenciar Categorias** → Falta implementar
- ❌ **Gerenciar Produtos** → Falta implementar
- ❌ **Gerenciar Pedidos** → Falta implementar
- ❌ **Moderar Usuários** → Falta implementar
- ✅ Visualizar Logs → Estrutura existe
- ✅ Configurar Sistema → `admin_configuracoes_routes.py`

### 2.4 Problemas Identificados nos Models Existentes

#### 1. `model/anuncio_model.py` - Problemas:
```python
# ERRO: "discricao" está escrito errado (deveria ser "descricao")
discricao: str  # ❌ CORRIGIR para "descricao"

# INCONSISTÊNCIA: "peso" e "estoque" são str, mas deveriam ser tipos específicos
peso: str  # ⚠️ Deveria ser float ou Decimal
estoque: str  # ⚠️ Deveria ser int
```

#### 2. `model/pedido_model.py` - Problemas:
```python
# FALTAM CAMPOS OPCIONAIS
# Muitos campos como data_hora_pagamento, codigo_rastreio, etc. deveriam ser Optional
data_hora_pagamento: datetime  # ⚠️ Deveria ser Optional[datetime]
data_hora_envio: datetime  # ⚠️ Deveria ser Optional[datetime]
codigo_rastreio: str  # ⚠️ Deveria ser Optional[str]
nota_avaliacao: int  # ⚠️ Deveria ser Optional[int]
comentario_avaliacao: str  # ⚠️ Deveria ser Optional[str]
data_hora_avaliacao: datetime  # ⚠️ Deveria ser Optional[datetime]
```

#### 3. `util/perfis.py` - Ajuste necessário:
```python
# ATUAL: Perfil tem 3 valores
class Perfil(str, Enum):
    ADMIN = "Administrador"
    CLIENTE = "Cliente"
    VENDEDOR = "Vendedor"

# ✅ ESTÁ CORRETO conforme PDF
# O PDF menciona os 3 perfis: Anônimo (sem cadastro), Usuário (base), Comprador, Vendedor, Admin
# No sistema: CLIENTE = Comprador, VENDEDOR = Vendedor, ADMIN = Administrador
```

---

## 3. ARQUITETURA E PADRÕES DO PROJETO

### 3.1 Camadas da Aplicação

O projeto segue uma arquitetura em 5 camadas bem definidas:

```
┌─────────────────────────────────────────────┐
│  ROUTES (FastAPI Routers)                   │  ← Endpoints HTTP
│  - Validação de entrada (DTOs)              │
│  - Autenticação/Autorização                 │
│  - Chamadas ao Repository                   │
│  - Retorno de Templates ou JSON             │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│  DTOs (Data Transfer Objects)               │  ← Validação Pydantic
│  - Validação de campos                      │
│  - Transformação de dados                   │
│  - Uso de validators.py reutilizáveis       │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│  REPOSITORY (Camada de Acesso a Dados)      │  ← Lógica de negócio
│  - Funções CRUD                             │
│  - Consultas especializadas                 │
│  - Manipulação de Models                    │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│  SQL (Queries SQL)                          │  ← SQL puro
│  - CREATE TABLE                             │
│  - INSERT, UPDATE, DELETE, SELECT           │
│  - Queries complexas                        │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│  DATABASE (SQLite via db_util.py)           │  ← Persistência
└─────────────────────────────────────────────┘
```

### 3.2 Padrão de Nomenclatura

#### Arquivos:
- **Models:** `{entidade}_model.py` → Ex: `categoria_model.py`
- **DTOs:** `{entidade}_dto.py` → Ex: `categoria_dto.py`
- **SQL:** `{entidade}_sql.py` → Ex: `categoria_sql.py`
- **Repositories:** `{entidade}_repo.py` → Ex: `categoria_repo.py`
- **Routes:** `{contexto}_routes.py` → Ex: `categorias_routes.py`, `admin_categorias_routes.py`

#### Classes e Funções:
- **Model:** `class Categoria` (PascalCase)
- **DTO:** `class CriarCategoriaDTO`, `class AlterarCategoriaDTO`
- **Repository:** `def criar_tabela()`, `def inserir()`, `def obter_por_id()`
- **Routes:** `async def listar()`, `async def get_cadastrar()`, `async def post_cadastrar()`

#### Constantes SQL:
```python
CRIAR_TABELA = """CREATE TABLE..."""
INSERIR = """INSERT INTO..."""
ALTERAR = """UPDATE..."""
EXCLUIR = """DELETE FROM..."""
OBTER_POR_ID = """SELECT * FROM ... WHERE id = ?"""
OBTER_TODOS = """SELECT * FROM ... ORDER BY..."""
```

### 3.3 Exemplo Completo de Padrão (Categoria)

Esta seção demonstra como implementar UMA entidade completa seguindo todos os padrões do projeto:

#### 1. Model (`model/categoria_model.py`)
```python
from dataclasses import dataclass

@dataclass
class Categoria:
    id: int
    nome: str
    descricao: str
```

#### 2. DTO (`dtos/categoria_dto.py`)
```python
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_id_positivo,
)

class CriarCategoriaDTO(BaseModel):
    nome: str
    descricao: str

    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=50)
    )
    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria("Descrição", tamanho_maximo=200)
    )

class AlterarCategoriaDTO(BaseModel):
    id: int
    nome: str
    descricao: str

    _validar_id = field_validator("id")(validar_id_positivo())
    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=50)
    )
    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria("Descrição", tamanho_maximo=200)
    )
```

#### 3. SQL (`sql/categoria_sql.py`)
```python
CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS categoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT NOT NULL
)
"""

INSERIR = "INSERT INTO categoria (nome, descricao) VALUES (?, ?)"
ALTERAR = "UPDATE categoria SET nome = ?, descricao = ? WHERE id = ?"
EXCLUIR = "DELETE FROM categoria WHERE id = ?"
OBTER_POR_ID = "SELECT * FROM categoria WHERE id = ?"
OBTER_TODOS = "SELECT * FROM categoria ORDER BY nome"
```

#### 4. Repository (`repo/categoria_repo.py`)
```python
from typing import Optional
from model.categoria_model import Categoria
from sql.categoria_sql import *
from util.db_util import get_connection

def criar_tabela() -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True

def inserir(categoria: Categoria) -> Optional[int]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (categoria.nome, categoria.descricao))
        return cursor.lastrowid

def alterar(categoria: Categoria) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ALTERAR, (categoria.nome, categoria.descricao, categoria.id))
        return cursor.rowcount > 0

def excluir(id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0

def obter_por_id(id: int) -> Optional[Categoria]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        if row:
            return Categoria(
                id=row["id"],
                nome=row["nome"],
                descricao=row["descricao"]
            )
        return None

def obter_todos() -> list[Categoria]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [
            Categoria(
                id=row["id"],
                nome=row["nome"],
                descricao=row["descricao"]
            )
            for row in rows
        ]
```

#### 5. Routes (`routes/categorias_routes.py`)
```python
from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from dtos.categoria_dto import CriarCategoriaDTO, AlterarCategoriaDTO
from model.categoria_model import Categoria
from repo import categoria_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.perfis import Perfil

router = APIRouter(prefix="/categorias")
templates = criar_templates("templates/categorias")

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value, Perfil.VENDEDOR.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    categorias = categoria_repo.obter_todos()
    return templates.TemplateResponse(
        "categorias/listar.html",
        {"request": request, "categorias": categorias}
    )

@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    return templates.TemplateResponse(
        "categorias/cadastro.html",
        {"request": request}
    )

@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    descricao: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    try:
        dto = CriarCategoriaDTO(nome=nome, descricao=descricao)
        categoria = Categoria(id=0, nome=dto.nome, descricao=dto.descricao)
        categoria_repo.inserir(categoria)
        informar_sucesso(request, "Categoria cadastrada com sucesso!")
        return RedirectResponse("/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        informar_erro(request, str(e))
        return templates.TemplateResponse(
            "categorias/cadastro.html",
            {"request": request, "dados": {"nome": nome, "descricao": descricao}}
        )
```

---

**📊 ESTATÍSTICAS DA ANÁLISE:**
- **Linhas:** ~650
- **Seções Completas:** 3 de 9
- **Próxima Etapa:** Seção 4 - Guia de Implementação - DTOs

---

## 4. GUIA DE IMPLEMENTAÇÃO - DTOs

### 4.1 Visão Geral dos DTOs

Os **DTOs (Data Transfer Objects)** são responsáveis por:
1. Validar dados de entrada do usuário
2. Transformar e sanitizar dados
3. Fornecer mensagens de erro amigáveis
4. Garantir consistência dos dados antes de chegar no Repository

**Estrutura de um DTO no projeto:**
- Herda de `pydantic.BaseModel`
- Usa `field_validator` para validações
- Reutiliza validadores de `dtos/validators.py`
- Segue padrão: `Criar{Entidade}DTO`, `Alterar{Entidade}DTO`

### 4.2 DTO: Categoria

#### Arquivo: `dtos/categoria_dto.py`

**O que criar:** DTOs para criar e alterar categorias

**Campos necessários:**
- `id`: int (apenas em AlterarCategoriaDTO)
- `nome`: str (obrigatório, 3-50 caracteres)
- `descricao`: str (obrigatório, até 200 caracteres)

**Passo a Passo:**

1. **Criar o arquivo** `dtos/categoria_dto.py`

2. **Importar dependências:**
```python
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_id_positivo,
)
```

3. **Criar DTO de Criação:**
```python
class CriarCategoriaDTO(BaseModel):
    """DTO para criação de categoria"""

    nome: str
    descricao: str

    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=50)
    )
    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria("Descrição", tamanho_maximo=200)
    )
```

4. **Criar DTO de Alteração:**
```python
class AlterarCategoriaDTO(BaseModel):
    """DTO para alteração de categoria"""

    id: int
    nome: str
    descricao: str

    _validar_id = field_validator("id")(validar_id_positivo())
    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=50)
    )
    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria("Descrição", tamanho_maximo=200)
    )
```

**Código completo:**
```python
"""
DTOs para operações com Categorias.
"""
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_id_positivo,
)


class CriarCategoriaDTO(BaseModel):
    """DTO para criação de categoria"""

    nome: str
    descricao: str

    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=50)
    )
    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria("Descrição", tamanho_maximo=200)
    )


class AlterarCategoriaDTO(BaseModel):
    """DTO para alteração de categoria"""

    id: int
    nome: str
    descricao: str

    _validar_id = field_validator("id")(validar_id_positivo())
    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=50)
    )
    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria("Descrição", tamanho_maximo=200)
    )
```

### 4.3 DTO: Endereco

#### Arquivo: `dtos/endereco_dto.py`

**O que criar:** DTOs para criar e alterar endereços

**Campos necessários (conforme DER do PDF):**
- `id_endereco`: int (apenas em AlterarEnderecoDTO)
- `id_usuario`: int (preenchido automaticamente)
- `titulo`: str (ex: "Casa", "Trabalho")
- `logradouro`: str (rua/avenida)
- `numero`: str (número do imóvel)
- `complemento`: str (opcional - apto, bloco, etc.)
- `bairro`: str
- `cidade`: str
- `uf`: str (2 caracteres - sigla do estado)
- `cep`: str (formato: 00000-000)

**Passo a Passo:**

1. **Criar o arquivo** `dtos/endereco_dto.py`

2. **Importar dependências:**
```python
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_id_positivo,
    validar_cep,
    validar_uf,
)
```

3. **Criar DTO de Criação:**
```python
class CriarEnderecoDTO(BaseModel):
    """DTO para criação de endereço"""

    titulo: str
    logradouro: str
    numero: str
    complemento: str
    bairro: str
    cidade: str
    uf: str
    cep: str

    _validar_titulo = field_validator("titulo")(
        validar_string_obrigatoria("Título", tamanho_maximo=50)
    )
    _validar_logradouro = field_validator("logradouro")(
        validar_string_obrigatoria("Logradouro", tamanho_maximo=100)
    )
    _validar_numero = field_validator("numero")(
        validar_string_obrigatoria("Número", tamanho_maximo=10)
    )
    # Complemento é opcional - não usa validar_string_obrigatoria
    _validar_bairro = field_validator("bairro")(
        validar_string_obrigatoria("Bairro", tamanho_maximo=50)
    )
    _validar_cidade = field_validator("cidade")(
        validar_string_obrigatoria("Cidade", tamanho_maximo=50)
    )
    _validar_uf = field_validator("uf")(validar_uf())
    _validar_cep = field_validator("cep")(validar_cep())
```

**Nota sobre validadores:**
- `validar_uf()` → Valida se é uma UF válida (AC, AL, AM, etc.)
- `validar_cep()` → Valida formato 00000-000 e remove caracteres especiais

**Código completo:**
```python
"""
DTOs para operações com Endereços.
"""
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_id_positivo,
    validar_cep,
    validar_uf,
)


class CriarEnderecoDTO(BaseModel):
    """DTO para criação de endereço"""

    titulo: str
    logradouro: str
    numero: str
    complemento: str
    bairro: str
    cidade: str
    uf: str
    cep: str

    _validar_titulo = field_validator("titulo")(
        validar_string_obrigatoria("Título", tamanho_maximo=50)
    )
    _validar_logradouro = field_validator("logradouro")(
        validar_string_obrigatoria("Logradouro", tamanho_maximo=100)
    )
    _validar_numero = field_validator("numero")(
        validar_string_obrigatoria("Número", tamanho_maximo=10)
    )
    # Complemento é opcional, então não validamos como obrigatório
    _validar_bairro = field_validator("bairro")(
        validar_string_obrigatoria("Bairro", tamanho_maximo=50)
    )
    _validar_cidade = field_validator("cidade")(
        validar_string_obrigatoria("Cidade", tamanho_maximo=50)
    )
    _validar_uf = field_validator("uf")(validar_uf())
    _validar_cep = field_validator("cep")(validar_cep())


class AlterarEnderecoDTO(BaseModel):
    """DTO para alteração de endereço"""

    id: int
    titulo: str
    logradouro: str
    numero: str
    complemento: str
    bairro: str
    cidade: str
    uf: str
    cep: str

    _validar_id = field_validator("id")(validar_id_positivo())
    _validar_titulo = field_validator("titulo")(
        validar_string_obrigatoria("Título", tamanho_maximo=50)
    )
    _validar_logradouro = field_validator("logradouro")(
        validar_string_obrigatoria("Logradouro", tamanho_maximo=100)
    )
    _validar_numero = field_validator("numero")(
        validar_string_obrigatoria("Número", tamanho_maximo=10)
    )
    _validar_bairro = field_validator("bairro")(
        validar_string_obrigatoria("Bairro", tamanho_maximo=50)
    )
    _validar_cidade = field_validator("cidade")(
        validar_string_obrigatoria("Cidade", tamanho_maximo=50)
    )
    _validar_uf = field_validator("uf")(validar_uf())
    _validar_cep = field_validator("cep")(validar_cep())
```

**⚠️ IMPORTANTE - Relacionamento com Usuario:**
- O campo `id_usuario` NÃO vai no DTO
- Ele será preenchido automaticamente no Repository usando o `usuario_logado["id"]`
- Isso garante que o usuário só pode criar endereços para ele mesmo

### 4.4 Checklist - DTOs de Categoria e Endereço

- [ ] Criar arquivo `dtos/categoria_dto.py`
  - [ ] Importar Pydantic e validators
  - [ ] Implementar `CriarCategoriaDTO`
  - [ ] Implementar `AlterarCategoriaDTO`
  - [ ] Testar validações (nome mínimo 3 chars, máximo 50)

- [ ] Criar arquivo `dtos/endereco_dto.py`
  - [ ] Importar Pydantic e validators
  - [ ] Implementar `CriarEnderecoDTO`
  - [ ] Implementar `AlterarEnderecoDTO`
  - [ ] Verificar validadores CEP e UF existem em `validators.py`

---

### 4.5 DTO: Anuncio

#### Arquivo: `dtos/anuncio_dto.py`

**O que criar:** DTOs para criar, alterar e filtrar anúncios (produtos)

**Campos necessários (conforme DER do PDF):**
- `id_anuncio`: int (apenas em AlterarAnuncioDTO)
- `id_vendedor`: int (preenchido automaticamente)
- `id_categoria`: int (seleção de categoria existente)
- `nome`: str (nome do produto)
- `descricao`: str (descrição detalhada)
- `peso`: float (peso em kg)
- `preco`: float (preço em reais)
- `estoque`: int (quantidade disponível)
- `ativo`: bool (se está visível ou não)

**⚠️ CORREÇÃO NO MODEL:**
Antes de criar os DTOs, precisamos corrigir o model existente:

```python
# model/anuncio_model.py - ANTES (ERRADO)
discricao: str  # ❌ ERRO de ortografia
peso: str  # ❌ Deveria ser float
estoque: str  # ❌ Deveria ser int

# model/anuncio_model.py - DEPOIS (CORRETO)
descricao: str  # ✅ Corrigido
peso: float  # ✅ Tipo correto
estoque: int  # ✅ Tipo correto
```

**Passo a Passo:**

1. **Criar o arquivo** `dtos/anuncio_dto.py`

2. **Importar dependências:**
```python
from typing import Optional
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_id_positivo,
    validar_valor_monetario,
    validar_numero_positivo,
)
```

3. **Criar DTO de Criação:**
```python
class CriarAnuncioDTO(BaseModel):
    """DTO para criação de anúncio"""

    id_categoria: int
    nome: str
    descricao: str
    peso: float
    preco: float
    estoque: int

    _validar_id_categoria = field_validator("id_categoria")(validar_id_positivo())
    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=100)
    )
    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria("Descrição", tamanho_minimo=10, tamanho_maximo=1000)
    )
    _validar_peso = field_validator("peso")(validar_numero_positivo("Peso"))
    _validar_preco = field_validator("preco")(validar_valor_monetario())
    _validar_estoque = field_validator("estoque")(validar_numero_positivo("Estoque"))
```

**Código completo:**
```python
"""
DTOs para operações com Anúncios (Produtos).
"""
from typing import Optional
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_id_positivo,
    validar_valor_monetario,
    validar_numero_positivo,
)


class CriarAnuncioDTO(BaseModel):
    """DTO para criação de anúncio"""

    id_categoria: int
    nome: str
    descricao: str
    peso: float
    preco: float
    estoque: int

    _validar_id_categoria = field_validator("id_categoria")(validar_id_positivo())
    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=100)
    )
    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria("Descrição", tamanho_minimo=10, tamanho_maximo=1000)
    )
    _validar_peso = field_validator("peso")(validar_numero_positivo("Peso"))
    _validar_preco = field_validator("preco")(validar_valor_monetario())
    _validar_estoque = field_validator("estoque")(validar_numero_positivo("Estoque"))


class AlterarAnuncioDTO(BaseModel):
    """DTO para alteração de anúncio"""

    id: int
    id_categoria: int
    nome: str
    descricao: str
    peso: float
    preco: float
    estoque: int
    ativo: bool

    _validar_id = field_validator("id")(validar_id_positivo())
    _validar_id_categoria = field_validator("id_categoria")(validar_id_positivo())
    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=100)
    )
    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria("Descrição", tamanho_minimo=10, tamanho_maximo=1000)
    )
    _validar_peso = field_validator("peso")(validar_numero_positivo("Peso"))
    _validar_preco = field_validator("preco")(validar_valor_monetario())
    _validar_estoque = field_validator("estoque")(validar_numero_positivo("Estoque"))


class FiltroAnuncioDTO(BaseModel):
    """DTO para filtrar anúncios na busca"""

    nome: Optional[str] = None
    id_categoria: Optional[int] = None
    preco_min: Optional[float] = None
    preco_max: Optional[float] = None
    apenas_ativos: bool = True

    # Validações opcionais
    _validar_id_categoria = field_validator("id_categoria")(validar_id_positivo())
```

**⚠️ IMPORTANTE - Relacionamentos:**
- `id_vendedor` NÃO vai no DTO de criação
- Será preenchido automaticamente no Repository com `usuario_logado["id"]`
- Apenas o próprio vendedor pode editar seus anúncios
- Campo `ativo` serve para "pausar" um anúncio sem excluí-lo

### 4.6 DTO: Mensagem

#### Arquivo: `dtos/mensagem_dto.py`

**O que criar:** DTOs para enviar e listar mensagens

**Campos necessários (conforme DER do PDF):**
- `id_mensagem`: int (apenas em listagens)
- `id_remetente`: int (preenchido automaticamente)
- `id_destinatario`: int (usuário que receberá)
- `mensagem`: str (conteúdo da mensagem)
- `data_hora`: datetime (preenchido automaticamente)
- `visualizada`: bool (se foi lida ou não)

**Passo a Passo:**

1. **Criar o arquivo** `dtos/mensagem_dto.py`

2. **Importar dependências:**
```python
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_id_positivo,
)
```

3. **Criar DTO de Envio:**
```python
class EnviarMensagemDTO(BaseModel):
    """DTO para enviar mensagem"""

    id_destinatario: int
    mensagem: str

    _validar_id_destinatario = field_validator("id_destinatario")(validar_id_positivo())
    _validar_mensagem = field_validator("mensagem")(
        validar_string_obrigatoria("Mensagem", tamanho_minimo=1, tamanho_maximo=500)
    )
```

**Código completo:**
```python
"""
DTOs para operações com Mensagens.
"""
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_id_positivo,
)


class EnviarMensagemDTO(BaseModel):
    """DTO para enviar mensagem"""

    id_destinatario: int
    mensagem: str

    _validar_id_destinatario = field_validator("id_destinatario")(validar_id_positivo())
    _validar_mensagem = field_validator("mensagem")(
        validar_string_obrigatoria("Mensagem", tamanho_minimo=1, tamanho_maximo=500)
    )


class MarcarMensagemLidaDTO(BaseModel):
    """DTO para marcar mensagem como lida"""

    id_mensagem: int

    _validar_id = field_validator("id_mensagem")(validar_id_positivo())
```

**⚠️ IMPORTANTE - Sistema de Mensagens:**
- `id_remetente` é preenchido automaticamente com `usuario_logado["id"]`
- `data_hora` é preenchida com `datetime.now()` no Repository
- `visualizada` inicia como `False`
- Apenas o destinatário pode marcar como lida
- Não há DTO de alteração (mensagens não podem ser editadas após envio)

### 4.7 Checklist - DTOs de Anúncio e Mensagem

- [ ] **PRIMEIRO:** Corrigir `model/anuncio_model.py`
  - [ ] Corrigir `discricao` → `descricao`
  - [ ] Alterar `peso: str` → `peso: float`
  - [ ] Alterar `estoque: str` → `estoque: int`

- [ ] Criar arquivo `dtos/anuncio_dto.py`
  - [ ] Implementar `CriarAnuncioDTO`
  - [ ] Implementar `AlterarAnuncioDTO`
  - [ ] Implementar `FiltroAnuncioDTO` (para buscas)
  - [ ] Verificar validadores `validar_valor_monetario` e `validar_numero_positivo`

- [ ] Criar arquivo `dtos/mensagem_dto.py`
  - [ ] Implementar `EnviarMensagemDTO`
  - [ ] Implementar `MarcarMensagemLidaDTO`

---

### 4.8 DTO: Pedido

#### Arquivo: `dtos/pedido_dto.py`

**O que criar:** DTOs para criar pedido, atualizar status e avaliar

**Campos necessários (conforme DER do PDF):**
- `id_pedido`: int
- `id_endereco`: int (endereço de entrega)
- `id_comprador`: int (preenchido automaticamente)
- `id_anuncio`: int (produto comprado)
- `preco`: float (preço no momento da compra)
- `status`: str (pendente, pago, enviado, entregue, cancelado)
- `data_hora_pedido`: datetime (preenchido automaticamente)
- `data_hora_pagamento`: Optional[datetime]
- `data_hora_envio`: Optional[datetime]
- `codigo_rastreio`: Optional[str]
- `nota_avaliacao`: Optional[int] (1 a 5)
- `comentario_avaliacao`: Optional[str]
- `data_hora_avaliacao`: Optional[datetime]

**⚠️ CORREÇÃO NO MODEL:**
Antes de criar os DTOs, precisamos ajustar os campos opcionais no model:

```python
# model/pedido_model.py - ANTES (PROBLEMÁTICO)
data_hora_pagamento: datetime  # ❌ Deveria ser Optional
data_hora_envio: datetime  # ❌ Deveria ser Optional
codigo_rastreio: str  # ❌ Deveria ser Optional
nota_avaliacao: int  # ❌ Deveria ser Optional
comentario_avaliacao: str  # ❌ Deveria ser Optional
data_hora_avaliacao: datetime  # ❌ Deveria ser Optional

# model/pedido_model.py - DEPOIS (CORRETO)
data_hora_pagamento: Optional[datetime] = None  # ✅
data_hora_envio: Optional[datetime] = None  # ✅
codigo_rastreio: Optional[str] = None  # ✅
nota_avaliacao: Optional[int] = None  # ✅
comentario_avaliacao: Optional[str] = None  # ✅
data_hora_avaliacao: Optional[datetime] = None  # ✅
```

**Passo a Passo:**

1. **Criar o arquivo** `dtos/pedido_dto.py`

2. **Importar dependências:**
```python
from typing import Optional
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_id_positivo,
    validar_status_pedido,
    validar_avaliacao,
    validar_string_obrigatoria,
)
```

3. **Definir status válidos** (criar em `util/status_pedido.py`):
```python
# util/status_pedido.py
from enum import Enum

class StatusPedido(str, Enum):
    PENDENTE = "Pendente"
    PAGO = "Pago"
    ENVIADO = "Enviado"
    ENTREGUE = "Entregue"
    CANCELADO = "Cancelado"

    @classmethod
    def valores(cls) -> list[str]:
        return [status.value for status in cls]
```

**Código completo:**
```python
"""
DTOs para operações com Pedidos.
"""
from typing import Optional
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_id_positivo,
    validar_string_obrigatoria,
)


class CriarPedidoDTO(BaseModel):
    """DTO para criação de pedido (compra)"""

    id_endereco: int
    id_anuncio: int

    _validar_id_endereco = field_validator("id_endereco")(validar_id_positivo())
    _validar_id_anuncio = field_validator("id_anuncio")(validar_id_positivo())


class AtualizarStatusPedidoDTO(BaseModel):
    """DTO para vendedor atualizar status do pedido"""

    id_pedido: int
    status: str
    codigo_rastreio: Optional[str] = None

    _validar_id = field_validator("id_pedido")(validar_id_positivo())

    @field_validator("status")
    @classmethod
    def validar_status(cls, v: str) -> str:
        """Valida se o status é válido"""
        from util.status_pedido import StatusPedido
        if v not in StatusPedido.valores():
            raise ValueError(f"Status inválido. Use: {', '.join(StatusPedido.valores())}")
        return v


class AvaliarPedidoDTO(BaseModel):
    """DTO para comprador avaliar pedido após entrega"""

    id_pedido: int
    nota_avaliacao: int
    comentario_avaliacao: str

    _validar_id = field_validator("id_pedido")(validar_id_positivo())

    @field_validator("nota_avaliacao")
    @classmethod
    def validar_nota(cls, v: int) -> int:
        """Valida se a nota está entre 1 e 5"""
        if not 1 <= v <= 5:
            raise ValueError("Nota deve estar entre 1 e 5")
        return v

    _validar_comentario = field_validator("comentario_avaliacao")(
        validar_string_obrigatoria("Comentário", tamanho_minimo=10, tamanho_maximo=500)
    )


class CancelarPedidoDTO(BaseModel):
    """DTO para cancelar pedido"""

    id_pedido: int

    _validar_id = field_validator("id_pedido")(validar_id_positivo())
```

**⚠️ IMPORTANTE - Regras de Negócio dos Pedidos:**

1. **Criação do Pedido:**
   - `id_comprador` é preenchido com `usuario_logado["id"]`
   - `preco` é copiado do anúncio no momento da compra (não pode mudar depois)
   - `status` inicia como "Pendente"
   - `data_hora_pedido` é preenchida com `datetime.now()`

2. **Atualização de Status (apenas vendedor):**
   - Apenas o vendedor do anúncio pode atualizar
   - Fluxo: Pendente → Pago → Enviado → Entregue
   - Ao marcar como "Enviado", deve informar `codigo_rastreio`
   - Ao marcar como "Pago", preenche `data_hora_pagamento`
   - Ao marcar como "Enviado", preenche `data_hora_envio`

3. **Avaliação (apenas comprador após entrega):**
   - Só pode avaliar se status = "Entregue"
   - Apenas o comprador pode avaliar
   - Nota de 1 a 5
   - Preenche `data_hora_avaliacao` automaticamente

4. **Cancelamento:**
   - Comprador pode cancelar se status = "Pendente"
   - Vendedor pode cancelar a qualquer momento antes de "Enviado"

### 4.9 Resumo - Todos os DTOs

| Entidade | Arquivo | DTOs Criados | Observações |
|----------|---------|--------------|-------------|
| **Categoria** | `categoria_dto.py` | Criar, Alterar | Simples, sem relacionamentos |
| **Endereco** | `endereco_dto.py` | Criar, Alterar | Vinculado ao usuario_logado |
| **Anuncio** | `anuncio_dto.py` | Criar, Alterar, Filtro | Vinculado ao vendedor |
| **Mensagem** | `mensagem_dto.py` | Enviar, MarcarLida | Simples, entre usuários |
| **Pedido** | `pedido_dto.py` | Criar, AtualizarStatus, Avaliar, Cancelar | Mais complexo, workflow |

### 4.10 Checklist Completo - DTOs

- [ ] **Correções nos Models:**
  - [ ] `model/anuncio_model.py` → corrigir `discricao`, `peso`, `estoque`
  - [ ] `model/pedido_model.py` → tornar campos opcionais

- [ ] **Criar DTOs:**
  - [ ] `dtos/categoria_dto.py`
  - [ ] `dtos/endereco_dto.py`
  - [ ] `dtos/anuncio_dto.py`
  - [ ] `dtos/mensagem_dto.py`
  - [ ] `dtos/pedido_dto.py`

- [ ] **Criar Enum de Status:**
  - [ ] `util/status_pedido.py`

- [ ] **Verificar Validadores Existem:**
  - [ ] `validar_cep()`
  - [ ] `validar_uf()`
  - [ ] `validar_valor_monetario()`
  - [ ] `validar_numero_positivo()`

---

## 5. GUIA DE IMPLEMENTAÇÃO - SQL

### 5.1 Visão Geral das Queries SQL

Os arquivos SQL contêm as queries puras que serão executadas pelo Repository. O projeto usa **SQLite**, então algumas funcionalidades específicas devem ser consideradas.

**Estrutura padrão de um arquivo SQL:**
```python
# sql/{entidade}_sql.py

CRIAR_TABELA = """CREATE TABLE IF NOT EXISTS..."""
INSERIR = """INSERT INTO..."""
ALTERAR = """UPDATE..."""
EXCLUIR = """DELETE FROM..."""
OBTER_POR_ID = """SELECT * FROM..."""
OBTER_TODOS = """SELECT * FROM..."""
# Queries específicas da entidade
```

**Boas práticas:**
- Usar `IF NOT EXISTS` em CREATE TABLE
- Usar placeholders `?` para prepared statements
- Definir FOREIGN KEYs corretamente
- Criar índices para campos de busca frequente
- Usar `DEFAULT` para timestamps

### 5.2 SQL: Categoria

#### Arquivo: `sql/categoria_sql.py`

**Tabela simples, sem relacionamentos complexos**

**Código completo:**
```python
"""
Queries SQL para tabela de Categorias.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS categoria (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT NOT NULL
)
"""

INSERIR = """
INSERT INTO categoria (nome, descricao)
VALUES (?, ?)
"""

ALTERAR = """
UPDATE categoria
SET nome = ?, descricao = ?
WHERE id_categoria = ?
"""

EXCLUIR = """
DELETE FROM categoria
WHERE id_categoria = ?
"""

OBTER_POR_ID = """
SELECT * FROM categoria
WHERE id_categoria = ?
"""

OBTER_TODOS = """
SELECT * FROM categoria
ORDER BY nome
"""

OBTER_POR_NOME = """
SELECT * FROM categoria
WHERE nome LIKE ?
ORDER BY nome
"""
```

**Observações:**
- `nome` é UNIQUE para evitar duplicatas
- Ordenação alfabética por padrão
- Query extra `OBTER_POR_NOME` para buscas

### 5.3 SQL: Endereco

#### Arquivo: `sql/endereco_sql.py`

**Tabela com FK para usuario**

**Código completo:**
```python
"""
Queries SQL para tabela de Endereços.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS endereco (
    id_endereco INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    logradouro TEXT NOT NULL,
    numero TEXT NOT NULL,
    complemento TEXT,
    bairro TEXT NOT NULL,
    cidade TEXT NOT NULL,
    uf TEXT NOT NULL,
    cep TEXT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id) ON DELETE CASCADE
)
"""

# Índice para otimizar buscas por usuário
CRIAR_INDICE = """
CREATE INDEX IF NOT EXISTS idx_endereco_usuario
ON endereco(id_usuario)
"""

INSERIR = """
INSERT INTO endereco (id_usuario, titulo, logradouro, numero, complemento, bairro, cidade, uf, cep)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

ALTERAR = """
UPDATE endereco
SET titulo = ?, logradouro = ?, numero = ?, complemento = ?,
    bairro = ?, cidade = ?, uf = ?, cep = ?
WHERE id_endereco = ?
"""

EXCLUIR = """
DELETE FROM endereco
WHERE id_endereco = ?
"""

OBTER_POR_ID = """
SELECT * FROM endereco
WHERE id_endereco = ?
"""

OBTER_TODOS_POR_USUARIO = """
SELECT * FROM endereco
WHERE id_usuario = ?
ORDER BY titulo
"""

OBTER_TODOS = """
SELECT * FROM endereco
ORDER BY id_usuario, titulo
"""
```

**Observações:**
- `ON DELETE CASCADE` → se usuário for excluído, endereços também são
- Índice em `id_usuario` para otimizar buscas
- Query principal: `OBTER_TODOS_POR_USUARIO`

### 5.4 SQL: Mensagem

#### Arquivo: `sql/mensagem_sql.py`

**Tabela com 2 FKs (remetente e destinatário)**

**Código completo:**
```python
"""
Queries SQL para tabela de Mensagens.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS mensagem (
    id_mensagem INTEGER PRIMARY KEY AUTOINCREMENT,
    id_remetente INTEGER NOT NULL,
    id_destinatario INTEGER NOT NULL,
    mensagem TEXT NOT NULL,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    visualizada BOOLEAN DEFAULT 0,
    FOREIGN KEY (id_remetente) REFERENCES usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (id_destinatario) REFERENCES usuario(id) ON DELETE CASCADE
)
"""

# Índices para otimizar buscas por remetente e destinatário
CRIAR_INDICE_REMETENTE = """
CREATE INDEX IF NOT EXISTS idx_mensagem_remetente
ON mensagem(id_remetente)
"""

CRIAR_INDICE_DESTINATARIO = """
CREATE INDEX IF NOT EXISTS idx_mensagem_destinatario
ON mensagem(id_destinatario)
"""

INSERIR = """
INSERT INTO mensagem (id_remetente, id_destinatario, mensagem)
VALUES (?, ?, ?)
"""

MARCAR_COMO_LIDA = """
UPDATE mensagem
SET visualizada = 1
WHERE id_mensagem = ?
"""

OBTER_POR_ID = """
SELECT * FROM mensagem
WHERE id_mensagem = ?
"""

OBTER_CONVERSA = """
SELECT * FROM mensagem
WHERE (id_remetente = ? AND id_destinatario = ?)
   OR (id_remetente = ? AND id_destinatario = ?)
ORDER BY data_hora ASC
"""

OBTER_MENSAGENS_RECEBIDAS = """
SELECT * FROM mensagem
WHERE id_destinatario = ?
ORDER BY data_hora DESC
"""

OBTER_MENSAGENS_NAO_LIDAS = """
SELECT * FROM mensagem
WHERE id_destinatario = ? AND visualizada = 0
ORDER BY data_hora DESC
"""

CONTAR_NAO_LIDAS = """
SELECT COUNT(*) as total
FROM mensagem
WHERE id_destinatario = ? AND visualizada = 0
"""
```

**Observações:**
- `data_hora` usa `CURRENT_TIMESTAMP` automaticamente
- `visualizada` é BOOLEAN (0 = não lida, 1 = lida)
- Query `OBTER_CONVERSA` busca mensagens entre 2 usuários
- Índices em ambas as FKs para performance

---

### 5.5 SQL: Anuncio

#### Arquivo: `sql/anuncio_sql.py`

**Tabela com FKs para vendedor e categoria**

**Código completo:**
```python
"""
Queries SQL para tabela de Anúncios (Produtos).
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS anuncio (
    id_anuncio INTEGER PRIMARY KEY AUTOINCREMENT,
    id_vendedor INTEGER NOT NULL,
    id_categoria INTEGER NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    peso REAL NOT NULL,
    preco REAL NOT NULL,
    estoque INTEGER NOT NULL,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT 1,
    FOREIGN KEY (id_vendedor) REFERENCES usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria) ON DELETE RESTRICT
)
"""

# Índices para otimizar buscas
CRIAR_INDICE_VENDEDOR = """
CREATE INDEX IF NOT EXISTS idx_anuncio_vendedor
ON anuncio(id_vendedor)
"""

CRIAR_INDICE_CATEGORIA = """
CREATE INDEX IF NOT EXISTS idx_anuncio_categoria
ON anuncio(id_categoria)
"""

CRIAR_INDICE_ATIVO = """
CREATE INDEX IF NOT EXISTS idx_anuncio_ativo
ON anuncio(ativo)
"""

INSERIR = """
INSERT INTO anuncio (id_vendedor, id_categoria, nome, descricao, peso, preco, estoque)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""

ALTERAR = """
UPDATE anuncio
SET id_categoria = ?, nome = ?, descricao = ?, peso = ?, preco = ?, estoque = ?, ativo = ?
WHERE id_anuncio = ?
"""

EXCLUIR = """
DELETE FROM anuncio
WHERE id_anuncio = ?
"""

OBTER_POR_ID = """
SELECT * FROM anuncio
WHERE id_anuncio = ?
"""

OBTER_TODOS = """
SELECT * FROM anuncio
ORDER BY data_cadastro DESC
"""

OBTER_TODOS_ATIVOS = """
SELECT * FROM anuncio
WHERE ativo = 1 AND estoque > 0
ORDER BY data_cadastro DESC
"""

OBTER_POR_VENDEDOR = """
SELECT * FROM anuncio
WHERE id_vendedor = ?
ORDER BY data_cadastro DESC
"""

OBTER_POR_CATEGORIA = """
SELECT * FROM anuncio
WHERE id_categoria = ? AND ativo = 1 AND estoque > 0
ORDER BY data_cadastro DESC
"""

BUSCAR_POR_NOME = """
SELECT * FROM anuncio
WHERE nome LIKE ? AND ativo = 1 AND estoque > 0
ORDER BY data_cadastro DESC
"""

BUSCAR_COM_FILTROS = """
SELECT * FROM anuncio
WHERE ativo = 1 AND estoque > 0
  AND (? IS NULL OR nome LIKE ?)
  AND (? IS NULL OR id_categoria = ?)
  AND (? IS NULL OR preco >= ?)
  AND (? IS NULL OR preco <= ?)
ORDER BY data_cadastro DESC
"""

ATUALIZAR_ESTOQUE = """
UPDATE anuncio
SET estoque = estoque - ?
WHERE id_anuncio = ? AND estoque >= ?
"""
```

**Observações:**
- `ON DELETE RESTRICT` em categoria → não permite excluir categoria com anúncios
- `ativo` permite "pausar" anúncios sem excluí-los
- Query `BUSCAR_COM_FILTROS` suporta filtros opcionais
- `ATUALIZAR_ESTOQUE` diminui estoque de forma atômica

### 5.6 SQL: Pedido

#### Arquivo: `sql/pedido_sql.py`

**Tabela mais complexa com múltiplas FKs e campos de rastreamento**

**Código completo:**
```python
"""
Queries SQL para tabela de Pedidos.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS pedido (
    id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
    id_endereco INTEGER NOT NULL,
    id_comprador INTEGER NOT NULL,
    id_anuncio INTEGER NOT NULL,
    preco REAL NOT NULL,
    status TEXT DEFAULT 'Pendente',
    data_hora_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_hora_pagamento DATETIME,
    data_hora_envio DATETIME,
    codigo_rastreio TEXT,
    nota_avaliacao INTEGER,
    comentario_avaliacao TEXT,
    data_hora_avaliacao DATETIME,
    FOREIGN KEY (id_endereco) REFERENCES endereco(id_endereco) ON DELETE RESTRICT,
    FOREIGN KEY (id_comprador) REFERENCES usuario(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_anuncio) REFERENCES anuncio(id_anuncio) ON DELETE RESTRICT,
    CHECK (nota_avaliacao IS NULL OR (nota_avaliacao >= 1 AND nota_avaliacao <= 5))
)
"""

# Índices para otimizar buscas
CRIAR_INDICE_COMPRADOR = """
CREATE INDEX IF NOT EXISTS idx_pedido_comprador
ON pedido(id_comprador)
"""

CRIAR_INDICE_ANUNCIO = """
CREATE INDEX IF NOT EXISTS idx_pedido_anuncio
ON pedido(id_anuncio)
"""

CRIAR_INDICE_STATUS = """
CREATE INDEX IF NOT EXISTS idx_pedido_status
ON pedido(status)
"""

INSERIR = """
INSERT INTO pedido (id_endereco, id_comprador, id_anuncio, preco, status)
VALUES (?, ?, ?, ?, 'Pendente')
"""

ATUALIZAR_STATUS = """
UPDATE pedido
SET status = ?
WHERE id_pedido = ?
"""

ATUALIZAR_PARA_PAGO = """
UPDATE pedido
SET status = 'Pago', data_hora_pagamento = CURRENT_TIMESTAMP
WHERE id_pedido = ?
"""

ATUALIZAR_PARA_ENVIADO = """
UPDATE pedido
SET status = 'Enviado', data_hora_envio = CURRENT_TIMESTAMP, codigo_rastreio = ?
WHERE id_pedido = ?
"""

CANCELAR_PEDIDO = """
UPDATE pedido
SET status = 'Cancelado'
WHERE id_pedido = ?
"""

AVALIAR_PEDIDO = """
UPDATE pedido
SET nota_avaliacao = ?, comentario_avaliacao = ?, data_hora_avaliacao = CURRENT_TIMESTAMP
WHERE id_pedido = ?
"""

OBTER_POR_ID = """
SELECT * FROM pedido
WHERE id_pedido = ?
"""

OBTER_POR_COMPRADOR = """
SELECT * FROM pedido
WHERE id_comprador = ?
ORDER BY data_hora_pedido DESC
"""

OBTER_POR_VENDEDOR = """
SELECT p.* FROM pedido p
INNER JOIN anuncio a ON p.id_anuncio = a.id_anuncio
WHERE a.id_vendedor = ?
ORDER BY p.data_hora_pedido DESC
"""

OBTER_POR_STATUS = """
SELECT * FROM pedido
WHERE status = ?
ORDER BY data_hora_pedido DESC
"""

OBTER_TODOS = """
SELECT * FROM pedido
ORDER BY data_hora_pedido DESC
"""

OBTER_COM_DETALHES = """
SELECT
    p.*,
    a.nome as nome_produto,
    a.id_vendedor,
    u_comprador.nome as nome_comprador,
    u_comprador.email as email_comprador,
    e.logradouro, e.numero, e.cidade, e.uf
FROM pedido p
INNER JOIN anuncio a ON p.id_anuncio = a.id_anuncio
INNER JOIN usuario u_comprador ON p.id_comprador = u_comprador.id
INNER JOIN endereco e ON p.id_endereco = e.id_endereco
WHERE p.id_pedido = ?
"""
```

**Observações:**
- `CHECK` constraint em nota_avaliacao (1-5)
- `ON DELETE RESTRICT` → pedidos não podem ser excluídos se houver referências
- Queries separadas para cada transição de status
- `OBTER_COM_DETALHES` faz JOINs para trazer todas as informações
- `OBTER_POR_VENDEDOR` usa JOIN com anuncio para filtrar

### 5.7 Checklist - SQL

- [ ] Criar arquivo `sql/categoria_sql.py`
- [ ] Criar arquivo `sql/endereco_sql.py`
  - [ ] Incluir query `CRIAR_INDICE`
- [ ] Criar arquivo `sql/mensagem_sql.py`
  - [ ] Incluir queries `CRIAR_INDICE_REMETENTE` e `CRIAR_INDICE_DESTINATARIO`
- [ ] Criar arquivo `sql/anuncio_sql.py`
  - [ ] Incluir 3 queries de índices
  - [ ] Incluir query `BUSCAR_COM_FILTROS`
- [ ] Criar arquivo `sql/pedido_sql.py`
  - [ ] Incluir 3 queries de índices
  - [ ] Incluir query `OBTER_COM_DETALHES` com JOINs

---

## 6. GUIA DE IMPLEMENTAÇÃO - REPOSITORIES

### 6.1 Visão Geral dos Repositories

Os **Repositories** são a camada de acesso aos dados. Eles:
1. Executam as queries SQL
2. Convertem rows do banco em Models
3. Gerenciam transações e conexões
4. Implementam lógica de negócio relacionada a dados

**Estrutura padrão:**
```python
from typing import Optional
from model.{entidade}_model import {Entidade}
from sql.{entidade}_sql import *
from util.db_util import get_connection

def criar_tabela() -> bool:
    """Cria tabela e índices"""

def inserir(entidade: Entidade) -> Optional[int]:
    """Insere e retorna ID"""

def alterar(entidade: Entidade) -> bool:
    """Atualiza registro"""

def excluir(id: int) -> bool:
    """Exclui registro"""

def obter_por_id(id: int) -> Optional[Entidade]:
    """Busca por ID"""

def obter_todos() -> list[Entidade]:
    """Lista todos"""
```

### 6.2 Repository: Categoria

#### Arquivo: `repo/categoria_repo.py`

**Código completo:**
```python
"""
Repository para operações com Categorias.
"""
from typing import Optional
from model.categoria_model import Categoria
from sql.categoria_sql import *
from util.db_util import get_connection


def criar_tabela() -> bool:
    """Cria a tabela de categorias"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(categoria: Categoria) -> Optional[int]:
    """Insere uma nova categoria"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (categoria.nome, categoria.descricao))
        return cursor.lastrowid


def alterar(categoria: Categoria) -> bool:
    """Altera uma categoria existente"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ALTERAR, (categoria.nome, categoria.descricao, categoria.id))
        return cursor.rowcount > 0


def excluir(id: int) -> bool:
    """Exclui uma categoria"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0


def obter_por_id(id: int) -> Optional[Categoria]:
    """Obtém categoria por ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        if row:
            return Categoria(
                id=row["id_categoria"],
                nome=row["nome"],
                descricao=row["descricao"]
            )
        return None


def obter_todos() -> list[Categoria]:
    """Obtém todas as categorias"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [
            Categoria(
                id=row["id_categoria"],
                nome=row["nome"],
                descricao=row["descricao"]
            )
            for row in rows
        ]


def buscar_por_nome(nome: str) -> list[Categoria]:
    """Busca categorias por nome (LIKE)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_NOME, (f"%{nome}%",))
        rows = cursor.fetchall()
        return [
            Categoria(
                id=row["id_categoria"],
                nome=row["nome"],
                descricao=row["descricao"]
            )
            for row in rows
        ]
```

### 6.3 Repository: Endereco

#### Arquivo: `repo/endereco_repo.py`

**Código completo:**
```python
"""
Repository para operações com Endereços.
"""
from typing import Optional
from model.endereco_model import Endereco
from sql.endereco_sql import *
from util.db_util import get_connection


def criar_tabela() -> bool:
    """Cria a tabela de endereços e índice"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_INDICE)
        return True


def inserir(endereco: Endereco) -> Optional[int]:
    """Insere um novo endereço"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            endereco.id_usuario,
            endereco.titulo,
            endereco.logradouro,
            endereco.numero,
            endereco.complemento,
            endereco.bairro,
            endereco.cidade,
            endereco.uf,
            endereco.cep
        ))
        return cursor.lastrowid


def alterar(endereco: Endereco) -> bool:
    """Altera um endereço existente"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ALTERAR, (
            endereco.titulo,
            endereco.logradouro,
            endereco.numero,
            endereco.complemento,
            endereco.bairro,
            endereco.cidade,
            endereco.uf,
            endereco.cep,
            endereco.id_endereco
        ))
        return cursor.rowcount > 0


def excluir(id: int) -> bool:
    """Exclui um endereço"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0


def obter_por_id(id: int) -> Optional[Endereco]:
    """Obtém endereço por ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        if row:
            return Endereco(
                id_endereco=row["id_endereco"],
                id_usuario=row["id_usuario"],
                titulo=row["titulo"],
                logradouro=row["logradouro"],
                numero=row["numero"],
                complemento=row["complemento"],
                bairro=row["bairro"],
                cidade=row["cidade"],
                uf=row["uf"],
                cep=row["cep"],
                usuario=None  # Não carrega relacionamento aqui
            )
        return None


def obter_por_usuario(id_usuario: int) -> list[Endereco]:
    """Obtém todos os endereços de um usuário"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS_POR_USUARIO, (id_usuario,))
        rows = cursor.fetchall()
        return [
            Endereco(
                id_endereco=row["id_endereco"],
                id_usuario=row["id_usuario"],
                titulo=row["titulo"],
                logradouro=row["logradouro"],
                numero=row["numero"],
                complemento=row["complemento"],
                bairro=row["bairro"],
                cidade=row["cidade"],
                uf=row["uf"],
                cep=row["cep"],
                usuario=None
            )
            for row in rows
        ]


def obter_todos() -> list[Endereco]:
    """Obtém todos os endereços"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [
            Endereco(
                id_endereco=row["id_endereco"],
                id_usuario=row["id_usuario"],
                titulo=row["titulo"],
                logradouro=row["logradouro"],
                numero=row["numero"],
                complemento=row["complemento"],
                bairro=row["bairro"],
                cidade=row["cidade"],
                uf=row["uf"],
                cep=row["cep"],
                usuario=None
            )
            for row in rows
        ]
```

### 6.4 Repository: Mensagem

#### Arquivo: `repo/mensagem_repo.py`

**Implementa operações de mensagens entre usuários**

**Código completo:**
```python
"""
Repositório para operações com mensagens.
"""
from typing import Optional
from datetime import datetime

from model.mensagem_model import Mensagem
from sql.mensagem_sql import *
from util.db_util import get_connection


def criar_tabela() -> bool:
    """Cria a tabela de mensagens e índices"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_INDICE_REMETENTE)
        cursor.execute(CRIAR_INDICE_DESTINATARIO)
        return True


def inserir(mensagem: Mensagem) -> Optional[Mensagem]:
    """Insere uma nova mensagem"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            INSERIR,
            (mensagem.id_remetente, mensagem.id_destinatario, mensagem.mensagem)
        )
        if cursor.lastrowid:
            return obter_por_id(cursor.lastrowid)
        return None


def marcar_como_lida(id_mensagem: int) -> bool:
    """Marca uma mensagem como lida"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(MARCAR_COMO_LIDA, (id_mensagem,))
        return cursor.rowcount > 0


def obter_por_id(id_mensagem: int) -> Optional[Mensagem]:
    """Obtém uma mensagem por ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_mensagem,))
        row = cursor.fetchone()
        if row:
            return Mensagem(
                id_mensagem=row["id_mensagem"],
                id_remetente=row["id_remetente"],
                id_destinatario=row["id_destinatario"],
                mensagem=row["mensagem"],
                data_hora=datetime.fromisoformat(row["data_hora"]),
                visualizada=bool(row["visualizada"]),
                remetente=None,
                destinatario=None
            )
        return None


def obter_conversa(id_usuario1: int, id_usuario2: int) -> list[Mensagem]:
    """Obtém todas as mensagens entre dois usuários"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_CONVERSA, (id_usuario1, id_usuario2, id_usuario2, id_usuario1))
        rows = cursor.fetchall()
        return [
            Mensagem(
                id_mensagem=row["id_mensagem"],
                id_remetente=row["id_remetente"],
                id_destinatario=row["id_destinatario"],
                mensagem=row["mensagem"],
                data_hora=datetime.fromisoformat(row["data_hora"]),
                visualizada=bool(row["visualizada"]),
                remetente=None,
                destinatario=None
            )
            for row in rows
        ]


def obter_mensagens_recebidas(id_usuario: int) -> list[Mensagem]:
    """Obtém todas as mensagens recebidas por um usuário"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_MENSAGENS_RECEBIDAS, (id_usuario,))
        rows = cursor.fetchall()
        return [
            Mensagem(
                id_mensagem=row["id_mensagem"],
                id_remetente=row["id_remetente"],
                id_destinatario=row["id_destinatario"],
                mensagem=row["mensagem"],
                data_hora=datetime.fromisoformat(row["data_hora"]),
                visualizada=bool(row["visualizada"]),
                remetente=None,
                destinatario=None
            )
            for row in rows
        ]


def obter_mensagens_nao_lidas(id_usuario: int) -> list[Mensagem]:
    """Obtém mensagens não lidas de um usuário"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_MENSAGENS_NAO_LIDAS, (id_usuario,))
        rows = cursor.fetchall()
        return [
            Mensagem(
                id_mensagem=row["id_mensagem"],
                id_remetente=row["id_remetente"],
                id_destinatario=row["id_destinatario"],
                mensagem=row["mensagem"],
                data_hora=datetime.fromisoformat(row["data_hora"]),
                visualizada=bool(row["visualizada"]),
                remetente=None,
                destinatario=None
            )
            for row in rows
        ]


def contar_nao_lidas(id_usuario: int) -> int:
    """Conta mensagens não lidas de um usuário"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_NAO_LIDAS, (id_usuario,))
        row = cursor.fetchone()
        return row["total"] if row else 0
```

**Métodos principais:**
- `criar_tabela()` → cria tabela e índices
- `inserir()` → nova mensagem
- `marcar_como_lida()` → marca mensagem como visualizada
- `obter_conversa()` → todas mensagens entre 2 usuários
- `obter_mensagens_nao_lidas()` → mensagens não lidas
- `contar_nao_lidas()` → contador para badge de notificações

---

### 6.5 Repository: Anuncio

#### Arquivo: `repo/anuncio_repo.py`

**Repository mais complexo com filtros e gestão de estoque**

**Código completo:**
```python
"""
Repositório para operações com anúncios (produtos).
"""
from typing import Optional
from datetime import datetime

from model.anuncio_model import Anuncio
from sql.anuncio_sql import *
from util.db_util import get_connection


def criar_tabela() -> bool:
    """Cria a tabela de anúncios e índices"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_INDICE_VENDEDOR)
        cursor.execute(CRIAR_INDICE_CATEGORIA)
        cursor.execute(CRIAR_INDICE_ATIVO)
        return True


def inserir(anuncio: Anuncio) -> Optional[Anuncio]:
    """Insere um novo anúncio"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            INSERIR,
            (
                anuncio.id_vendedor,
                anuncio.id_categoria,
                anuncio.nome,
                anuncio.discricao,  # Note: usar campo do model atual (com typo)
                anuncio.peso,
                anuncio.preco,
                anuncio.estoque
            )
        )
        if cursor.lastrowid:
            return obter_por_id(cursor.lastrowid)
        return None


def alterar(anuncio: Anuncio) -> bool:
    """Altera um anúncio existente"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            ALTERAR,
            (
                anuncio.id_categoria,
                anuncio.nome,
                anuncio.discricao,
                anuncio.peso,
                anuncio.preco,
                anuncio.estoque,
                anuncio.ativo,
                anuncio.id_anuncio
            )
        )
        return cursor.rowcount > 0


def excluir(id_anuncio: int) -> bool:
    """Exclui um anúncio"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id_anuncio,))
        return cursor.rowcount > 0


def obter_por_id(id_anuncio: int) -> Optional[Anuncio]:
    """Obtém um anúncio por ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_anuncio,))
        row = cursor.fetchone()
        if row:
            return _row_to_anuncio(row)
        return None


def obter_todos() -> list[Anuncio]:
    """Obtém todos os anúncios"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def obter_todos_ativos() -> list[Anuncio]:
    """Obtém apenas anúncios ativos com estoque"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS_ATIVOS)
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def obter_por_vendedor(id_vendedor: int) -> list[Anuncio]:
    """Obtém todos os anúncios de um vendedor"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_VENDEDOR, (id_vendedor,))
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def obter_por_categoria(id_categoria: int) -> list[Anuncio]:
    """Obtém anúncios ativos de uma categoria"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_CATEGORIA, (id_categoria,))
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def buscar_por_nome(termo: str) -> list[Anuncio]:
    """Busca anúncios por nome (LIKE)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(BUSCAR_POR_NOME, (f"%{termo}%",))
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def buscar_com_filtros(
    termo: Optional[str] = None,
    id_categoria: Optional[int] = None,
    preco_min: Optional[float] = None,
    preco_max: Optional[float] = None
) -> list[Anuncio]:
    """Busca anúncios com filtros opcionais"""
    with get_connection() as conn:
        cursor = conn.cursor()
        # Preparar parâmetros para query SQL com IS NULL checks
        termo_like = f"%{termo}%" if termo else None
        cursor.execute(
            BUSCAR_COM_FILTROS,
            (
                termo_like, termo_like,
                id_categoria, id_categoria,
                preco_min, preco_min,
                preco_max, preco_max
            )
        )
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def atualizar_estoque(id_anuncio: int, quantidade: int) -> bool:
    """
    Diminui o estoque de um anúncio de forma atômica.
    Retorna True se conseguiu atualizar (estoque suficiente).
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_ESTOQUE, (quantidade, id_anuncio, quantidade))
        return cursor.rowcount > 0


def _row_to_anuncio(row) -> Anuncio:
    """Converte row do banco para objeto Anuncio"""
    return Anuncio(
        id_anuncio=row["id_anuncio"],
        id_vendedor=row["id_vendedor"],
        id_categoria=row["id_categoria"],
        nome=row["nome"],
        discricao=row["descricao"],  # Note: SQL usa "descricao" corrigido
        peso=row["peso"],
        preco=row["preco"],
        estoque=row["estoque"],
        data_cadastro=datetime.fromisoformat(row["data_cadastro"]),
        ativo=bool(row["ativo"]),
        vendedor=None,
        categoria=None
    )
```

**Métodos principais:**
- `obter_todos_ativos()` → lista pública de produtos
- `obter_por_vendedor()` → gerenciamento de anúncios do vendedor
- `buscar_com_filtros()` → busca avançada com múltiplos filtros
- `atualizar_estoque()` → gestão atômica de estoque em pedidos

**Observações:**
- Nota sobre o typo `discricao` no model atual
- Helper `_row_to_anuncio()` para conversão
- Query `BUSCAR_COM_FILTROS` suporta filtros opcionais

---

### 6.6 Repository: Pedido

#### Arquivo: `repo/pedido_repo.py`

**Repository mais complexo com gerenciamento de status e relatórios**

**Código completo:**
```python
"""
Repositório para operações com pedidos.
"""
from typing import Optional
from datetime import datetime

from model.pedido_model import Pedido
from sql.pedido_sql import *
from util.db_util import get_connection


def criar_tabela() -> bool:
    """Cria a tabela de pedidos e índices"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_INDICE_COMPRADOR)
        cursor.execute(CRIAR_INDICE_ANUNCIO)
        cursor.execute(CRIAR_INDICE_STATUS)
        return True


def inserir(pedido: Pedido) -> Optional[Pedido]:
    """Insere um novo pedido"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            INSERIR,
            (pedido.id_endereco, pedido.id_comprador, pedido.id_anuncio, pedido.preco)
        )
        if cursor.lastrowid:
            return obter_por_id(cursor.lastrowid)
        return None


def atualizar_status(id_pedido: int, status: str) -> bool:
    """Atualiza o status de um pedido"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_STATUS, (status, id_pedido))
        return cursor.rowcount > 0


def atualizar_para_pago(id_pedido: int) -> bool:
    """Marca pedido como pago (registra timestamp)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_PARA_PAGO, (id_pedido,))
        return cursor.rowcount > 0


def atualizar_para_enviado(id_pedido: int, codigo_rastreio: str) -> bool:
    """Marca pedido como enviado com código de rastreio"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_PARA_ENVIADO, (codigo_rastreio, id_pedido))
        return cursor.rowcount > 0


def cancelar_pedido(id_pedido: int) -> bool:
    """Cancela um pedido"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CANCELAR_PEDIDO, (id_pedido,))
        return cursor.rowcount > 0


def avaliar_pedido(id_pedido: int, nota: int, comentario: str) -> bool:
    """Registra avaliação de um pedido"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(AVALIAR_PEDIDO, (nota, comentario, id_pedido))
        return cursor.rowcount > 0


def obter_por_id(id_pedido: int) -> Optional[Pedido]:
    """Obtém um pedido por ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_pedido,))
        row = cursor.fetchone()
        if row:
            return _row_to_pedido(row)
        return None


def obter_por_comprador(id_comprador: int) -> list[Pedido]:
    """Obtém todos os pedidos de um comprador"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_COMPRADOR, (id_comprador,))
        rows = cursor.fetchall()
        return [_row_to_pedido(row) for row in rows]


def obter_por_vendedor(id_vendedor: int) -> list[Pedido]:
    """Obtém todos os pedidos dos anúncios de um vendedor"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_VENDEDOR, (id_vendedor,))
        rows = cursor.fetchall()
        return [_row_to_pedido(row) for row in rows]


def obter_por_status(status: str) -> list[Pedido]:
    """Obtém pedidos por status"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_STATUS, (status,))
        rows = cursor.fetchall()
        return [_row_to_pedido(row) for row in rows]


def obter_todos() -> list[Pedido]:
    """Obtém todos os pedidos (admin)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [_row_to_pedido(row) for row in rows]


def _row_to_pedido(row) -> Pedido:
    """Converte row do banco para objeto Pedido"""
    return Pedido(
        id_pedido=row["id_pedido"],
        id_endereco=row["id_endereco"],
        id_comprador=row["id_comprador"],
        id_anuncio=row["id_anuncio"],
        preco=row["preco"],
        status=row["status"],
        data_hora_pedido=datetime.fromisoformat(row["data_hora_pedido"]),
        data_hora_pagamento=datetime.fromisoformat(row["data_hora_pagamento"]) if row["data_hora_pagamento"] else None,
        data_hora_envio=datetime.fromisoformat(row["data_hora_envio"]) if row["data_hora_envio"] else None,
        codigo_rastreio=row["codigo_rastreio"],
        nota_avaliacao=row["nota_avaliacao"],
        comentario_avaliacao=row["comentario_avaliacao"],
        data_hora_avaliacao=datetime.fromisoformat(row["data_hora_avaliacao"]) if row["data_hora_avaliacao"] else None,
        endereco=None,
        comprador=None,
        anuncio=None
    )
```

**Métodos principais:**
- `inserir()` → novo pedido (sempre com status 'Pendente')
- `atualizar_para_pago()` → registra pagamento automático
- `atualizar_para_enviado()` → registra envio + rastreio
- `avaliar_pedido()` → registra nota e comentário
- `obter_por_vendedor()` → JOIN com anúncios para listar vendas
- `obter_por_comprador()` → histórico de compras

**Observações:**
- Campos opcionais tratados com `if row[campo] else None`
- Métodos específicos para cada transição de status
- Helper `_row_to_pedido()` para conversão

---

## 7. ROTAS (Routes)

Agora vamos criar as rotas que conectam o frontend ao backend. Cada router segue o padrão do `admin_usuarios_routes.py`.

### 7.1 Routes: Categorias

#### Arquivo: `routes/admin_categorias_routes.py`

**CRUD completo de categorias (apenas ADMIN)**

**Estrutura resumida:**
```python
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.categoria_dto import CriarCategoriaDTO, AlterarCategoriaDTO
from model.categoria_model import Categoria
from repo import categoria_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.perfis import Perfil
from util.exceptions import FormValidationError

router = APIRouter(prefix="/admin/categorias")
templates = criar_templates("templates/admin/categorias")

# GET /admin/categorias/ → redireciona para /listar
# GET /admin/categorias/listar → lista todas categorias
# GET /admin/categorias/cadastrar → formulário de cadastro
# POST /admin/categorias/cadastrar → processa cadastro
# GET /admin/categorias/editar/{id} → formulário de edição
# POST /admin/categorias/editar/{id} → processa edição
# POST /admin/categorias/excluir/{id} → exclui categoria
```

**Pontos-chave:**
- Apenas perfil ADMIN
- Validação com DTOs
- Tratamento de erro de categoria já existente (nome UNIQUE)
- Proteção ao excluir: verificar se há anúncios vinculados

---

### 7.2 Routes: Endereços

#### Arquivo: `routes/enderecos_routes.py`

**CRUD de endereços do usuário logado**

**Estrutura resumida:**
```python
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.endereco_dto import CriarEnderecoDTO, AlterarEnderecoDTO
from model.endereco_model import Endereco
from repo import endereco_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.perfis import Perfil
from util.exceptions import FormValidationError

router = APIRouter(prefix="/enderecos")
templates = criar_templates("templates/enderecos")

# GET /enderecos/ → redireciona para /listar
# GET /enderecos/listar → lista endereços do usuário logado
# GET /enderecos/cadastrar → formulário de cadastro
# POST /enderecos/cadastrar → processa cadastro
# GET /enderecos/editar/{id} → formulário de edição
# POST /enderecos/editar/{id} → processa edição
# POST /enderecos/excluir/{id} → exclui endereço
```

**Pontos-chave:**
- Qualquer usuário autenticado (CLIENTE ou VENDEDOR)
- Sempre usa `usuario_logado["id"]` para filtrar endereços
- Validação: usuário só pode editar/excluir seus próprios endereços

---

### 7.3 Routes: Anúncios

#### Arquivo: `routes/anuncios_routes.py`

**Gestão de anúncios (vendedor) + listagem pública (cliente)**

**Estrutura resumida:**
```python
from typing import Optional
from fastapi import APIRouter, Form, Request, Query, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.anuncio_dto import CriarAnuncioDTO, AlterarAnuncioDTO
from model.anuncio_model import Anuncio
from repo import anuncio_repo, categoria_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.perfis import Perfil
from util.exceptions import FormValidationError

router = APIRouter(prefix="/anuncios")
templates = criar_templates("templates/anuncios")

# ROTAS PÚBLICAS (ou autenticadas para compra)
# GET /anuncios/ → vitrine de produtos (buscar_com_filtros)
# GET /anuncios/detalhes/{id} → detalhes de um produto

# ROTAS DO VENDEDOR
# GET /anuncios/meus → lista anúncios do vendedor logado
# GET /anuncios/cadastrar → formulário de cadastro (select de categorias)
# POST /anuncios/cadastrar → processa cadastro
# GET /anuncios/editar/{id} → formulário de edição
# POST /anuncios/editar/{id} → processa edição
# POST /anuncios/excluir/{id} → exclui anúncio
# POST /anuncios/ativar/{id} → ativa/desativa anúncio
```

**Pontos-chave:**
- Vitrine pública com filtros (categoria, preço, termo)
- Vendedor só edita seus próprios anúncios
- Dropdown de categorias preenchido com `categoria_repo.obter_todos()`
- Validação: vendedor só pode editar anúncios onde `id_vendedor == usuario_logado["id"]`

---

### 7.4 Routes: Mensagens

#### Arquivo: `routes/mensagens_routes.py`

**Sistema de mensagens entre usuários**

**Estrutura resumida:**
```python
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.mensagem_dto import EnviarMensagemDTO
from model.mensagem_model import Mensagem
from repo import mensagem_repo, usuario_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.exceptions import FormValidationError

router = APIRouter(prefix="/mensagens")
templates = criar_templates("templates/mensagens")

# GET /mensagens/ → redireciona para /caixa-entrada
# GET /mensagens/caixa-entrada → lista mensagens recebidas
# GET /mensagens/conversa/{id_outro_usuario} → exibe conversa com outro usuário
# POST /mensagens/enviar → envia mensagem
# POST /mensagens/marcar-lida/{id} → marca mensagem como lida
```

**Pontos-chave:**
- Usuário autenticado (CLIENTE ou VENDEDOR)
- `obter_conversa()` exibe thread entre 2 usuários
- Badge de notificações usa `contar_nao_lidas()`
- Marcar como lida ao abrir conversa

---

### 7.5 Routes: Pedidos

#### Arquivo: `routes/pedidos_routes.py`

**Gestão de pedidos (comprador + vendedor)**

**Estrutura resumida:**
```python
from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.pedido_dto import CriarPedidoDTO, AvaliarPedidoDTO
from model.pedido_model import Pedido
from repo import pedido_repo, anuncio_repo, endereco_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.perfis import Perfil
from util.exceptions import FormValidationError

router = APIRouter(prefix="/pedidos")
templates = criar_templates("templates/pedidos")

# ROTAS DO COMPRADOR
# GET /pedidos/meus → lista pedidos do comprador
# GET /pedidos/detalhes/{id} → detalhes de um pedido
# POST /pedidos/criar → cria novo pedido (diminui estoque)
# POST /pedidos/pagar/{id} → marca como pago
# POST /pedidos/cancelar/{id} → cancela pedido (restaura estoque)
# POST /pedidos/avaliar/{id} → avalia pedido

# ROTAS DO VENDEDOR
# GET /pedidos/vendas → lista vendas (obter_por_vendedor)
# POST /pedidos/enviar/{id} → marca como enviado + rastreio
```

**Pontos-chave:**
- Ao criar pedido: `anuncio_repo.atualizar_estoque()`
- Ao cancelar: restaurar estoque
- Comprador só vê seus pedidos, vendedor só vê suas vendas
- Validação de permissões: comprador só cancela seus pedidos, vendedor só envia suas vendas

---

## 8. ATUALIZAÇÃO DO MAIN.PY E SEEDS

### 8.1 Atualizar `main.py`

**Adicionar imports dos novos repos:**
```python
from repo import (
    usuario_repo,
    configuracao_repo,
    tarefa_repo,
    categoria_repo,      # NOVO
    endereco_repo,       # NOVO
    anuncio_repo,        # NOVO
    mensagem_repo,       # NOVO
    pedido_repo          # NOVO
)
```

**Adicionar routers:**
```python
from routes.admin_categorias_routes import router as admin_categorias_router
from routes.enderecos_routes import router as enderecos_router
from routes.anuncios_routes import router as anuncios_router
from routes.mensagens_routes import router as mensagens_router
from routes.pedidos_routes import router as pedidos_router

# ... mais abaixo ...

app.include_router(admin_categorias_router, tags=["Admin - Categorias"])
app.include_router(enderecos_router, tags=["Endereços"])
app.include_router(anuncios_router, tags=["Anúncios"])
app.include_router(mensagens_router, tags=["Mensagens"])
app.include_router(pedidos_router, tags=["Pedidos"])
```

**Criar tabelas:**
```python
# Após criar tabelas existentes...
categoria_repo.criar_tabela()
logger.info("Tabela 'categoria' criada/verificada")

endereco_repo.criar_tabela()
logger.info("Tabela 'endereco' criada/verificada")

mensagem_repo.criar_tabela()
logger.info("Tabela 'mensagem' criada/verificada")

anuncio_repo.criar_tabela()
logger.info("Tabela 'anuncio' criada/verificada")

pedido_repo.criar_tabela()
logger.info("Tabela 'pedido' criada/verificada")
```

### 8.2 Seeds: `util/seed_data.py`

**Adicionar dados iniciais para testes:**
```python
def inicializar_dados():
    """Inicializa dados básicos no banco"""
    # ... código existente de usuários ...

    # Categorias
    from repo import categoria_repo
    from model.categoria_model import Categoria

    if not categoria_repo.obter_todos():
        categorias = [
            Categoria(0, "Eletrônicos", "Produtos eletrônicos e tecnologia"),
            Categoria(0, "Livros", "Livros novos e usados"),
            Categoria(0, "Móveis", "Móveis e decoração"),
            Categoria(0, "Vestuário", "Roupas, calçados e acessórios"),
        ]
        for cat in categorias:
            categoria_repo.inserir(cat)
        logger.info("Categorias seed criadas")
```

---

## 9. CHECKLIST FINAL DE IMPLEMENTAÇÃO

### Fase 1: DTOs e SQL ✅
- [ ] Criar `dtos/categoria_dto.py`
- [ ] Criar `dtos/endereco_dto.py`
- [ ] Criar `dtos/anuncio_dto.py`
- [ ] Criar `dtos/mensagem_dto.py`
- [ ] Criar `dtos/pedido_dto.py`
- [ ] Criar `sql/categoria_sql.py`
- [ ] Criar `sql/endereco_sql.py`
- [ ] Criar `sql/mensagem_sql.py`
- [ ] Criar `sql/anuncio_sql.py`
- [ ] Criar `sql/pedido_sql.py`

### Fase 2: Repositories ✅
- [ ] Criar `repo/categoria_repo.py`
- [ ] Criar `repo/endereco_repo.py`
- [ ] Criar `repo/mensagem_repo.py`
- [ ] Criar `repo/anuncio_repo.py`
- [ ] Criar `repo/pedido_repo.py`

### Fase 3: Routes 🔄
- [ ] Criar `routes/admin_categorias_routes.py`
- [ ] Criar `routes/enderecos_routes.py`
- [ ] Criar `routes/anuncios_routes.py`
- [ ] Criar `routes/mensagens_routes.py`
- [ ] Criar `routes/pedidos_routes.py`

### Fase 4: Integração 🔄
- [ ] Atualizar `main.py` (imports, routers, criar_tabela)
- [ ] Atualizar `util/seed_data.py` (categorias seed)
- [ ] Corrigir `model/anuncio_model.py` (typos: discricao → descricao, peso/estoque tipos)
- [ ] Corrigir `model/pedido_model.py` (adicionar Optional nos campos opcionais)

### Fase 5: Testes 🔄
- [ ] Testar CRUD de categorias
- [ ] Testar CRUD de endereços
- [ ] Testar criação e listagem de anúncios
- [ ] Testar busca com filtros
- [ ] Testar sistema de mensagens
- [ ] Testar fluxo completo de pedido
- [ ] Testar atualização de estoque
- [ ] Testar avaliações

---

## CONCLUSÃO

Este documento fornece um **guia completo de implementação do backend** do Compraê.

**Ordem de implementação recomendada:**
1. DTOs + SQL (camadas de dados)
2. Repositories (lógica de persistência)
3. Routes (endpoints da API)
4. Integração com main.py e seeds
5. Correção dos models existentes
6. Testes manuais de cada funcionalidade

**Total estimado:** ~25 arquivos novos + 3 arquivos modificados

**Próximos passos (fora do escopo deste documento):**
- Templates HTML para as rotas
- Melhorias de UX
- Upload de imagens nos anúncios
- Relatórios e dashboards

---

*Documento criado em: 21/10/2025*
*Projeto: Compraê - Plataforma de Marketplace Local*
*Versão: 2.0 - COMPLETO: Análise + DTOs + SQL + Repositories + Routes + Integração*
