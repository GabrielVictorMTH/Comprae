# Atividade Final - Projeto Comprae

Este documento contém 4 atividades independentes para os alunos. Cada atividade deve ser realizada individualmente e representa um aprimoramento do sistema Comprae.

**Tempo estimado por atividade:** 60 minutos
**Nivel:** Facil
**Requisito:** Ter o projeto funcionando localmente

---

## Atividade 1 - Aluno 1: Adicionar Contador de Visualizacoes nos Anuncios

**Objetivo:** Adicionar um campo que conta quantas vezes um anuncio foi visualizado e exibir esse contador na pagina de detalhes do anuncio.

### Passo 1: Criar a branch de trabalho

Abra o terminal na pasta do projeto e execute:

```bash
git checkout -b aluno1
```

### Passo 2: Alterar o arquivo de SQL do anuncio

Abra o arquivo `sql/anuncio_sql.py` e adicione a seguinte query no final do arquivo (antes da ultima linha):

```python
INCREMENTAR_VISUALIZACOES = """
UPDATE anuncio
SET visualizacoes = visualizacoes + 1
WHERE id = ?
"""
```

### Passo 3: Alterar a criacao da tabela

No mesmo arquivo `sql/anuncio_sql.py`, localize a constante `CRIAR_TABELA` e adicione o campo `visualizacoes` na definicao da tabela. Substitua a linha:

```python
    ativo BOOLEAN DEFAULT 1,
```

Por:

```python
    ativo BOOLEAN DEFAULT 1,
    visualizacoes INTEGER DEFAULT 0,
```

### Passo 4: Alterar o modelo do anuncio

Abra o arquivo `model/anuncio_model.py` e adicione o campo `visualizacoes` na classe. Localize a linha:

```python
    ativo: bool
```

E adicione logo abaixo dela:

```python
    visualizacoes: int = 0
```

O arquivo ficara assim:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from model.usuario_model import Usuario

if TYPE_CHECKING:
    from model.categoria_model import Categoria


@dataclass
class Anuncio:
    id: int
    id_vendedor: int
    id_categoria: int
    nome: str
    descricao: str
    peso: float
    preco: float
    estoque: int
    data_cadastro: datetime
    ativo: bool
    visualizacoes: int = 0
    # Relacionamentos
    vendedor: Optional[Usuario] = None
    categoria: Optional["Categoria"] = None
```

### Passo 5: Adicionar funcao no repositorio

Abra o arquivo `repo/anuncio_repo.py` e adicione a seguinte funcao no final do arquivo:

```python
def incrementar_visualizacoes(id: int) -> bool:
    """Incrementa o contador de visualizacoes de um anuncio"""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(anuncio_sql.INCREMENTAR_VISUALIZACOES, (id,))
        return cursor.rowcount > 0
```

Tambem adicione o import no topo do arquivo (se ainda nao existir):

```python
from sql import anuncio_sql
```

### Passo 6: Chamar a funcao ao visualizar o anuncio

Abra o arquivo `routes/anuncios_publicos_routes.py` e localize a funcao `detalhes_anuncio`. Adicione a chamada para incrementar visualizacoes apos buscar o anuncio.

Localize este trecho:

```python
    # Buscar anuncio com detalhes
    anuncio = anuncio_repo.obter_por_id_com_detalhes(id)

    if not anuncio:
```

E altere para:

```python
    # Buscar anuncio com detalhes
    anuncio = anuncio_repo.obter_por_id_com_detalhes(id)

    if not anuncio:
```

Logo apos a verificacao `if not anuncio:` e seu bloco, adicione antes de `# Verificar se anuncio esta ativo`:

```python
    # Incrementar contador de visualizacoes
    anuncio_repo.incrementar_visualizacoes(id)
```

### Passo 7: Exibir o contador na pagina de detalhes

Abra o arquivo `templates/anuncios/detalhes.html` e localize onde sao exibidas as informacoes do anuncio. Adicione o seguinte codigo HTML onde desejar mostrar as visualizacoes (sugestao: proximo ao estoque):

