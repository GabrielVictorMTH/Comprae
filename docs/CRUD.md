# Manual para Criação de CRUD - Área Administrativa

Este manual ensina passo a passo como criar um CRUD completo na área administrativa do sistema, seguindo os padrões do projeto Comprae.

## O que é um CRUD?

CRUD significa **C**reate, **R**ead, **U**pdate e **D**elete (Criar, Ler, Atualizar e Deletar). São as 4 operações básicas que você precisa para gerenciar qualquer tipo de dado no sistema.

## Visão Geral da Estrutura

Para criar um CRUD completo, você precisará criar 5 arquivos principais e modificar 2 arquivos existentes:

```
Projeto/
├── model/               → 1. Criar arquivo do modelo
├── sql/                 → 2. Criar arquivo com comandos SQL
├── repo/                → 3. Criar arquivo do repositório
├── dtos/                → 4. Criar arquivo de validação
├── routes/              → 5. Criar arquivo de rotas
├── templates/
│   └── admin/
│       └── [seu_crud]/  → 6. Criar pasta com 3 templates
├── main.py              → 7. Modificar para registrar rotas
└── templates/dashboard.html → 8. Modificar para adicionar card no menu
```

---

## Passo 1: Criar o Modelo (Model)

**Local:** `model/[nome]_model.py`

O modelo define a estrutura dos dados. Use `@dataclass` para facilitar.

### Exemplo baseado em Categorias:

**Arquivo:** `model/categoria_model.py`

```python
from dataclasses import dataclass


@dataclass
class Categoria:
    id: int
    nome: str
    descricao: str
```

### Como adaptar para seu CRUD:

1. Crie um arquivo com o nome no singular: `model/[seu_modelo]_model.py`
2. Defina a classe com `@dataclass`
3. Liste os campos necessários com seus tipos:
   - `id: int` - sempre presente
   - `str` - para textos
   - `int` - para números inteiros
   - `float` - para números decimais
   - `bool` - para verdadeiro/falso
   - `Optional[tipo]` - para campos opcionais

**Exemplo para um CRUD de Fornecedores:**

```python
from dataclasses import dataclass


@dataclass
class Fornecedor:
    id: int
    nome: str
    cnpj: str
    telefone: str
    email: str
```

---

## Passo 2: Criar os Comandos SQL

**Local:** `sql/[nome]_sql.py`

Este arquivo contém todos os comandos SQL necessários para interagir com o banco de dados.

### Exemplo baseado em Categorias:

**Arquivo:** `sql/categoria_sql.py`

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

### Como adaptar para seu CRUD:

1. **CRIAR_TABELA**: Define a estrutura da tabela
   - `id INTEGER PRIMARY KEY AUTOINCREMENT` - sempre presente
   - `NOT NULL` - campo obrigatório
   - `UNIQUE` - não permite valores duplicados
   - Tipos: `TEXT`, `INTEGER`, `REAL` (decimal), `BLOB` (arquivo)

2. **INSERIR**: Lista os campos sem o ID (ele é automático)

3. **ALTERAR**: Atualiza os campos pelo ID

4. **EXCLUIR**: Remove registro pelo ID

5. **OBTER_POR_ID**: Busca um registro específico

6. **OBTER_TODOS**: Lista todos os registros (pode adicionar ORDER BY)

**Exemplo para Fornecedores:**

```python
CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS fornecedor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cnpj TEXT NOT NULL UNIQUE,
    telefone TEXT NOT NULL,
    email TEXT NOT NULL
)
"""

INSERIR = "INSERT INTO fornecedor (nome, cnpj, telefone, email) VALUES (?, ?, ?, ?)"
ALTERAR = "UPDATE fornecedor SET nome = ?, cnpj = ?, telefone = ?, email = ? WHERE id = ?"
EXCLUIR = "DELETE FROM fornecedor WHERE id = ?"
OBTER_POR_ID = "SELECT * FROM fornecedor WHERE id = ?"
OBTER_TODOS = "SELECT * FROM fornecedor ORDER BY nome"
```

---

## Passo 3: Criar o Repositório (Repository)

