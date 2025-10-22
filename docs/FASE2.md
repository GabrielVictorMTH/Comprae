# FASE 2 - IMPLEMENTAÇÃO DAS ROTAS ADMINISTRATIVAS DO COMPRAÊ

**Projeto**: Compraê - Plataforma de Marketplace Local
**Data**: 22/10/2025
**Versão**: 1.0
**Autor**: Sistema de Planejamento

---

## 📑 ÍNDICE

1. [Introdução](#introdução)
   - [Padrões Obrigatórios](#padrões-obrigatórios-a-seguir)
2. [Status da Implementação](#status-da-implementação)
3. [1. Gerenciamento de Categorias](#1-gerenciamento-de-categorias)
   - [1.1. Listar Categorias](#11-listar-categorias)
   - [1.2. Cadastrar Categoria](#12-cadastrar-categoria)
   - [1.3. Editar Categoria](#13-editar-categoria)
   - [1.4. Excluir Categoria](#14-excluir-categoria)
4. [2. Gerenciamento de Produtos](#2-gerenciamento-de-produtos-moderação)
   - [2.1. Listar Produtos](#21-listar-produtos)
   - [2.2. Moderar Produtos](#22-moderar-produtos-aprovarreprovar)
   - [2.3. Editar Produto](#23-editar-produto-admin)
   - [2.4. Excluir Produto](#24-excluir-produto)
5. [3. Registro de Rotas](#3-registro-de-rotas-no-mainpy)
6. [4. Atualização da Navegação](#4-atualização-da-navegação-navbar)
7. [5. Checklist de Implementação](#5-checklist-de-implementação)
8. [6. Testes Recomendados](#6-testes-recomendados)
9. [7. Observações Finais](#7-observações-finais)

---

## INTRODUÇÃO

Este documento descreve o plano de implementação completo das funcionalidades administrativas do projeto Compraê, seguindo rigorosamente os padrões arquiteturais e de código do projeto DefaultWebApp (forkado como base).

### Padrões Obrigatórios a Seguir

1. **Estrutura de Arquivos**:
   - Rotas: `routes/admin_{recurso}_routes.py`
   - DTOs: `dtos/{recurso}_dto.py`
   - Templates: `templates/admin/{recurso}/`
   - Repositórios: `repo/{recurso}_repo.py` (já existentes)

2. **Padrões de Código**:
   - Decorador `@requer_autenticacao([Perfil.ADMIN.value])` em todas as rotas
   - Rate limiting com `RateLimiter`
   - Flash messages: `informar_sucesso()`, `informar_erro()`
   - Validação com DTOs Pydantic
   - Exception handling com `FormValidationError`
   - Logging de todas as operações

3. **Padrões de Templates**:
   - Herdar de `base_privada.html`
   - Usar macros de `templates/macros/form_fields.html`
   - Usar componentes de `templates/components/`
   - Modal de confirmação para exclusões
   - Bootstrap 5 para estilização

4. **Fluxo de Rotas**:
   - `GET /admin/{recurso}/listar` - Lista todos os registros
   - `GET /admin/{recurso}/cadastrar` - Exibe formulário de cadastro
   - `POST /admin/{recurso}/cadastrar` - Processa cadastro
   - `GET /admin/{recurso}/editar/{id}` - Exibe formulário de edição
   - `POST /admin/{recurso}/editar/{id}` - Processa edição
   - `POST /admin/{recurso}/excluir/{id}` - Exclui registro

---

## STATUS DA IMPLEMENTAÇÃO

**Data de Conclusão**: 22/10/2025
**Resultado dos Testes**: ✅ 302 testes passando, 0 falhas
**Status Geral**: ✅ **FASE 2 CONCLUÍDA**

### Resumo Executivo

A FASE 2 contempla exclusivamente as **rotas administrativas** do Compraê, permitindo que administradores gerenciem categorias e produtos (incluindo moderação).

| Módulo | Status | Rotas | Templates | DTOs |
|--------|--------|-------|-----------|------|
| **Categorias** | ✅ Completo | 7 rotas | 3 templates | 2 (já existiam) |
| **Produtos** | ✅ Completo | 11 rotas | 3 templates | 1 novo + 1 existente |
| **Integração** | ✅ Completo | main.py + navbar | - | - |

### Arquivos Criados

**Rotas:**
- ✅ `routes/admin_categorias_routes.py` (226 linhas)
- ✅ `routes/admin_produtos_routes.py` (273 linhas)

**Templates:**
- ✅ `templates/admin/categorias/listar.html`
- ✅ `templates/admin/categorias/cadastro.html`
- ✅ `templates/admin/categorias/editar.html`
- ✅ `templates/admin/produtos/listar.html`
- ✅ `templates/admin/produtos/moderar.html`
- ✅ `templates/admin/produtos/editar.html`

**DTOs:**
- ✅ `ModerarProdutoDTO` adicionado em `dtos/anuncio_dto.py`

**Arquivos Modificados:**
- ✅ `main.py` - Importações e registro dos routers
- ✅ `templates/base_privada.html` - Adição de itens na navbar admin

### Funcionalidades Implementadas

**Gerenciamento de Categorias (Admin):**
- Listar todas as categorias
- Criar nova categoria
- Editar categoria existente
- Excluir categoria (com validação de FK constraint)

**Gerenciamento/Moderação de Produtos (Admin):**
- Listar todos os produtos (ativos e inativos)
- Listar produtos pendentes de moderação
- Aprovar produto (tornar ativo)
- Reprovar produto com motivo registrado em log
- Editar produto (incluindo status ativo/inativo)
- Excluir produto (com validação de FK constraint)

---

## 1. GERENCIAMENTO DE CATEGORIAS

**Prioridade**: 🔴 ALTA
**Requisito**: RF8 - O sistema deve permitir que administradores gerenciem categorias
**Status**: ✅ **IMPLEMENTADO E TESTADO** (22/10/2025)

### 1.1. Listar Categorias

#### 1.1.1. Rota GET: Listar

**Arquivo**: `routes/admin_categorias_routes.py`

```python
from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.categoria_dto import CriarCategoriaDTO, AlterarCategoriaDTO
from model.categoria_model import Categoria
from repo import categoria_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil
from util.exceptions import FormValidationError
from util.rate_limiter import RateLimiter, obter_identificador_cliente

router = APIRouter(prefix="/admin/categorias")
templates = criar_templates("templates/admin/categorias")

# Rate limiter para operações admin
admin_categorias_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_categorias",
)

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de categorias"""
    return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todas as categorias do sistema"""
    categorias = categoria_repo.obter_todos()
    return templates.TemplateResponse(
        "admin/categorias/listar.html",
        {"request": request, "categorias": categorias}
    )
```

#### 1.1.2. Template: Listar Categorias

**Arquivo**: `templates/admin/categorias/listar.html`

```html
{% extends "base_privada.html" %}

{% block titulo %}Gerenciar Categorias{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-tag"></i> Gerenciar Categorias</h2>
            <a href="/admin/categorias/cadastrar" class="btn btn-primary">
                <i class="bi bi-plus-circle"></i> Nova Categoria
            </a>
        </div>

        <div class="card shadow-sm">
            <div class="card-body">
                {% if categorias %}
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th scope="col">ID</th>
                                <th scope="col">Nome</th>
                                <th scope="col">Descrição</th>
                                <th scope="col" class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for categoria in categorias %}
                            <tr>
                                <td>{{ categoria.id }}</td>
                                <td>{{ categoria.nome }}</td>
                                <td>{{ categoria.descricao }}</td>
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm" role="group">
                                        <a href="/admin/categorias/editar/{{ categoria.id }}"
                                            class="btn btn-outline-primary"
                                            title="Editar"
                                            aria-label="Editar categoria {{ categoria.nome }}">
                                            <i class="bi bi-pencil"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-danger"
                                            title="Excluir"
                                            aria-label="Excluir categoria {{ categoria.nome }}"
                                            onclick="excluirCategoria({{ categoria.id }}, '{{ categoria.nome|replace("'", "\\'") }}', '{{ categoria.descricao|replace("'", "\\'") }}')">
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
                    <i class="bi bi-info-circle"></i> Nenhuma categoria cadastrada.
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
     * Função para excluir uma categoria
     */
    function excluirCategoria(categoriaId, categoriaNome, categoriaDescricao) {
        const detalhes = `
        <div class="card bg-light">
            <div class="card-body">
                <table class="table table-sm table-borderless mb-0">
                    <tr>
                        <th scope="row" width="30%">Nome:</th>
                        <td>${categoriaNome}</td>
                    </tr>
                    <tr>
                        <th scope="row">Descrição:</th>
                        <td>${categoriaDescricao}</td>
                    </tr>
                </table>
            </div>
        </div>
    `;

        abrirModalConfirmacao({
            url: `/admin/categorias/excluir/${categoriaId}`,
            mensagem: 'Tem certeza que deseja excluir esta categoria?',
            detalhes: detalhes
        });
    }
</script>
{% endblock %}
```

---

### 1.2. Cadastrar Categoria

#### 1.2.1. DTO: Criar Categoria

**Arquivo**: `dtos/categoria_dto.py` ✅ (já existe)

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
```

#### 1.2.2. Rota GET: Formulário de Cadastro

**Arquivo**: `routes/admin_categorias_routes.py` (adicionar)

```python
@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro de categoria"""
    return templates.TemplateResponse(
        "admin/categorias/cadastro.html",
        {"request": request}
    )
```

#### 1.2.3. Template: Cadastro de Categoria

**Arquivo**: `templates/admin/categorias/cadastro.html`

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Cadastrar Categoria{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="d-flex align-items-center mb-4">
            <h2 class="mb-0"><i class="bi bi-tag-fill"></i> Cadastrar Nova Categoria</h2>
        </div>

        <div class="card shadow-sm">
            <form method="POST" action="/admin/categorias/cadastrar">
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-12">
                            {% include "components/alerta_erro.html" %}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='nome', label='Nome da Categoria', type='text', required=true,
                                   placeholder='Ex: Eletrônicos, Livros, Roupas...') }}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='descricao', label='Descrição', type='textarea', required=true, rows=4,
                                   placeholder='Descreva brevemente o tipo de produtos desta categoria...') }}
                        </div>
                    </div>
                </div>
                <div class="card-footer p-4">
                    <div class="d-flex gap-3">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle"></i> Cadastrar
                        </button>
                        <a href="/admin/categorias/listar" class="btn btn-secondary">
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

#### 1.2.4. Rota POST: Processar Cadastro

**Arquivo**: `routes/admin_categorias_routes.py` (adicionar)

```python
@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    descricao: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Cadastra uma nova categoria"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {"nome": nome, "descricao": descricao}

    try:
        # Validar com DTO
        dto = CriarCategoriaDTO(
            nome=nome,
            descricao=descricao
        )

        # Criar categoria
        categoria = Categoria(
            id=0,
            nome=dto.nome,
            descricao=dto.descricao
        )

        categoria_repo.inserir(categoria)
        logger.info(f"Categoria '{dto.nome}' cadastrada por admin {usuario_logado['id']}")

        informar_sucesso(request, "Categoria cadastrada com sucesso!")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="admin/categorias/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome",
        )
```

---

### 1.3. Editar Categoria

#### 1.3.1. DTO: Alterar Categoria

**Arquivo**: `dtos/categoria_dto.py` ✅ (já existe)

```python
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

#### 1.3.2. Rota GET: Formulário de Edição

**Arquivo**: `routes/admin_categorias_routes.py` (adicionar)

```python
@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário de alteração de categoria"""
    categoria = categoria_repo.obter_por_id(id)

    if not categoria:
        informar_erro(request, "Categoria não encontrada")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "admin/categorias/editar.html",
        {
            "request": request,
            "categoria": categoria,
            "dados": categoria.__dict__
        }
    )
```

#### 1.3.3. Template: Edição de Categoria

**Arquivo**: `templates/admin/categorias/editar.html`

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Editar Categoria{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="d-flex align-items-center mb-4">
            <h2 class="mb-0"><i class="bi bi-pencil-square"></i> Editar Categoria</h2>
        </div>

        <div class="card shadow-sm">
            <form method="POST" action="/admin/categorias/editar/{{ categoria.id }}">
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-12">
                            {% include "components/alerta_erro.html" %}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='nome', label='Nome da Categoria', type='text', required=true,
                                   value=dados.nome if dados else categoria.nome) }}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='descricao', label='Descrição', type='textarea', required=true, rows=4,
                                   value=dados.descricao if dados else categoria.descricao) }}
                        </div>
                    </div>
                </div>
                <div class="card-footer p-4">
                    <div class="d-flex gap-3">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle"></i> Salvar Alterações
                        </button>
                        <a href="/admin/categorias/listar" class="btn btn-secondary">
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

#### 1.3.4. Rota POST: Processar Edição

**Arquivo**: `routes/admin_categorias_routes.py` (adicionar)

```python
@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    nome: str = Form(...),
    descricao: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Altera dados de uma categoria"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se categoria existe
    categoria_atual = categoria_repo.obter_por_id(id)
    if not categoria_atual:
        informar_erro(request, "Categoria não encontrada")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {"id": id, "nome": nome, "descricao": descricao}

    try:
        # Validar com DTO
        dto = AlterarCategoriaDTO(
            id=id,
            nome=nome,
            descricao=descricao
        )

        # Atualizar categoria
        categoria_atualizada = Categoria(
            id=id,
            nome=dto.nome,
            descricao=dto.descricao
        )

        categoria_repo.alterar(categoria_atualizada)
        logger.info(f"Categoria {id} alterada por admin {usuario_logado['id']}")

        informar_sucesso(request, "Categoria alterada com sucesso!")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Adicionar categoria aos dados para renderizar o template
        dados_formulario["categoria"] = categoria_repo.obter_por_id(id)
        raise FormValidationError(
            validation_error=e,
            template_path="admin/categorias/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome",
        )
```

---

### 1.4. Excluir Categoria

#### 1.4.1. Rota POST: Excluir

**Arquivo**: `routes/admin_categorias_routes.py` (adicionar)

```python
@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exclui uma categoria"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    categoria = categoria_repo.obter_por_id(id)

    if not categoria:
        informar_erro(request, "Categoria não encontrada")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    try:
        categoria_repo.excluir(id)
        logger.info(f"Categoria {id} ({categoria.nome}) excluída por admin {usuario_logado['id']}")
        informar_sucesso(request, "Categoria excluída com sucesso!")
    except Exception as e:
        # Captura erro de FK constraint (categoria com produtos vinculados)
        logger.error(f"Erro ao excluir categoria {id}: {str(e)}")
        informar_erro(request, "Não é possível excluir esta categoria pois existem produtos vinculados a ela.")

    return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)
```

---

## 2. GERENCIAMENTO DE PRODUTOS (MODERAÇÃO)

**Prioridade**: 🔴 ALTA
**Requisito**: RF16 - O sistema deve permitir que administradores moderem produtos
**Status**: ✅ **IMPLEMENTADO E TESTADO** (22/10/2025)

### 2.1. Listar Produtos

#### 2.1.1. Rota GET: Listar Todos os Produtos

**Arquivo**: `routes/admin_produtos_routes.py` (criar novo)

```python
from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.anuncio_dto import AlterarAnuncioDTO, ModerarProdutoDTO
from model.anuncio_model import Anuncio
from repo import anuncio_repo, categoria_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil
from util.exceptions import FormValidationError
from util.rate_limiter import RateLimiter, obter_identificador_cliente

router = APIRouter(prefix="/admin/produtos")
templates = criar_templates("templates/admin/produtos")

# Rate limiter para operações admin
admin_produtos_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_produtos",
)

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de produtos"""
    return RedirectResponse("/admin/produtos/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todos os produtos do sistema"""
    # Obter todos os anúncios (ativos e inativos)
    anuncios = anuncio_repo.obter_todos()

    return templates.TemplateResponse(
        "admin/produtos/listar.html",
        {"request": request, "anuncios": anuncios}
    )
```

#### 2.1.2. Template: Listar Produtos

**Arquivo**: `templates/admin/produtos/listar.html`

```html
{% extends "base_privada.html" %}

{% block titulo %}Gerenciar Produtos{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-box-seam"></i> Gerenciar Produtos</h2>
            <a href="/admin/produtos/moderar" class="btn btn-warning">
                <i class="bi bi-shield-exclamation"></i> Produtos Pendentes
            </a>
        </div>

        <div class="card shadow-sm">
            <div class="card-body">
                {% if anuncios %}
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th scope="col">ID</th>
                                <th scope="col">Nome</th>
                                <th scope="col">Categoria</th>
                                <th scope="col">Vendedor</th>
                                <th scope="col">Preço</th>
                                <th scope="col">Estoque</th>
                                <th scope="col">Status</th>
                                <th scope="col" class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for anuncio in anuncios %}
                            <tr>
                                <td>{{ anuncio.id }}</td>
                                <td>{{ anuncio.nome }}</td>
                                <td>{{ anuncio.categoria_nome if anuncio.categoria_nome else '-' }}</td>
                                <td>{{ anuncio.vendedor_nome if anuncio.vendedor_nome else '-' }}</td>
                                <td>R$ {{ "%.2f"|format(anuncio.preco) }}</td>
                                <td>{{ anuncio.estoque }}</td>
                                <td>
                                    <span class="badge bg-{{ 'success' if anuncio.ativo else 'danger' }}">
                                        {{ 'Ativo' if anuncio.ativo else 'Inativo' }}
                                    </span>
                                </td>
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm" role="group">
                                        <a href="/admin/produtos/editar/{{ anuncio.id }}"
                                            class="btn btn-outline-primary"
                                            title="Editar"
                                            aria-label="Editar produto {{ anuncio.nome }}">
                                            <i class="bi bi-pencil"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-danger"
                                            title="Excluir"
                                            aria-label="Excluir produto {{ anuncio.nome }}"
                                            onclick="excluirProduto({{ anuncio.id }}, '{{ anuncio.nome|replace("'", "\\'") }}')">
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
                    <i class="bi bi-info-circle"></i> Nenhum produto cadastrado.
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    function excluirProduto(produtoId, produtoNome) {
        const detalhes = `
        <div class="card bg-light">
            <div class="card-body">
                <p class="mb-0"><strong>Produto:</strong> ${produtoNome}</p>
            </div>
        </div>
    `;

        abrirModalConfirmacao({
            url: `/admin/produtos/excluir/${produtoId}`,
            mensagem: 'Tem certeza que deseja excluir este produto?',
            detalhes: detalhes
        });
    }
</script>
{% endblock %}
```

---

### 2.2. Moderar Produtos (Aprovar/Reprovar)

#### 2.2.1. DTO: Moderar Produto

**Arquivo**: `dtos/anuncio_dto.py` (adicionar)

```python
class ModerarProdutoDTO(BaseModel):
    """DTO para reprovar/moderar produto"""
    id: int
    motivo_reprovacao: str

    _validar_id = field_validator("id")(validar_id_positivo())
    _validar_motivo = field_validator("motivo_reprovacao")(
        validar_string_obrigatoria("Motivo", tamanho_minimo=10, tamanho_maximo=500)
    )
```

#### 2.2.2. Rota GET: Página de Moderação

**Arquivo**: `routes/admin_produtos_routes.py` (adicionar)

```python
@router.get("/moderar")
@requer_autenticacao([Perfil.ADMIN.value])
async def moderar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista produtos pendentes de moderação ou inativos"""
    # Obter todos os produtos inativos (pendentes de aprovação)
    anuncios = anuncio_repo.obter_todos()
    anuncios_pendentes = [a for a in anuncios if not a.ativo]

    return templates.TemplateResponse(
        "admin/produtos/moderar.html",
        {"request": request, "anuncios": anuncios_pendentes}
    )
```

#### 2.2.3. Template: Moderação de Produtos

**Arquivo**: `templates/admin/produtos/moderar.html`

```html
{% extends "base_privada.html" %}

{% block titulo %}Moderar Produtos{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-shield-exclamation"></i> Moderar Produtos</h2>
            <a href="/admin/produtos/listar" class="btn btn-secondary">
                <i class="bi bi-arrow-left"></i> Voltar para Lista Completa
            </a>
        </div>

        <div class="card shadow-sm">
            <div class="card-body">
                {% if anuncios %}
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th scope="col">ID</th>
                                <th scope="col">Nome</th>
                                <th scope="col">Categoria</th>
                                <th scope="col">Vendedor</th>
                                <th scope="col">Preço</th>
                                <th scope="col" class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for anuncio in anuncios %}
                            <tr>
                                <td>{{ anuncio.id }}</td>
                                <td>{{ anuncio.nome }}</td>
                                <td>{{ anuncio.categoria_nome if anuncio.categoria_nome else '-' }}</td>
                                <td>{{ anuncio.vendedor_nome if anuncio.vendedor_nome else '-' }}</td>
                                <td>R$ {{ "%.2f"|format(anuncio.preco) }}</td>
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm" role="group">
                                        <button type="button" class="btn btn-outline-success"
                                            title="Aprovar"
                                            onclick="aprovarProduto({{ anuncio.id }}, '{{ anuncio.nome|replace("'", "\\'") }}')">
                                            <i class="bi bi-check-circle"></i> Aprovar
                                        </button>
                                        <button type="button" class="btn btn-outline-danger"
                                            title="Reprovar"
                                            onclick="reprovarProduto({{ anuncio.id }}, '{{ anuncio.nome|replace("'", "\\'") }}')">
                                            <i class="bi bi-x-circle"></i> Reprovar
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="alert alert-success text-center mb-0">
                    <i class="bi bi-check-circle"></i> Nenhum produto pendente de moderação!
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- Modal para reprovar produto -->
<div class="modal fade" id="modalReprovar" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <form method="POST" id="formReprovar">
                <div class="modal-header">
                    <h5 class="modal-title">Reprovar Produto</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>Produto: <strong id="produtoNomeReprovar"></strong></p>
                    <div class="mb-3">
                        <label for="motivo_reprovacao" class="form-label">Motivo da Reprovação *</label>
                        <textarea class="form-control" id="motivo_reprovacao" name="motivo_reprovacao"
                                  rows="4" required minlength="10" maxlength="500"
                                  placeholder="Descreva o motivo da reprovação..."></textarea>
                        <div class="form-text">Mínimo 10 caracteres, máximo 500.</div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="submit" class="btn btn-danger">Reprovar Produto</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    function aprovarProduto(produtoId, produtoNome) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/produtos/aprovar/${produtoId}`;

        if (confirm(`Deseja aprovar o produto "${produtoNome}"?`)) {
            document.body.appendChild(form);
            form.submit();
        }
    }

    function reprovarProduto(produtoId, produtoNome) {
        document.getElementById('produtoNomeReprovar').textContent = produtoNome;
        document.getElementById('formReprovar').action = `/admin/produtos/reprovar/${produtoId}`;

        const modal = new bootstrap.Modal(document.getElementById('modalReprovar'));
        modal.show();
    }
</script>
{% endblock %}
```

#### 2.2.4. Rota POST: Aprovar Produto

**Arquivo**: `routes/admin_produtos_routes.py` (adicionar)

```python
@router.post("/aprovar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def aprovar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Aprova um produto (torna ativo)"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_produtos_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/produtos/moderar", status_code=status.HTTP_303_SEE_OTHER)

    anuncio = anuncio_repo.obter_por_id(id)

    if not anuncio:
        informar_erro(request, "Produto não encontrado")
        return RedirectResponse("/admin/produtos/moderar", status_code=status.HTTP_303_SEE_OTHER)

    # Ativar produto
    anuncio.ativo = True
    anuncio_repo.alterar(anuncio)

    logger.info(f"Produto {id} ({anuncio.nome}) aprovado por admin {usuario_logado['id']}")
    informar_sucesso(request, f"Produto '{anuncio.nome}' aprovado com sucesso!")

    return RedirectResponse("/admin/produtos/moderar", status_code=status.HTTP_303_SEE_OTHER)
```

#### 2.2.5. Rota POST: Reprovar Produto

**Arquivo**: `routes/admin_produtos_routes.py` (adicionar)

```python
@router.post("/reprovar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def reprovar(
    request: Request,
    id: int,
    motivo_reprovacao: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Reprova um produto com motivo"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_produtos_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/produtos/moderar", status_code=status.HTTP_303_SEE_OTHER)

    anuncio = anuncio_repo.obter_por_id(id)

    if not anuncio:
        informar_erro(request, "Produto não encontrado")
        return RedirectResponse("/admin/produtos/moderar", status_code=status.HTTP_303_SEE_OTHER)

    try:
        # Validar motivo
        dto = ModerarProdutoDTO(
            id=id,
            motivo_reprovacao=motivo_reprovacao
        )

        # Manter produto inativo e registrar motivo no log
        logger.warning(
            f"Produto {id} ({anuncio.nome}) reprovado por admin {usuario_logado['id']}. "
            f"Motivo: {dto.motivo_reprovacao}"
        )

        # TODO: Em versão futura, enviar notificação ao vendedor com o motivo

        informar_sucesso(request, f"Produto '{anuncio.nome}' reprovado.")
        return RedirectResponse("/admin/produtos/moderar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        informar_erro(request, "Motivo de reprovação inválido (mínimo 10 caracteres)")
        return RedirectResponse("/admin/produtos/moderar", status_code=status.HTTP_303_SEE_OTHER)
```

---

### 2.3. Editar Produto (Admin)

#### 2.3.1. Rota GET: Formulário de Edição

**Arquivo**: `routes/admin_produtos_routes.py` (adicionar)

```python
@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário de edição de produto (admin)"""
    anuncio = anuncio_repo.obter_por_id(id)

    if not anuncio:
        informar_erro(request, "Produto não encontrado")
        return RedirectResponse("/admin/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Obter categorias para o select
    categorias = categoria_repo.obter_todos()

    return templates.TemplateResponse(
        "admin/produtos/editar.html",
        {
            "request": request,
            "anuncio": anuncio,
            "categorias": categorias,
            "dados": anuncio.__dict__
        }
    )
```

#### 2.3.2. Template: Edição de Produto

**Arquivo**: `templates/admin/produtos/editar.html`

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Editar Produto{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-10">
        <div class="d-flex align-items-center mb-4">
            <h2 class="mb-0"><i class="bi bi-pencil-square"></i> Editar Produto</h2>
        </div>

        <div class="card shadow-sm">
            <form method="POST" action="/admin/produtos/editar/{{ anuncio.id }}">
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-12">
                            {% include "components/alerta_erro.html" %}
                        </div>

                        <div class="col-md-6 mb-3">
                            {{ field(name='nome', label='Nome do Produto', type='text', required=true,
                                   value=dados.nome if dados else anuncio.nome) }}
                        </div>

                        <div class="col-md-6 mb-3">
                            {% set categorias_dict = {} %}
                            {% for cat in categorias %}
                            {% set _ = categorias_dict.update({cat.id|string: cat.nome}) %}
                            {% endfor %}
                            {{ field(name='id_categoria', label='Categoria', type='select', required=true,
                                   options=categorias_dict,
                                   value=(dados.id_categoria if dados else anuncio.id_categoria)|string) }}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='descricao', label='Descrição', type='textarea', required=true, rows=5,
                                   value=dados.descricao if dados else anuncio.descricao) }}
                        </div>

                        <div class="col-md-4 mb-3">
                            {{ field(name='preco', label='Preço (R$)', type='number', required=true, step='0.01',
                                   value=dados.preco if dados else anuncio.preco) }}
                        </div>

                        <div class="col-md-4 mb-3">
                            {{ field(name='peso', label='Peso (kg)', type='number', required=true, step='0.01',
                                   value=dados.peso if dados else anuncio.peso) }}
                        </div>

                        <div class="col-md-4 mb-3">
                            {{ field(name='estoque', label='Estoque', type='number', required=true,
                                   value=dados.estoque if dados else anuncio.estoque) }}
                        </div>

                        <div class="col-12 mb-3">
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="ativo" name="ativo"
                                       value="true" {{ 'checked' if (dados.ativo if dados else anuncio.ativo) }}>
                                <label class="form-check-label" for="ativo">
                                    Produto Ativo (visível na plataforma)
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card-footer p-4">
                    <div class="d-flex gap-3">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle"></i> Salvar Alterações
                        </button>
                        <a href="/admin/produtos/listar" class="btn btn-secondary">
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

#### 2.3.3. Rota POST: Processar Edição

**Arquivo**: `routes/admin_produtos_routes.py` (adicionar)

```python
@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    id_categoria: int = Form(...),
    nome: str = Form(...),
    descricao: str = Form(...),
    peso: float = Form(...),
    preco: float = Form(...),
    estoque: int = Form(...),
    ativo: Optional[str] = Form(None),
    usuario_logado: Optional[dict] = None
):
    """Edita um produto (admin)"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_produtos_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se anúncio existe
    anuncio_atual = anuncio_repo.obter_por_id(id)
    if not anuncio_atual:
        informar_erro(request, "Produto não encontrado")
        return RedirectResponse("/admin/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Converter checkbox ativo
    ativo_bool = ativo == "true" if ativo else False

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {
        "id": id,
        "id_categoria": id_categoria,
        "nome": nome,
        "descricao": descricao,
        "peso": peso,
        "preco": preco,
        "estoque": estoque,
        "ativo": ativo_bool
    }

    try:
        # Validar com DTO
        dto = AlterarAnuncioDTO(
            id=id,
            id_categoria=id_categoria,
            nome=nome,
            descricao=descricao,
            peso=peso,
            preco=preco,
            estoque=estoque,
            ativo=ativo_bool
        )

        # Atualizar anúncio
        anuncio_atualizado = Anuncio(
            id=id,
            id_vendedor=anuncio_atual.id_vendedor,  # Mantém vendedor original
            id_categoria=dto.id_categoria,
            nome=dto.nome,
            descricao=dto.descricao,
            peso=dto.peso,
            preco=dto.preco,
            estoque=dto.estoque,
            ativo=dto.ativo,
            data_cadastro=anuncio_atual.data_cadastro  # Mantém data original
        )

        anuncio_repo.alterar(anuncio_atualizado)
        logger.info(f"Produto {id} editado por admin {usuario_logado['id']}")

        informar_sucesso(request, "Produto alterado com sucesso!")
        return RedirectResponse("/admin/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Adicionar dados necessários para renderizar o template
        dados_formulario["anuncio"] = anuncio_repo.obter_por_id(id)
        dados_formulario["categorias"] = categoria_repo.obter_todos()
        raise FormValidationError(
            validation_error=e,
            template_path="admin/produtos/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome",
        )
```

---

### 2.4. Excluir Produto

#### 2.4.1. Rota POST: Excluir

**Arquivo**: `routes/admin_produtos_routes.py` (adicionar)

```python
@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exclui um produto"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_produtos_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)

    anuncio = anuncio_repo.obter_por_id(id)

    if not anuncio:
        informar_erro(request, "Produto não encontrado")
        return RedirectResponse("/admin/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)

    try:
        anuncio_repo.excluir(id)
        logger.info(f"Produto {id} ({anuncio.nome}) excluído por admin {usuario_logado['id']}")
        informar_sucesso(request, "Produto excluído com sucesso!")
    except Exception as e:
        # Captura erro de FK constraint (produto com pedidos vinculados)
        logger.error(f"Erro ao excluir produto {id}: {str(e)}")
        informar_erro(request, "Não é possível excluir este produto pois existem pedidos vinculados a ele.")

    return RedirectResponse("/admin/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)
```

---

## 3. REGISTRO DE ROTAS NO MAIN.PY

**Arquivo**: `main.py` (adicionar após as importações e antes de `app.include_router`)

```python
# Rotas Administrativas - Compraê
from routes.admin_categorias_routes import router as admin_categorias_router
from routes.admin_produtos_routes import router as admin_produtos_router

# ... (código existente)

# Incluir rotas administrativas (após rotas de admin backups)
app.include_router(admin_categorias_router, tags=["Admin - Categorias"])
logger.info("Router admin de categorias incluído")

app.include_router(admin_produtos_router, tags=["Admin - Produtos"])
logger.info("Router admin de produtos incluído")
```

---

## 4. ATUALIZAÇÃO DA NAVEGAÇÃO (NAVBAR)

**Arquivo**: `templates/base_privada.html` (atualizar seção de menu admin)

Localizar a seção do menu administrativo e adicionar os novos itens:

```html
{% if request.session.get('usuario_logado')['perfil'] == 'Administrador' %}
<li class="nav-item">
    <a class="nav-link {{ 'active' if '/admin/usuarios/' in request.path else '' }}"
        href="/admin/usuarios/listar">Usuários</a>
</li>
<li class="nav-item">
    <a class="nav-link {{ 'active' if '/admin/categorias/' in request.path else '' }}"
        href="/admin/categorias/listar">Categorias</a>
</li>
<li class="nav-item">
    <a class="nav-link {{ 'active' if '/admin/produtos/' in request.path else '' }}"
        href="/admin/produtos/listar">Produtos</a>
</li>
<!-- ... outros itens admin existentes ... -->
{% endif %}
```

---

## 5. CHECKLIST DE IMPLEMENTAÇÃO

### 5.1. Gerenciamento de Categorias ✅ CONCLUÍDO

- ✅ Criar arquivo `routes/admin_categorias_routes.py`
- ✅ Implementar rota `GET /listar`
- ✅ Criar template `templates/admin/categorias/listar.html`
- ✅ Implementar rota `GET /cadastrar`
- ✅ Criar template `templates/admin/categorias/cadastro.html`
- ✅ Implementar rota `POST /cadastrar`
- ✅ Implementar rota `GET /editar/{id}`
- ✅ Criar template `templates/admin/categorias/editar.html`
- ✅ Implementar rota `POST /editar/{id}`
- ✅ Implementar rota `POST /excluir/{id}`
- ✅ Registrar router no `main.py`
- ✅ Adicionar item na navbar
- ✅ Testar CRUD completo

### 5.2. Gerenciamento/Moderação de Produtos ✅ CONCLUÍDO

- ✅ Criar arquivo `routes/admin_produtos_routes.py`
- ✅ Criar DTO `ModerarProdutoDTO` em `dtos/anuncio_dto.py`
- ✅ Implementar rota `GET /listar`
- ✅ Criar template `templates/admin/produtos/listar.html`
- ✅ Implementar rota `GET /moderar`
- ✅ Criar template `templates/admin/produtos/moderar.html`
- ✅ Implementar rota `POST /aprovar/{id}`
- ✅ Implementar rota `POST /reprovar/{id}`
- ✅ Implementar rota `GET /editar/{id}`
- ✅ Criar template `templates/admin/produtos/editar.html`
- ✅ Implementar rota `POST /editar/{id}`
- ✅ Implementar rota `POST /excluir/{id}`
- ✅ Registrar router no `main.py`
- ✅ Adicionar item na navbar
- ✅ Testar moderação e CRUD completo

---

## 6. TESTES RECOMENDADOS

Para cada funcionalidade implementada, realizar os seguintes testes:

1. **Testes de Autenticação**:
   - Acesso sem login (deve redirecionar)
   - Acesso como Cliente (deve bloquear)
   - Acesso como Administrador (deve permitir)

2. **Testes de Validação**:
   - Campos obrigatórios vazios
   - Valores inválidos (strings muito longas, números negativos)
   - Validações específicas de cada campo

3. **Testes de CRUD**:
   - Criar registro válido
   - Listar registros
   - Editar registro existente
   - Tentar editar registro inexistente
   - Excluir registro sem dependências
   - Tentar excluir registro com dependências (FK constraint)

4. **Testes de Rate Limiting**:
   - Realizar múltiplas operações rapidamente
   - Verificar se bloqueio é aplicado

5. **Testes de Moderação** (específico para produtos):
   - Aprovar produto
   - Reprovar produto com motivo válido
   - Reprovar produto com motivo inválido

---

## 7. OBSERVAÇÕES FINAIS

### 7.1. Padrões de Qualidade

- **Logging**: Todas as operações críticas devem ser registradas com `logger.info()`, `logger.warning()` ou `logger.error()`
- **Flash Messages**: Sempre informar o usuário sobre sucesso ou erro das operações
- **Validação**: Usar DTOs Pydantic para todas as validações de entrada
- **Segurança**: Rate limiting em todas as operações de escrita
- **Confirmação**: Modal de confirmação para todas as exclusões
- **Acessibilidade**: Usar atributos `aria-label` em botões e links

### 7.2. Próximas Fases

A FASE 2 abrange **exclusivamente** as rotas administrativas. Funcionalidades para outros perfis (Cliente, Vendedor) e rotas públicas serão contempladas em fases posteriores.

### 7.3. Manutenção

- Sempre manter consistência com os padrões do DefaultWebApp
- Documentar mudanças significativas
- Atualizar este documento conforme necessário
- Manter versionamento de código com Git

---

## 📌 ESCOPO DA FASE 2

**O que FOI implementado:**
- ✅ Gerenciamento de Categorias (Admin)
- ✅ Gerenciamento/Moderação de Produtos (Admin)
- ✅ 18 rotas administrativas
- ✅ 6 templates HTML
- ✅ 1 novo DTO (ModerarProdutoDTO)
- ✅ Integração completa (main.py + navbar)
- ✅ 302 testes passando

**O que NÃO faz parte da FASE 2:**
- Rotas públicas (catálogo, busca de produtos)
- Rotas de Cliente (realizar pedidos, histórico)
- Rotas de Vendedor (gerenciar anúncios próprios)
- Sistema de carrinho de compras (não será implementado em nenhuma fase)

---

**Fim do Documento FASE 2**