```html
<p class="text-muted">
    <i class="bi bi-eye me-1"></i>
    {{ anuncio.visualizacoes }} visualizacao{% if anuncio.visualizacoes != 1 %}es{% endif %}
</p>
```

### Passo 8: Atualizar o banco de dados

Como adicionamos uma nova coluna, precisamos atualizar o banco. Abra o terminal e execute:

```bash
rm dados.db
python main.py
```

Isso ira recriar o banco de dados com a nova estrutura.

### Passo 9: Testar a funcionalidade

1. Acesse a aplicacao no navegador
2. Va ate a listagem de anuncios
3. Clique em um anuncio para ver os detalhes
4. Atualize a pagina e veja o contador aumentar

### Passo 10: Fazer o commit

```bash
git add .
git commit -m "Adicionar contador de visualizacoes nos anuncios"
```

---

## Atividade 2 - Aluno 2: Adicionar Campo "Sobre Mim" no Perfil do Usuario

**Objetivo:** Permitir que o usuario adicione uma descricao pessoal ("bio") no seu perfil.

### Passo 1: Criar a branch de trabalho

Abra o terminal na pasta do projeto e execute:

```bash
git checkout -b aluno2
```

### Passo 2: Alterar o arquivo de SQL do usuario

Abra o arquivo `sql/usuario_sql.py` e localize a constante `CRIAR_TABELA`. Adicione o campo `sobre_mim` na definicao da tabela. Localize a linha:

```python
    data_atualizacao TIMESTAMP
```

E altere para:

```python
    sobre_mim TEXT,
    data_atualizacao TIMESTAMP
```

### Passo 3: Alterar a query de alteracao

No mesmo arquivo `sql/usuario_sql.py`, localize a constante `ALTERAR` e modifique para incluir o campo `sobre_mim`:

```python
ALTERAR = """
UPDATE usuario
SET nome = ?, email = ?, perfil = ?, genero = ?, data_nascimento = ?, sobre_mim = ?, data_atualizacao = CURRENT_TIMESTAMP
WHERE id = ?
"""
```

### Passo 4: Alterar o modelo do usuario

Abra o arquivo `model/usuario_model.py` e adicione o campo `sobre_mim`. Localize a linha:

```python
    data_nascimento: Optional[datetime] = None
```

E adicione logo abaixo:

```python
    sobre_mim: Optional[str] = None
```

O arquivo completo ficara assim:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    senha: str
    perfil: str
    genero: Optional[str] = None
    data_nascimento: Optional[datetime] = None
    sobre_mim: Optional[str] = None
    token_redefinicao: Optional[str] = None
    data_token: Optional[datetime] = None
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
```

### Passo 5: Atualizar o repositorio do usuario

Abra o arquivo `repo/usuario_repo.py` e localize a funcao `_row_to_usuario`. Adicione o campo `sobre_mim` na conversao. Modifique a funcao para:

```python
def _row_to_usuario(row: sqlite3.Row) -> Usuario:
    """
    Converte uma linha do banco de dados em objeto Usuario.
    """
    return Usuario(
        id=row["id"],
        nome=row["nome"],
        email=row["email"],
        senha=row["senha"],
        perfil=row["perfil"],
        genero=row["genero"] if "genero" in row.keys() else None,
        data_nascimento=row["data_nascimento"] if "data_nascimento" in row.keys() else None,
        sobre_mim=row["sobre_mim"] if "sobre_mim" in row.keys() else None,
        token_redefinicao=row["token_redefinicao"] if "token_redefinicao" in row.keys() else None,
        data_token=row["data_token"] if "data_token" in row.keys() else None,
        data_cadastro=row["data_cadastro"] if "data_cadastro" in row.keys() else None,
        data_atualizacao=row["data_atualizacao"] if "data_atualizacao" in row.keys() else None
    )