**Local:** `repo/[nome]_repo.py`

O repositório executa os comandos SQL e transforma os resultados em objetos do modelo.

### Exemplo baseado em Categorias:

**Arquivo:** `repo/categoria_repo.py`

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

### Como adaptar para seu CRUD:

1. Importe seu modelo e seus comandos SQL
2. Em `inserir()`: liste os campos na ordem do comando INSERIR (sem o ID)
3. Em `alterar()`: liste os campos na ordem do comando ALTERAR (ID por último)
4. Em `obter_por_id()` e `obter_todos()`: construa o objeto com todos os campos do modelo

**Dica:** A ordem dos campos em `cursor.execute()` deve ser exatamente a mesma dos `?` no comando SQL.

---

## Passo 4: Criar os DTOs (Data Transfer Objects)

**Local:** `dtos/[nome]_dto.py`

DTOs fazem a validação dos dados que vêm dos formulários.

### Exemplo baseado em Categorias:

**Arquivo:** `dtos/categoria_dto.py`

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

### Como adaptar para seu CRUD:

**Você precisa criar 2 classes:**

1. **CriarDTO**: Para cadastro (sem ID)
2. **AlterarDTO**: Para edição (com ID)

**Validadores disponíveis (arquivo `dtos/validators.py`):**

- `validar_string_obrigatoria(nome, tamanho_minimo=1, tamanho_maximo=255)`
- `validar_email()`
- `validar_cpf()`
- `validar_cnpj()`
- `validar_telefone()`
- `validar_cep()`
- `validar_numero_positivo()`
- `validar_id_positivo()`

**Exemplo para Fornecedores:**

```python
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_id_positivo,
    validar_cnpj,
    validar_email,
    validar_telefone,
)

class CriarFornecedorDTO(BaseModel):
    nome: str
    cnpj: str
    telefone: str
    email: str

    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=100)
    )
    _validar_cnpj = field_validator("cnpj")(validar_cnpj())
    _validar_telefone = field_validator("telefone")(validar_telefone())
    _validar_email = field_validator("email")(validar_email())

class AlterarFornecedorDTO(BaseModel):
    id: int
    nome: str
    cnpj: str
    telefone: str
    email: str

    _validar_id = field_validator("id")(validar_id_positivo())
    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=100)
    )
    _validar_cnpj = field_validator("cnpj")(validar_cnpj())
    _validar_telefone = field_validator("telefone")(validar_telefone())
    _validar_email = field_validator("email")(validar_email())
```

---

## Passo 5: Criar as Rotas (Routes)

**Local:** `routes/admin_[nome]_routes.py`

As rotas conectam as URLs às funções que processam as requisições.

### Estrutura do arquivo de rotas:

```python
from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.[seu_dto] import Criar[Seu]DTO, Alterar[Seu]DTO
from model.[seu_model] import [SeuModelo]
from repo import [seu]_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil
from util.exceptions import FormValidationError
from util.rate_limiter import RateLimiter, obter_identificador_cliente

router = APIRouter(prefix="/admin/[seu_recurso]")
templates = criar_templates("templates/admin/[seu_recurso]")

# Rate limiter para operações admin
admin_[seu_recurso]_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_[seu_recurso]",
)
```

### As 6 rotas necessárias:

#### 1. Index (Redireciona para listar)

```python
@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista"""
    return RedirectResponse("/admin/[seu_recurso]/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
```

#### 2. Listar (GET)

```python
@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todos os registros"""
    itens = [seu]_repo.obter_todos()
    return templates.TemplateResponse(
        "admin/[seu_recurso]/listar.html",
        {"request": request, "[itens]": itens}
    )
```

#### 3. Cadastrar GET (Mostra formulário)

```python
@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro"""
    return templates.TemplateResponse(
        "admin/[seu_recurso]/cadastro.html",
        {"request": request}
    )
```

#### 4. Cadastrar POST (Processa formulário)

```python
@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    # Liste aqui todos os campos do formulário:
    campo1: str = Form(...),
    campo2: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Cadastra um novo registro"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_[seu_recurso]_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/[seu_recurso]/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {
        "campo1": campo1,
        "campo2": campo2,
    }

    try:
        # Validar com DTO
        dto = Criar[Seu]DTO(
            campo1=campo1,
            campo2=campo2
        )

        # Criar objeto
        item = [SeuModelo](
            id=0,
            campo1=dto.campo1,
            campo2=dto.campo2
        )

        [seu]_repo.inserir(item)
        logger.info(f"[SeuModelo] '{dto.campo1}' cadastrado por admin {usuario_logado['id']}")

        informar_sucesso(request, "[SeuModelo] cadastrado com sucesso!")
        return RedirectResponse("/admin/[seu_recurso]/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="admin/[seu_recurso]/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="campo1",
        )
```

#### 5. Editar GET (Mostra formulário preenchido)

```python
@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário de alteração"""
    item = [seu]_repo.obter_por_id(id)

    if not item:
        informar_erro(request, "[SeuModelo] não encontrado")
        return RedirectResponse("/admin/[seu_recurso]/listar", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "admin/[seu_recurso]/editar.html",
        {
            "request": request,
            "[item]": item,
            "dados": item.__dict__
        }
    )
```

#### 6. Editar POST (Processa alteração)

```python
@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    campo1: str = Form(...),
    campo2: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Altera dados de um registro"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_[seu_recurso]_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/[seu_recurso]/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se existe
    item_atual = [seu]_repo.obter_por_id(id)
    if not item_atual:
        informar_erro(request, "[SeuModelo] não encontrado")
        return RedirectResponse("/admin/[seu_recurso]/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {
        "id": id,
        "campo1": campo1,
        "campo2": campo2
    }

    try:
        # Validar com DTO
        dto = Alterar[Seu]DTO(
            id=id,
            campo1=campo1,
            campo2=campo2
        )

        # Atualizar objeto
        item_atualizado = [SeuModelo](
            id=id,
            campo1=dto.campo1,
            campo2=dto.campo2
        )

        [seu]_repo.alterar(item_atualizado)
        logger.info(f"[SeuModelo] {id} alterado por admin {usuario_logado['id']}")

        informar_sucesso(request, "[SeuModelo] alterado com sucesso!")
        return RedirectResponse("/admin/[seu_recurso]/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Adicionar item aos dados para renderizar o template
        dados_formulario["[item]"] = [seu]_repo.obter_por_id(id)
        raise FormValidationError(
            validation_error=e,
            template_path="admin/[seu_recurso]/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="campo1",
        )
```

#### 7. Excluir POST

```python
@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exclui um registro"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_[seu_recurso]_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/[seu_recurso]/listar", status_code=status.HTTP_303_SEE_OTHER)

    item = [seu]_repo.obter_por_id(id)

    if not item:
        informar_erro(request, "[SeuModelo] não encontrado")
        return RedirectResponse("/admin/[seu_recurso]/listar", status_code=status.HTTP_303_SEE_OTHER)

    try:
        [seu]_repo.excluir(id)
        logger.info(f"[SeuModelo] {id} excluído por admin {usuario_logado['id']}")
        informar_sucesso(request, "[SeuModelo] excluído com sucesso!")
    except Exception as e:
        # Captura erro de FK constraint (registros vinculados)
        logger.error(f"Erro ao excluir [SeuModelo] {id}: {str(e)}")
        informar_erro(request, "Não é possível excluir este registro pois existem dados vinculados a ele.")

    return RedirectResponse("/admin/[seu_recurso]/listar", status_code=status.HTTP_303_SEE_OTHER)
```

---

## Passo 6: Criar os Templates HTML

**Local:** `templates/admin/[seu_recurso]/`

Crie uma pasta com o nome do seu recurso (plural) dentro de `templates/admin/` e adicione 3 arquivos HTML.

### 6.1. Template de Listagem

**Arquivo:** `templates/admin/[seu_recurso]/listar.html`