```

Tambem modifique a funcao `alterar` para incluir o novo campo:

```python
def alterar(usuario: Usuario) -> bool:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ALTERAR, (
            usuario.nome,
            usuario.email,
            usuario.perfil,
            usuario.genero,
            usuario.data_nascimento,
            usuario.sobre_mim,
            usuario.id
        ))
        return cursor.rowcount > 0
```

### Passo 6: Adicionar campo no formulario de edicao

Abra o arquivo `templates/perfil/editar.html` e adicione o campo "Sobre Mim" no formulario. Localize o trecho:

```html
                        <div class="col-12">
                            {{ field(name='perfil', label='Perfil de Acesso', type='text',
                            value=dados.perfil, disabled=true, wrapper_class='mb-0') }}
                        </div>
```

E adicione ANTES dele:

```html
                        <div class="col-12 mb-3">
                            <label for="sobre_mim" class="form-label">Sobre Mim</label>
                            <textarea class="form-control" id="sobre_mim" name="sobre_mim"
                                rows="3" maxlength="500"
                                placeholder="Conte um pouco sobre voce...">{{ dados.sobre_mim or '' }}</textarea>
                            <div class="form-text">Maximo de 500 caracteres</div>
                        </div>
```

### Passo 7: Processar o campo no backend

Abra o arquivo `routes/usuario_routes.py` e localize a funcao `post_editar_perfil`. Adicione o parametro `sobre_mim` na assinatura da funcao:

Localize:

```python
async def post_editar_perfil(
    request: Request,
    nome: str = Form(),
    email: str = Form(),
    usuario_logado: Optional[UsuarioLogado] = None,
):
```

E altere para:

```python
async def post_editar_perfil(
    request: Request,
    nome: str = Form(),
    email: str = Form(),
    sobre_mim: str = Form(default=""),
    usuario_logado: Optional[UsuarioLogado] = None,
):
```

Ainda na mesma funcao, localize:

```python
        # Atualizar dados
        usuario.nome = dto.nome
        usuario.email = dto.email
```

E adicione logo abaixo:

```python
        usuario.sobre_mim = sobre_mim[:500] if sobre_mim else None
```

Tambem atualize o dicionario `dados_formulario`:

```python
    dados_formulario: dict = {"nome": nome, "email": email, "sobre_mim": sobre_mim}
```

### Passo 8: Exibir o "Sobre Mim" na visualizacao do perfil

Abra o arquivo `templates/perfil/visualizar.html` e adicione a exibicao do campo. Localize o trecho:

```html
                {% if usuario.data_cadastro %}
                <p class="text-muted small">
                    <i class="bi bi-calendar-event" style="color: #7C3AED;"></i>Membro desde {{ usuario.data_cadastro|data_br }}
                </p>
                {% endif %}
```

E adicione ANTES dele:

```html
                {% if usuario.sobre_mim %}
                <div class="mt-3 p-3 rounded" style="background: rgba(124, 58, 237, 0.05);">
                    <p class="mb-0 fst-italic text-muted">
                        <i class="bi bi-quote me-1"></i>{{ usuario.sobre_mim }}
                    </p>
                </div>
                {% endif %}
```

### Passo 9: Atualizar o banco de dados

```bash
rm dados.db
python main.py
```

### Passo 10: Testar a funcionalidade

1. Faca login na aplicacao
2. Acesse seu perfil
3. Clique em "Editar Dados"
4. Preencha o campo "Sobre Mim"
5. Salve e verifique se aparece na visualizacao do perfil

### Passo 11: Fazer o commit

```bash
git add .
git commit -m "Adicionar campo Sobre Mim no perfil do usuario"
```

---

## Atividade 3 - Aluno 3: Criar Pagina "Meus Favoritos"

**Objetivo:** Criar uma pagina que lista todos os anuncios que o usuario curtiu (favoritou).

### Passo 1: Criar a branch de trabalho

```bash
git checkout -b aluno3
```

### Passo 2: Adicionar query para buscar curtidas do usuario

Abra o arquivo `sql/curtida_sql.py` e adicione no final:

```python
OBTER_POR_USUARIO = """
SELECT c.*, a.nome as nome_anuncio, a.preco, a.descricao, a.estoque,
       cat.nome as nome_categoria
FROM curtida c
INNER JOIN anuncio a ON c.id_anuncio = a.id
LEFT JOIN categoria cat ON a.id_categoria = cat.id
WHERE c.id_usuario = ? AND a.ativo = 1
ORDER BY c.data_curtida DESC
"""

CONTAR_POR_USUARIO = """
SELECT COUNT(*) as quantidade
FROM curtida
WHERE id_usuario = ?
"""
```

### Passo 3: Adicionar funcao no repositorio de curtidas

Abra o arquivo `repo/curtida_repo.py` e adicione as seguintes funcoes no final:

```python
def obter_por_usuario(id_usuario: int) -> list[dict]:
    """Retorna todos os anuncios curtidos por um usuario"""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_USUARIO, (id_usuario,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def contar_por_usuario(id_usuario: int) -> int:
    """Conta quantos anuncios um usuario curtiu"""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_POR_USUARIO, (id_usuario,))
        return cursor.fetchone()["quantidade"]
```

Tambem adicione os imports no topo do arquivo:

```python
from sql.curtida_sql import (
    CRIAR_TABELA, INSERIR, EXCLUIR, OBTER_POR_ID,
    OBTER_QUANTIDADE_POR_ANUNCIO, OBTER_TODOS,
    OBTER_POR_USUARIO, CONTAR_POR_USUARIO
)
```

### Passo 4: Criar o arquivo de rotas para favoritos

Crie um novo arquivo `routes/favoritos_routes.py` com o seguinte conteudo:

```python
"""
Rotas para pagina de favoritos do usuario
"""

from typing import Optional

from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from model.usuario_logado_model import UsuarioLogado
from repo import curtida_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates

router = APIRouter(prefix="/favoritos", tags=["Favoritos"])
templates = criar_templates()