```html
{% extends "base_privada.html" %}

{% block titulo %}Gerenciar [Seus Itens]{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-[seu-icone]"></i> Gerenciar [Seus Itens]</h2>
            <a href="/admin/[seu_recurso]/cadastrar" class="btn btn-primary">
                <i class="bi bi-plus-circle"></i> Novo [Item]
            </a>
        </div>

        <div class="card shadow-sm">
            <div class="card-body">
                {% if [itens] %}
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th scope="col">ID</th>
                                <th scope="col">Campo 1</th>
                                <th scope="col">Campo 2</th>
                                <th scope="col" class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for item in [itens] %}
                            <tr>
                                <td>{{ item.id }}</td>
                                <td>{{ item.campo1 }}</td>
                                <td>{{ item.campo2 }}</td>
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm" role="group">
                                        <a href="/admin/[seu_recurso]/editar/{{ item.id }}"
                                            class="btn btn-outline-primary"
                                            title="Editar"
                                            aria-label="Editar {{ item.campo1 }}">
                                            <i class="bi bi-pencil"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-danger"
                                            title="Excluir"
                                            aria-label="Excluir {{ item.campo1 }}"
                                            onclick="excluir[SeuModelo]({{ item.id }}, '{{ item.campo1|replace("'", "\\'") }}', '{{ item.campo2|replace("'", "\\'") }}')">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="alert alert-info text-center mb-0">
                    <i class="bi bi-info-circle"></i> Nenhum [item] cadastrado.
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    /**
     * Função para excluir um item
     */
    function excluir[SeuModelo](itemId, campo1, campo2) {
        const detalhes = `
        <div class="card bg-light">
            <div class="card-body">
                <table class="table table-sm table-borderless mb-0">
                    <tr>
                        <th scope="row" width="30%">Campo 1:</th>
                        <td>${campo1}</td>
                    </tr>
                    <tr>
                        <th scope="row">Campo 2:</th>
                        <td>${campo2}</td>
                    </tr>
                </table>
            </div>
        </div>
    `;

        abrirModalConfirmacao({
            url: `/admin/[seu_recurso]/excluir/${itemId}`,
            mensagem: 'Tem certeza que deseja excluir este [item]?',
            detalhes: detalhes
        });
    }
</script>
{% endblock %}
```

**Ícones Bootstrap disponíveis:** Veja em https://icons.getbootstrap.com/
Exemplos: `bi-tag`, `bi-people`, `bi-box`, `bi-cart`, `bi-truck`, `bi-building`, `bi-person-badge`

### 6.2. Template de Cadastro

**Arquivo:** `templates/admin/[seu_recurso]/cadastro.html`

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Cadastrar [Item]{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="d-flex align-items-center mb-4">
            <h2 class="mb-0"><i class="bi bi-[seu-icone]-fill"></i> Cadastrar Novo [Item]</h2>
        </div>

        <div class="card shadow-sm">
            <form method="POST" action="/admin/[seu_recurso]/cadastrar">
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-12">
                            {% include "components/alerta_erro.html" %}
                        </div>

                        <!-- Adicione um campo para cada atributo do seu modelo -->
                        <div class="col-12 mb-3">
                            {{ field(name='campo1', label='Nome do Campo 1', type='text', required=true,
                                   placeholder='Digite aqui...') }}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='campo2', label='Nome do Campo 2', type='textarea', required=true, rows=4,
                                   placeholder='Digite aqui...') }}
                        </div>
                    </div>
                </div>
                <div class="card-footer p-4">
                    <div class="d-flex gap-3">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle"></i> Cadastrar
                        </button>
                        <a href="/admin/[seu_recurso]/listar" class="btn btn-secondary">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </a>
                    </div>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

**Tipos de campos disponíveis no macro `field`:**
- `type='text'` - Campo de texto simples
- `type='textarea'` - Campo de texto grande (use `rows=4` para definir altura)
- `type='email'` - Campo de email
- `type='number'` - Campo numérico
- `type='date'` - Campo de data
- `type='tel'` - Campo de telefone
- `type='password'` - Campo de senha

### 6.3. Template de Edição