@router.get("")
@requer_autenticacao()
async def listar_favoritos(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None
):
    """Lista todos os anuncios curtidos pelo usuario"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Buscar anuncios curtidos
    favoritos = curtida_repo.obter_por_usuario(usuario_logado.id)
    total = curtida_repo.contar_por_usuario(usuario_logado.id)

    return templates.TemplateResponse(
        "favoritos/listar.html",
        {
            "request": request,
            "favoritos": favoritos,
            "total": total,
            "usuario_logado": usuario_logado,
        },
    )
```

### Passo 5: Criar o template da pagina de favoritos

Crie a pasta `templates/favoritos` e dentro dela crie o arquivo `listar.html`:

```bash
mkdir -p templates/favoritos
```

Crie o arquivo `templates/favoritos/listar.html` com o seguinte conteudo:

```html
{% extends "base_privada.html" %}

{% block titulo %}Meus Favoritos{% endblock %}

{% block content %}
<div class="container py-4">
    <!-- Cabecalho -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h2 class="mb-1">
                <i class="bi bi-heart-fill text-danger me-2"></i>
                Meus Favoritos
            </h2>
            <p class="text-muted mb-0">
                Voce tem {{ total }} anuncio{% if total != 1 %}s{% endif %} favoritado{% if total != 1 %}s{% endif %}
            </p>
        </div>
        <a href="/anuncios" class="btn btn-outline-primary">
            <i class="bi bi-search me-1"></i>Explorar anuncios
        </a>
    </div>

    {% if favoritos %}
    <!-- Grid de Favoritos -->
    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
        {% for fav in favoritos %}
        <div class="col">
            <div class="card h-100 shadow-sm">
                <a href="/anuncios/{{ fav.id_anuncio }}">
                    <img src="{{ fav.id_anuncio|foto_anuncio }}"
                         class="card-img-top"
                         alt="{{ fav.nome_anuncio }}"
                         style="height: 180px; object-fit: cover;">
                </a>
                <div class="card-body">
                    <h5 class="card-title">
                        <a href="/anuncios/{{ fav.id_anuncio }}" class="text-decoration-none text-dark">
                            {{ fav.nome_anuncio }}
                        </a>
                    </h5>
                    <p class="card-text text-muted small">
                        {{ fav.descricao[:80] }}{% if fav.descricao|length > 80 %}...{% endif %}
                    </p>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="fw-bold text-primary fs-5">
                            R$ {{ "%.2f"|format(fav.preco)|replace('.', ',') }}
                        </span>
                        <span class="badge bg-secondary">{{ fav.nome_categoria or 'Geral' }}</span>
                    </div>
                </div>
                <div class="card-footer bg-transparent">
                    <small class="text-muted">
                        <i class="bi bi-heart-fill text-danger me-1"></i>
                        Favoritado em {{ fav.data_curtida|data_br }}
                    </small>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>

    {% else %}
    <!-- Estado vazio -->
    <div class="text-center py-5">
        <div class="mb-4">
            <i class="bi bi-heart display-1 text-muted"></i>
        </div>
        <h4 class="text-muted">Nenhum favorito ainda</h4>
        <p class="text-muted">Explore os anuncios e clique no coracao para adicionar aos favoritos!</p>
        <a href="/anuncios" class="btn btn-primary mt-3">
            <i class="bi bi-search me-2"></i>Explorar anuncios
        </a>
    </div>
    {% endif %}
</div>
{% endblock %}
```

### Passo 6: Registrar a rota no main.py

Abra o arquivo `main.py` e adicione o import e registro da rota. Localize onde estao os outros imports de rotas:

```python
from routes import favoritos_routes
```

E adicione no local onde as outras rotas sao registradas:

```python
app.include_router(favoritos_routes.router)
```

### Passo 7: Adicionar link no menu

Abra o arquivo `templates/base_privada.html` e adicione um link para a pagina de favoritos no menu. Localize a secao de navegacao/menu lateral e adicione:

```html
<a href="/favoritos" class="nav-link">
    <i class="bi bi-heart me-2"></i>Meus Favoritos
</a>
```

### Passo 8: Testar a funcionalidade

1. Faca login na aplicacao
2. Acesse a listagem de anuncios
3. Use o botao de curtir em alguns anuncios (se disponivel)
4. Acesse a pagina "Meus Favoritos" pelo menu
5. Verifique se os anuncios curtidos aparecem

### Passo 9: Fazer o commit

```bash
git add .
git commit -m "Criar pagina Meus Favoritos para listar anuncios curtidos"
```

---

## Atividade 4 - Aluno 4: Adicionar Ordenacao na Listagem de Anuncios

**Objetivo:** Permitir que o usuario ordene os anuncios por preco (menor/maior) ou por data (mais recente/mais antigo).

### Passo 1: Criar a branch de trabalho

```bash
git checkout -b aluno4
```

### Passo 2: Modificar a query SQL de listagem

Abra o arquivo `sql/anuncio_sql.py` e substitua a query `OBTER_ATIVOS_PAGINADOS` pela seguinte versao que suporta ordenacao:

```python
OBTER_ATIVOS_PAGINADOS = """
SELECT a.*, c.nome as nome_categoria, u.nome as nome_vendedor
FROM anuncio a
LEFT JOIN categoria c ON a.id_categoria = c.id
LEFT JOIN usuario u ON a.id_vendedor = u.id
WHERE a.ativo = 1 AND a.estoque > 0
  AND (? IS NULL OR a.nome LIKE ? OR a.descricao LIKE ?)
  AND (? IS NULL OR a.id_categoria = ?)
ORDER BY
    CASE WHEN ? = 'preco_asc' THEN a.preco END ASC,
    CASE WHEN ? = 'preco_desc' THEN a.preco END DESC,
    CASE WHEN ? = 'data_asc' THEN a.data_cadastro END ASC,
    CASE WHEN ? = 'data_desc' OR ? IS NULL THEN a.data_cadastro END DESC