**Arquivo:** `templates/admin/[seu_recurso]/editar.html`

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Editar [Item]{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="d-flex align-items-center mb-4">
            <h2 class="mb-0"><i class="bi bi-pencil-square"></i> Editar [Item]</h2>
        </div>

        <div class="card shadow-sm">
            <form method="POST" action="/admin/[seu_recurso]/editar/{{ [item].id }}">
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-12">
                            {% include "components/alerta_erro.html" %}
                        </div>

                        <!-- Os mesmos campos do cadastro, mas com value preenchido -->
                        <div class="col-12 mb-3">
                            {{ field(name='campo1', label='Nome do Campo 1', type='text', required=true,
                                   value=dados.campo1 if dados else [item].campo1) }}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='campo2', label='Nome do Campo 2', type='textarea', required=true, rows=4,
                                   value=dados.campo2 if dados else [item].campo2) }}
                        </div>
                    </div>
                </div>
                <div class="card-footer p-4">
                    <div class="d-flex gap-3">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle"></i> Salvar Alterações
                        </button>
                        <a href="/admin/[seu_recurso]/listar" class="btn btn-secondary">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </a>
                    </div>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

---

## Passo 7: Registrar as Rotas no main.py

**Local:** `main.py`

Você precisa adicionar duas linhas no arquivo `main.py`:

1. **Importar o router** (no início do arquivo, junto com os outros imports):

```python
from routes import admin_[seu_recurso]_routes
```

2. **Registrar o router** (onde estão os outros `app.include_router()`):

```python
app.include_router(admin_[seu_recurso]_routes.router)
```

**Exemplo para Fornecedores:**

```python
# No início do arquivo
from routes import admin_fornecedores_routes

# Mais abaixo, junto com os outros routers
app.include_router(admin_fornecedores_routes.router)
```

---

## Passo 8: Adicionar Card no Dashboard

**Local:** `templates/dashboard.html`

Adicione um card para acessar seu CRUD no dashboard. Localize a seção onde estão os outros cards (procure por `{% if perfil == 'Administrador' %}`) e adicione:

```html
<div class="col-md-4">
    <div class="card h-100 shadow-sm shadow-hover">
        <div class="card-body text-center">
            <div class="mb-3">
                <i class="bi bi-[seu-icone] text-primary display-3"></i>
            </div>
            <h5 class="card-title">[Nome do Seu CRUD]</h5>
            <p class="card-text text-muted">
                [Descrição do que este CRUD gerencia]
            </p>
            <a href="/admin/[seu_recurso]/listar" class="btn btn-primary">
                <i class="bi bi-arrow-right-circle"></i> Acessar
            </a>
        </div>
    </div>
</div>
```

**Exemplo para Fornecedores:**

```html
<div class="col-md-4">
    <div class="card h-100 shadow-sm shadow-hover">
        <div class="card-body text-center">
            <div class="mb-3">
                <i class="bi bi-truck text-primary display-3"></i>
            </div>
            <h5 class="card-title">Fornecedores</h5>
            <p class="card-text text-muted">
                Gerencie os fornecedores de produtos do sistema
            </p>
            <a href="/admin/fornecedores/listar" class="btn btn-primary">
                <i class="bi bi-arrow-right-circle"></i> Acessar
            </a>
        </div>
    </div>
</div>
```

---

## Passo 9: Criar a Tabela no Banco de Dados

Depois de criar todos os arquivos, você precisa criar a tabela no banco de dados.

**Opção 1:** Adicionar no arquivo `create_tables.py`

Abra o arquivo `create_tables.py` e adicione:

```python
import [seu]_repo
[seu]_repo.criar_tabela()
```

Depois execute:

```bash
python create_tables.py
```

**Opção 2:** Criar manualmente usando Python:

```python
from repo import [seu]_repo
[seu]_repo.criar_tabela()
```

---

## Checklist Final

Antes de testar seu CRUD, verifique se você:

### Arquivos Backend (Python)

- [ ] Criou `model/[nome]_model.py` com a classe do modelo
- [ ] Criou `sql/[nome]_sql.py` com todos os comandos SQL (CRIAR_TABELA, INSERIR, ALTERAR, EXCLUIR, OBTER_POR_ID, OBTER_TODOS)
- [ ] Criou `repo/[nome]_repo.py` com todas as funções (criar_tabela, inserir, alterar, excluir, obter_por_id, obter_todos)
- [ ] Criou `dtos/[nome]_dto.py` com as classes CriarDTO e AlterarDTO
- [ ] Criou `routes/admin_[nome]_routes.py` com todas as 7 rotas (index, listar GET, cadastrar GET, cadastrar POST, editar GET, editar POST, excluir POST)

### Arquivos Frontend (HTML)

- [ ] Criou pasta `templates/admin/[seu_recurso]/`
- [ ] Criou `templates/admin/[seu_recurso]/listar.html` com a tabela e função JavaScript de exclusão
- [ ] Criou `templates/admin/[seu_recurso]/cadastro.html` com o formulário de cadastro
- [ ] Criou `templates/admin/[seu_recurso]/editar.html` com o formulário de edição

### Configurações

- [ ] Adicionou import no `main.py`
- [ ] Registrou o router no `main.py` com `app.include_router()`
- [ ] Adicionou card no `templates/dashboard.html`
- [ ] Criou a tabela no banco de dados

### Testes

- [ ] Consegue acessar o card no dashboard
- [ ] Consegue abrir a página de listagem
- [ ] Consegue cadastrar um novo registro
- [ ] Consegue editar um registro existente
- [ ] Consegue excluir um registro
- [ ] Validações estão funcionando corretamente
- [ ] Mensagens de sucesso/erro aparecem corretamente

---

## Exemplo Completo: CRUD de Marcas

Vamos criar um exemplo completo de um CRUD de Marcas (para produtos).

### 1. Model (`model/marca_model.py`)

```python
from dataclasses import dataclass


@dataclass
class Marca:
    id: int
    nome: str
    descricao: str
```

### 2. SQL (`sql/marca_sql.py`)

```python
CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS marca (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT NOT NULL
)
"""

INSERIR = "INSERT INTO marca (nome, descricao) VALUES (?, ?)"
ALTERAR = "UPDATE marca SET nome = ?, descricao = ? WHERE id = ?"
EXCLUIR = "DELETE FROM marca WHERE id = ?"
OBTER_POR_ID = "SELECT * FROM marca WHERE id = ?"
OBTER_TODOS = "SELECT * FROM marca ORDER BY nome"
```

### 3. Repository (`repo/marca_repo.py`)

```python
from typing import Optional
from model.marca_model import Marca
from sql.marca_sql import *
from util.db_util import get_connection

def criar_tabela() -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True

def inserir(marca: Marca) -> Optional[int]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (marca.nome, marca.descricao))
        return cursor.lastrowid

def alterar(marca: Marca) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ALTERAR, (marca.nome, marca.descricao, marca.id))
        return cursor.rowcount > 0

def excluir(id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0

def obter_por_id(id: int) -> Optional[Marca]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        if row:
            return Marca(
                id=row["id"],
                nome=row["nome"],
                descricao=row["descricao"]
            )
        return None

def obter_todos() -> list[Marca]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [
            Marca(
                id=row["id"],
                nome=row["nome"],
                descricao=row["descricao"]
            )
            for row in rows
        ]
```

### 4. DTOs (`dtos/marca_dto.py`)

```python
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_id_positivo,
)

class CriarMarcaDTO(BaseModel):
    nome: str
    descricao: str

    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria("Descrição", tamanho_maximo=200)
    )

class AlterarMarcaDTO(BaseModel):
    id: int
    nome: str
    descricao: str

    _validar_id = field_validator("id")(validar_id_positivo())
    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria("Descrição", tamanho_maximo=200)
    )
```

### 5. Routes (`routes/admin_marcas_routes.py`)