LIMIT ? OFFSET ?
"""
```

### Passo 3: Modificar o repositorio de anuncios

Abra o arquivo `repo/anuncio_repo.py` e localize a funcao `obter_ativos_paginados`. Modifique-a para aceitar o parametro de ordenacao:

```python
def obter_ativos_paginados(
    pagina: int = 1,
    por_pagina: int = 12,
    termo: str = None,
    id_categoria: int = None,
    ordenar_por: str = None
) -> tuple[list, int]:
    """
    Retorna anuncios ativos com paginacao, filtros e ordenacao.

    Args:
        ordenar_por: 'preco_asc', 'preco_desc', 'data_asc', 'data_desc'
    """
    offset = (pagina - 1) * por_pagina
    termo_busca = f"%{termo}%" if termo else None

    with obter_conexao() as conn:
        cursor = conn.cursor()

        # Contar total
        cursor.execute(
            anuncio_sql.CONTAR_ATIVOS,
            (termo_busca, termo_busca, termo_busca, id_categoria, id_categoria)
        )
        total = cursor.fetchone()["total"]

        # Buscar anuncios
        cursor.execute(
            anuncio_sql.OBTER_ATIVOS_PAGINADOS,
            (
                termo_busca, termo_busca, termo_busca,
                id_categoria, id_categoria,
                ordenar_por, ordenar_por, ordenar_por, ordenar_por, ordenar_por,
                por_pagina, offset
            )
        )
        rows = cursor.fetchall()
        anuncios = [_row_to_anuncio(row) for row in rows]

        return anuncios, total
```

### Passo 4: Modificar a rota de listagem de anuncios

Abra o arquivo `routes/anuncios_publicos_routes.py` e modifique a funcao `listar_anuncios` para aceitar o parametro de ordenacao:

Localize a assinatura da funcao:

```python
async def listar_anuncios(
    request: Request,
    pagina: int = Query(1, ge=1, description="Numero da pagina"),
    busca: Optional[str] = Query(None, description="Termo de busca"),
    categoria: Optional[int] = Query(None, description="ID da categoria"),
):
```

E altere para:

```python
async def listar_anuncios(
    request: Request,
    pagina: int = Query(1, ge=1, description="Numero da pagina"),
    busca: Optional[str] = Query(None, description="Termo de busca"),
    categoria: Optional[int] = Query(None, description="ID da categoria"),
    ordenar: Optional[str] = Query(None, description="Ordenacao"),
):
```

Modifique a chamada do repositorio:

```python
    # Buscar anuncios com filtros
    anuncios, total = anuncio_repo.obter_ativos_paginados(
        pagina=pagina,
        por_pagina=ANUNCIOS_POR_PAGINA,
        termo=busca,
        id_categoria=categoria,
        ordenar_por=ordenar
    )
```

E adicione `ordenar` ao contexto do template:

```python
    return templates_anuncios.TemplateResponse(
        "anuncios/listar.html",
        {
            "request": request,
            "anuncios": anuncios,
            "categorias": categorias,
            "usuario_logado": usuario_logado,
            # Filtros atuais
            "busca": busca or "",
            "categoria_selecionada": categoria,
            "ordenacao_selecionada": ordenar,
            # Paginacao
            "pagina_atual": pagina,
            "total_paginas": total_paginas,
            "total_anuncios": total,
        },
    )
```

### Passo 5: Adicionar o seletor de ordenacao no template

Abra o arquivo `templates/anuncios/listar.html` e adicione o campo de ordenacao. Localize o formulario de filtros e adicione uma nova coluna para ordenacao.

Localize este trecho:

```html
                    <div class="col-md-4">
                        <label for="categoria" class="form-label fw-semibold">
                            <i class="bi bi-tag me-1 text-primary"></i>Categoria
                        </label>
                        <select class="form-select form-select-lg" id="categoria" name="categoria">
                            <option value="">Todas as categorias</option>
                            {% for cat in categorias %}
                            <option value="{{ cat.id }}" {% if categoria_selecionada == cat.id %}selected{% endif %}>
                                {{ cat.nome }}
                            </option>
                            {% endfor %}
                        </select>
                    </div>
```

E adicione LOGO APOS esse bloco (antes do botao Filtrar):

```html
                    <div class="col-md-3">
                        <label for="ordenar" class="form-label fw-semibold">
                            <i class="bi bi-sort-down me-1 text-primary"></i>Ordenar por
                        </label>
                        <select class="form-select form-select-lg" id="ordenar" name="ordenar">
                            <option value="">Mais recentes</option>
                            <option value="preco_asc" {% if ordenacao_selecionada == 'preco_asc' %}selected{% endif %}>
                                Menor preco
                            </option>
                            <option value="preco_desc" {% if ordenacao_selecionada == 'preco_desc' %}selected{% endif %}>
                                Maior preco
                            </option>
                            <option value="data_asc" {% if ordenacao_selecionada == 'data_asc' %}selected{% endif %}>
                                Mais antigos
                            </option>
                            <option value="data_desc" {% if ordenacao_selecionada == 'data_desc' %}selected{% endif %}>
                                Mais recentes
                            </option>
                        </select>
                    </div>
```

Ajuste as colunas para acomodar o novo campo. Altere:
- `col-md-5` para `col-md-4` no campo de busca
- `col-md-4` para `col-md-3` no campo de categoria
- `col-md-3` para `col-md-2` no botao Filtrar

### Passo 6: Manter a ordenacao na paginacao

Ainda no arquivo `templates/anuncios/listar.html`, atualize os links de paginacao para manter a ordenacao. Localize todos os links de paginacao e adicione o parametro `ordenar`. Por exemplo:

Onde estiver:
```html
href="/anuncios?pagina={{ pagina_atual - 1 }}{% if busca %}&busca={{ busca }}{% endif %}{% if categoria_selecionada %}&categoria={{ categoria_selecionada }}{% endif %}"
```

Adicione no final:
```html
{% if ordenacao_selecionada %}&ordenar={{ ordenacao_selecionada }}{% endif %}
```

Faca isso para TODOS os links de paginacao no arquivo (aproximadamente 5 lugares).

### Passo 7: Remover o campo ordenar quando vazio

No bloco de script no final do arquivo, adicione a logica para remover o campo ordenar quando vazio:

Localize:
```javascript
document.querySelector('form[action="/anuncios"]').addEventListener('submit', function(e) {
    const categoria = document.getElementById('categoria');
    if (categoria.value === '') {
        categoria.removeAttribute('name');
    }
});
```

E altere para:

```javascript
document.querySelector('form[action="/anuncios"]').addEventListener('submit', function(e) {
    const categoria = document.getElementById('categoria');
    if (categoria.value === '') {
        categoria.removeAttribute('name');
    }
    const ordenar = document.getElementById('ordenar');
    if (ordenar.value === '') {
        ordenar.removeAttribute('name');
    }
});
```

### Passo 8: Testar a funcionalidade

1. Acesse a listagem de anuncios
2. Selecione diferentes opcoes de ordenacao
3. Clique em "Filtrar"
4. Verifique se os anuncios aparecem na ordem correta
5. Teste a navegacao entre paginas e verifique se a ordenacao e mantida

### Passo 9: Fazer o commit

```bash
git add .
git commit -m "Adicionar ordenacao por preco e data na listagem de anuncios"
```

---

## Resumo das Atividades

| Aluno | Atividade | Branch |
|-------|-----------|--------|
| Aluno 1 | Contador de Visualizacoes | aluno1 |
| Aluno 2 | Campo "Sobre Mim" no Perfil | aluno2 |
| Aluno 3 | Pagina "Meus Favoritos" | aluno3 |
| Aluno 4 | Ordenacao na Listagem | aluno4 |

**Importante:** Cada aluno deve trabalhar em sua propria branch para evitar conflitos. As atividades sao independentes e podem ser realizadas simultaneamente.