```python
from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.marca_dto import CriarMarcaDTO, AlterarMarcaDTO
from model.marca_model import Marca
from repo import marca_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil
from util.exceptions import FormValidationError
from util.rate_limiter import RateLimiter, obter_identificador_cliente

router = APIRouter(prefix="/admin/marcas")
templates = criar_templates("templates/admin/marcas")

admin_marcas_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_marcas",
)

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    return RedirectResponse("/admin/marcas/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    marcas = marca_repo.obter_todos()
    return templates.TemplateResponse(
        "admin/marcas/listar.html",
        {"request": request, "marcas": marcas}
    )

@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    return templates.TemplateResponse(
        "admin/marcas/cadastro.html",
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
    assert usuario_logado is not None

    ip = obter_identificador_cliente(request)
    if not admin_marcas_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/marcas/listar", status_code=status.HTTP_303_SEE_OTHER)

    dados_formulario: dict = {"nome": nome, "descricao": descricao}

    try:
        dto = CriarMarcaDTO(nome=nome, descricao=descricao)
        marca = Marca(id=0, nome=dto.nome, descricao=dto.descricao)
        marca_repo.inserir(marca)
        logger.info(f"Marca '{dto.nome}' cadastrada por admin {usuario_logado['id']}")
        informar_sucesso(request, "Marca cadastrada com sucesso!")
        return RedirectResponse("/admin/marcas/listar", status_code=status.HTTP_303_SEE_OTHER)
    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="admin/marcas/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome",
        )

@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    marca = marca_repo.obter_por_id(id)
    if not marca:
        informar_erro(request, "Marca não encontrada")
        return RedirectResponse("/admin/marcas/listar", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        "admin/marcas/editar.html",
        {"request": request, "marca": marca, "dados": marca.__dict__}
    )

@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    nome: str = Form(...),
    descricao: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    assert usuario_logado is not None

    ip = obter_identificador_cliente(request)
    if not admin_marcas_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/marcas/listar", status_code=status.HTTP_303_SEE_OTHER)

    marca_atual = marca_repo.obter_por_id(id)
    if not marca_atual:
        informar_erro(request, "Marca não encontrada")
        return RedirectResponse("/admin/marcas/listar", status_code=status.HTTP_303_SEE_OTHER)

    dados_formulario: dict = {"id": id, "nome": nome, "descricao": descricao}

    try:
        dto = AlterarMarcaDTO(id=id, nome=nome, descricao=descricao)
        marca_atualizada = Marca(id=id, nome=dto.nome, descricao=dto.descricao)
        marca_repo.alterar(marca_atualizada)
        logger.info(f"Marca {id} alterada por admin {usuario_logado['id']}")
        informar_sucesso(request, "Marca alterada com sucesso!")
        return RedirectResponse("/admin/marcas/listar", status_code=status.HTTP_303_SEE_OTHER)
    except ValidationError as e:
        dados_formulario["marca"] = marca_repo.obter_por_id(id)
        raise FormValidationError(
            validation_error=e,
            template_path="admin/marcas/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome",
        )

@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(request: Request, id: int, usuario_logado: Optional[dict] = None):
    assert usuario_logado is not None

    ip = obter_identificador_cliente(request)
    if not admin_marcas_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/marcas/listar", status_code=status.HTTP_303_SEE_OTHER)

    marca = marca_repo.obter_por_id(id)
    if not marca:
        informar_erro(request, "Marca não encontrada")
        return RedirectResponse("/admin/marcas/listar", status_code=status.HTTP_303_SEE_OTHER)

    try:
        marca_repo.excluir(id)
        logger.info(f"Marca {id} ({marca.nome}) excluída por admin {usuario_logado['id']}")
        informar_sucesso(request, "Marca excluída com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao excluir marca {id}: {str(e)}")
        informar_erro(request, "Não é possível excluir esta marca pois existem produtos vinculados a ela.")

    return RedirectResponse("/admin/marcas/listar", status_code=status.HTTP_303_SEE_OTHER)
```

### 6. Templates

Crie a pasta `templates/admin/marcas/` e adicione os 3 arquivos HTML conforme os exemplos do Passo 6.

### 7. Registrar no main.py

```python
# Import
from routes import admin_marcas_routes

# Registro
app.include_router(admin_marcas_routes.router)
```

### 8. Card no Dashboard

```html
<div class="col-md-4">
    <div class="card h-100 shadow-sm shadow-hover">
        <div class="card-body text-center">
            <div class="mb-3">
                <i class="bi bi-award text-primary display-3"></i>
            </div>
            <h5 class="card-title">Marcas</h5>
            <p class="card-text text-muted">
                Gerencie as marcas de produtos do sistema
            </p>
            <a href="/admin/marcas/listar" class="btn btn-primary">
                <i class="bi bi-arrow-right-circle"></i> Acessar
            </a>
        </div>
    </div>
</div>
```

---

## Dicas Importantes

### Nomenclatura

- **Arquivos Python:** Use snake_case (ex: `categoria_model.py`)
- **Classes Python:** Use PascalCase (ex: `class Categoria`)
- **Funções Python:** Use snake_case (ex: `def obter_todos()`)
- **Rotas:** Use plural e kebab-case (ex: `/admin/categorias`)
- **Variáveis de template:** Use snake_case (ex: `{{ categoria.nome }}`)

### Ordem dos campos

Mantenha sempre a mesma ordem dos campos em:
- Comandos SQL
- Parâmetros das funções do repositório
- DTOs
- Templates HTML

### Testes

Sempre teste seu CRUD na seguinte ordem:
1. Cadastrar vários registros
2. Listar e verificar se todos aparecem
3. Editar alguns registros
4. Excluir um registro sem vínculos
5. Testar validações (campos vazios, tamanhos inválidos)

### Segurança

O projeto já implementa:
- Autenticação (apenas admin acessa)
- Rate limiting (evita spam)
- Validação de dados (DTOs)
- Proteção contra SQL injection (prepared statements)
- CSRF protection

### Boas Práticas

1. Sempre use `Optional[dict] = None` para `usuario_logado`
2. Sempre use `status.HTTP_303_SEE_OTHER` em redirects POST
3. Sempre capture exceções ao excluir (pode ter FK constraint)
4. Sempre adicione logs importantes
5. Sempre valide se o registro existe antes de editar/excluir

---

## Problemas Comuns

### Erro: "Table already exists"

**Solução:** A tabela já foi criada. Ignore o erro ou delete o banco de dados e crie novamente.

### Erro: "Template not found"

**Solução:** Verifique se:
- A pasta `templates/admin/[seu_recurso]/` existe
- Os nomes dos arquivos HTML estão corretos
- O caminho no `criar_templates()` está correto

### Erro: "Router not found" ou rota não funciona

**Solução:** Verifique se:
- Você importou o router no `main.py`
- Você registrou com `app.include_router()`
- O prefix do router está correto

### Erro de validação não aparece no formulário

**Solução:** Verifique se:
- Você incluiu `{% include "components/alerta_erro.html" %}` no template
- O nome do campo no template é igual ao do DTO
- Você está capturando `ValidationError` e lançando `FormValidationError`

### Card não aparece no dashboard

**Solução:** Verifique se:
- O card está dentro do bloco `{% if perfil == 'Administrador' %}`
- Você está logado como administrador
- A sintaxe HTML está correta

---

## Recursos Adicionais

### Validadores Disponíveis (`dtos/validators.py`)

- `validar_string_obrigatoria(nome_campo, tamanho_minimo=1, tamanho_maximo=255)`
- `validar_email()`
- `validar_cpf()`
- `validar_cnpj()`
- `validar_telefone()`
- `validar_cep()`
- `validar_numero_positivo(nome_campo="Número")`
- `validar_id_positivo()`
- `validar_data_passado(nome_campo="Data")`
- `validar_data_futuro(nome_campo="Data")`

### Funções Úteis

- `informar_sucesso(request, mensagem)` - Mostra mensagem verde
- `informar_erro(request, mensagem)` - Mostra mensagem vermelha
- `obter_usuario_logado(request)` - Retorna usuário da sessão
- `logger.info(mensagem)` - Registra log informativo
- `logger.error(mensagem)` - Registra log de erro

---

## Conclusão

Seguindo este manual, você conseguirá criar qualquer CRUD na área administrativa do sistema. Lembre-se de:

1. Seguir a ordem dos passos
2. Adaptar os exemplos para seu caso
3. Testar cada funcionalidade
4. Manter o padrão do projeto
5. Perguntar se tiver dúvidas

Boa sorte com seu projeto!
