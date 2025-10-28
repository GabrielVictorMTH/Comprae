# Tutorial: Implementando um CRUD Completo no SimpleBlog

## Índice

1. [Introdução](#introdução)
2. [Arquitetura do SimpleBlog](#arquitetura-do-simpleblog)
3. [Visão Geral do que Vamos Construir](#visão-geral-do-que-vamos-construir)
4. [Passo 1: Criar as Queries SQL](#passo-1-criar-as-queries-sql)
5. [Passo 2: Criar o Modelo de Domínio](#passo-2-criar-o-modelo-de-domínio)
6. [Passo 3: Criar os DTOs de Validação](#passo-3-criar-os-dtos-de-validação)
7. [Passo 4: Criar o Repository](#passo-4-criar-o-repository)
8. [Passo 5: Registrar o Repository no Main](#passo-5-registrar-o-repository-no-main)
9. [Passo 6: Criar as Routes (Controllers)](#passo-6-criar-as-routes-controllers)
10. [Passo 7: Registrar as Routes no Main](#passo-7-registrar-as-routes-no-main)
11. [Passo 8: Criar o Template de Listagem](#passo-8-criar-o-template-de-listagem)
12. [Passo 9: Criar o Template de Cadastro](#passo-9-criar-o-template-de-cadastro)
13. [Passo 10: Criar o Template de Edição](#passo-10-criar-o-template-de-edição)
14. [Passo 11: Adicionar Link no Menu](#passo-11-adicionar-link-no-menu)
15. [Passo 12: Testar o CRUD Completo](#passo-12-testar-o-crud-completo)
16. [Padrões e Boas Práticas](#padrões-e-boas-práticas)
17. [Troubleshooting](#troubleshooting)
18. [Exercícios Propostos](#exercícios-propostos)

---

## Introdução

### O que é CRUD?

**CRUD** é um acrônimo para as quatro operações básicas que podemos fazer com dados:

- **C**reate (Criar): Adicionar novos registros
- **R**ead (Ler): Visualizar registros existentes
- **U**pdate (Atualizar): Modificar registros existentes
- **D**elete (Excluir): Remover registros

Praticamente todo sistema precisa de CRUDs para gerenciar suas informações. Por exemplo:
- Um e-commerce tem CRUD de produtos, clientes, pedidos
- Uma rede social tem CRUD de usuários, posts, comentários
- Um blog tem CRUD de artigos, categorias, autores

### Por que Separar em Camadas?

Imagine construir uma casa:
- Você não mistura a fundação com o telhado
- Cada parte tem sua função específica
- Se precisar consertar o telhado, não mexe na fundação

Da mesma forma, em programação separamos o código em **camadas** para:

✅ **Organização**: Cada arquivo tem uma responsabilidade clara
✅ **Manutenção**: Facilita encontrar e corrigir bugs
✅ **Reutilização**: Podemos usar a mesma lógica em diferentes lugares
✅ **Trabalho em equipe**: Várias pessoas podem trabalhar em camadas diferentes
✅ **Testabilidade**: Podemos testar cada parte isoladamente

---

## Arquitetura do SimpleBlog

O SimpleBlog utiliza uma **arquitetura em 7 camadas**. Vamos entender cada uma:

```
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 1: ROUTES (Controladores)                          │
│  Arquivo: routes/admin_categorias_routes.py                 │
│                                                              │
│  Responsabilidade:                                          │
│  • Receber requisições HTTP (GET, POST)                    │
│  • Validar dados usando DTOs                               │
│  • Chamar o Repository para acessar dados                  │
│  • Retornar templates HTML ou fazer redirects              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 2: DTOs (Data Transfer Objects)                    │
│  Arquivo: dtos/categoria_dto.py                            │
│                                                              │
│  Responsabilidade:                                          │
│  • Validar dados vindos de formulários                     │
│  • Garantir que os dados estão no formato correto          │
│  • Aplicar regras de negócio (tamanho mín/máx, etc)       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 3: MODEL (Modelo de Domínio)                       │
│  Arquivo: model/categoria_model.py                         │
│                                                              │
│  Responsabilidade:                                          │
│  • Representar uma Categoria como objeto Python            │
│  • Definir quais campos uma Categoria possui               │
│  • Facilitar o transporte de dados entre camadas           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 4: REPOSITORY (Acesso a Dados)                     │
│  Arquivo: repo/categoria_repo.py                           │
│                                                              │
│  Responsabilidade:                                          │
│  • Executar operações no banco de dados                    │
│  • Criar, ler, atualizar, excluir registros                │
│  • Converter linhas do BD em objetos Model                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 5: SQL (Consultas)                                 │
│  Arquivo: sql/categoria_sql.py                             │
│                                                              │
│  Responsabilidade:                                          │
│  • Armazenar queries SQL como constantes                   │
│  • Facilitar revisão e manutenção das queries              │
│  • Prevenir SQL Injection usando placeholders (?)          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 6: DATABASE UTILITY (Utilidades do BD)             │
│  Arquivo: util/db_util.py                                  │
│                                                              │
│  Responsabilidade:                                          │
│  • Gerenciar conexões com o banco de dados                 │
│  • Fazer commit/rollback automático                        │
│  • Garantir que conexões sejam fechadas corretamente       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 7: DATABASE (Banco de Dados)                       │
│  Arquivo: dados.db (SQLite)                                │
│                                                              │
│  Responsabilidade:                                          │
│  • Armazenar dados persistentemente                        │
│  • Garantir integridade dos dados                          │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de uma Requisição

Quando um usuário clica em "Criar Categoria":

1. **Route** recebe a requisição HTTP POST
2. **DTO** valida os dados do formulário
3. **Route** cria um objeto **Model** com os dados validados
4. **Route** chama o **Repository** para salvar
5. **Repository** executa a query **SQL**
6. **DB Utility** gerencia a conexão
7. **Database** armazena o registro
8. **Route** redireciona para a página de listagem

---

## Visão Geral do que Vamos Construir

Vamos criar um **CRUD de Categorias** para o SimpleBlog. Ao final, teremos:

### Funcionalidades

✅ **Listar todas as categorias** em uma tabela
✅ **Cadastrar nova categoria** com nome e descrição
✅ **Editar categoria existente** alterando seus dados
✅ **Excluir categoria** com confirmação

### Estrutura do Banco de Dados

```sql
Tabela: categoria
- id (inteiro, chave primária, auto-incremento)
- nome (texto, único, obrigatório, 3-50 caracteres)
- descricao (texto, opcional, máx 200 caracteres)
- data_cadastro (timestamp, preenchido automaticamente)
- data_atualizacao (timestamp, atualizado ao modificar)
```

### Arquivos que Vamos Criar

```
SimpleBlog/
├── sql/
│   └── categoria_sql.py          # Passo 1 (28 linhas)
├── model/
│   └── categoria_model.py        # Passo 2 (12 linhas)
├── dtos/
│   └── categoria_dto.py          # Passo 3 (36 linhas)
├── repo/
│   └── categoria_repo.py         # Passo 4 (135 linhas)
├── routes/
│   └── admin_categorias_routes.py # Passo 6 (246 linhas)
└── templates/admin/categorias/
    ├── listar.html               # Passo 8 (109 linhas)
    ├── cadastro.html             # Passo 9 (53 linhas)
    └── editar.html               # Passo 10 (53 linhas)
```

### Arquivos que Vamos Modificar

```
SimpleBlog/
├── main.py                       # Passos 5 e 7 (+9 linhas)
└── templates/
    └── base_privada.html         # Passo 11 (+4 linhas)
```

**Total**: 685 linhas de código em 10 arquivos

---

## Passo 1: Criar as Queries SQL

### Objetivo

Criar um arquivo com todas as queries SQL necessárias para o CRUD de categorias.

### Por que fazer isso primeiro?

- É a camada mais básica (apenas strings)
- Não depende de nenhum outro arquivo
- Podemos revisar o SQL antes de implementar a lógica

### Arquivo a Criar

📁 `sql/categoria_sql.py`

### Código Completo

```python
# Queries SQL para operações com categorias

# Cria a tabela categoria se ela não existir
CRIAR_TABELA = """
    CREATE TABLE IF NOT EXISTS categoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        descricao TEXT,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_atualizacao TIMESTAMP
    )
"""

# Insere uma nova categoria
INSERIR = """
    INSERT INTO categoria (nome, descricao)
    VALUES (?, ?)
"""

# Atualiza uma categoria existente
ALTERAR = """
    UPDATE categoria
    SET nome=?, descricao=?, data_atualizacao=CURRENT_TIMESTAMP
    WHERE id=?
"""

# Exclui uma categoria
EXCLUIR = """
    DELETE FROM categoria WHERE id=?
"""

# Busca todas as categorias ordenadas por nome
OBTER_TODOS = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM categoria
    ORDER BY nome
"""

# Busca uma categoria por ID
OBTER_POR_ID = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM categoria
    WHERE id=?
"""

# Busca uma categoria por nome
OBTER_POR_NOME = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM categoria
    WHERE nome=?
"""
```

### Explicação Detalhada

#### CREATE TABLE

```sql
CREATE TABLE IF NOT EXISTS categoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL,
    descricao TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP
)
```

- `IF NOT EXISTS`: Cria apenas se a tabela não existir (evita erro)
- `id INTEGER PRIMARY KEY AUTOINCREMENT`:
  - Chave primária que incrementa automaticamente (1, 2, 3...)
- `nome TEXT UNIQUE NOT NULL`:
  - `UNIQUE`: Não permite nomes duplicados
  - `NOT NULL`: Campo obrigatório
- `descricao TEXT`: Campo opcional (pode ser vazio)
- `data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP`:
  - Preenche automaticamente com a data/hora atual
- `data_atualizacao TIMESTAMP`: Preencheremos manualmente ao atualizar

#### INSERT

```sql
INSERT INTO categoria (nome, descricao)
VALUES (?, ?)
```

- Os `?` são **placeholders** (espaços reservados)
- Na hora de executar, substituímos pelos valores reais
- **Isso previne SQL Injection!** ⚠️

Exemplo de uso seguro:
```python
cursor.execute(INSERIR, ("Tecnologia", "Artigos sobre tecnologia"))
```

Exemplo INSEGURO (nunca faça!):
```python
# ❌ VULNERÁVEL A SQL INJECTION
cursor.execute(f"INSERT INTO categoria VALUES ('{nome}')")
```

#### UPDATE

```sql
UPDATE categoria
SET nome=?, descricao=?, data_atualizacao=CURRENT_TIMESTAMP
WHERE id=?
```

- Atualiza nome e descrição
- Preenche automaticamente `data_atualizacao` com hora atual
- `WHERE id=?`: Garante que atualizamos apenas o registro correto

#### DELETE

```sql
DELETE FROM categoria WHERE id=?
```

- Remove apenas o registro com o ID especificado
- **Cuidado**: Não tem "desfazer"!

#### SELECT

```sql
SELECT id, nome, descricao, data_cadastro, data_atualizacao
FROM categoria
ORDER BY nome
```

- Lista todos os campos que precisamos
- `ORDER BY nome`: Retorna em ordem alfabética

### ✅ Checkpoint

Após criar este arquivo:

1. Verifique se o arquivo está em `sql/categoria_sql.py`
2. Certifique-se de que não há erros de sintaxe
3. Execute o comando para testar importação:

```bash
python -c "from sql.categoria_sql import CRIAR_TABELA; print('OK!')"
```

Se aparecer `OK!`, está tudo certo! 🎉

---

## Passo 2: Criar o Modelo de Domínio

### Objetivo

Criar uma classe Python que representa uma Categoria com todos os seus atributos.

### Por que precisamos disso?

Imagine que você tem uma categoria. Como representá-la no código?

**Opção 1: Usar dicionário** ❌
```python
categoria = {
    "id": 1,
    "nome": "Tecnologia",
    "descricao": "Artigos sobre tecnologia"
}
```
Problema: Sem validação de tipo, fácil errar o nome das chaves

**Opção 2: Usar Model (classe)** ✅
```python
categoria = Categoria(
    id=1,
    nome="Tecnologia",
    descricao="Artigos sobre tecnologia"
)
```
Vantagens:
- O editor autocompleta os campos
- Erros de digitação são detectados
- Podemos adicionar métodos úteis

### Arquivo a Criar

📁 `model/categoria_model.py`

### Código Completo

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Categoria:
    """
    Representa uma categoria do blog.

    Atributos:
        id: Identificador único da categoria
        nome: Nome da categoria (ex: "Tecnologia")
        descricao: Descrição opcional da categoria
        data_cadastro: Data/hora de criação do registro
        data_atualizacao: Data/hora da última atualização
    """
    id: Optional[int] = None
    nome: str = ""
    descricao: str = ""
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
```

### Explicação Detalhada

#### @dataclass

```python
@dataclass
class Categoria:
```

`@dataclass` é um **decorador** que transforma a classe em uma estrutura de dados eficiente.

Sem `@dataclass` teríamos que escrever:
```python
class Categoria:
    def __init__(self, id, nome, descricao, data_cadastro, data_atualizacao):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.data_cadastro = data_cadastro
        self.data_atualizacao = data_atualizacao

    def __repr__(self):
        return f"Categoria(id={self.id}, nome={self.nome}...)"
```

Com `@dataclass`, tudo isso é gerado automaticamente! 🎉

#### Tipos dos Campos

```python
id: Optional[int] = None
```

- `Optional[int]`: Pode ser um número inteiro OU `None`
- `= None`: Valor padrão é `None` (útil ao criar nova categoria sem ID)

```python
nome: str = ""
```

- `str`: Deve ser uma string (texto)
- `= ""`: Valor padrão é string vazia

```python
data_cadastro: Optional[datetime] = None
```

- `datetime`: Objeto de data/hora do Python
- `Optional`: Pode ser `None` (quando ainda não foi salvo no BD)

### Como Usar

```python
# Criar uma nova categoria (antes de salvar no BD)
nova_categoria = Categoria(
    nome="Esportes",
    descricao="Notícias esportivas"
)
print(nova_categoria.id)  # None (ainda não tem ID)

# Categoria vinda do banco de dados
categoria_do_bd = Categoria(
    id=5,
    nome="Tecnologia",
    descricao="Artigos tech",
    data_cadastro=datetime.now()
)
print(categoria_do_bd.nome)  # "Tecnologia"
```

### ✅ Checkpoint

Após criar este arquivo:

1. Verifique se o arquivo está em `model/categoria_model.py`
2. Teste criando uma categoria:

```bash
python -c "
from model.categoria_model import Categoria
c = Categoria(nome='Teste', descricao='Desc teste')
print(f'Categoria criada: {c.nome}')
print('OK!')
"
```

Se aparecer a mensagem, está funcionando! 🎉

---

## Passo 3: Criar os DTOs de Validação

### Objetivo

Criar classes que validam os dados vindos dos formulários antes de processá-los.

### O que é um DTO?

**DTO** significa **Data Transfer Object** (Objeto de Transferência de Dados).

É uma classe que:
- Recebe dados "crus" de um formulário
- Valida se estão corretos
- Se estão errados, gera mensagens de erro claras
- Se estão corretos, permite prosseguir

### Por que precisamos?

Imagine um usuário mal-intencionado tentando:
- Cadastrar categoria com nome vazio
- Nome com 500 caracteres
- Nome com caracteres especiais perigosos

O DTO **protege** nossa aplicação dessas situações! 🛡️

### Arquivo a Criar

📁 `dtos/categoria_dto.py`

### Código Completo

```python
from pydantic import BaseModel, field_validator
from dtos.validators import validar_string_obrigatoria, validar_comprimento

class CriarCategoriaDTO(BaseModel):
    """
    DTO para validar dados ao criar uma nova categoria.

    Regras:
    - nome: obrigatório, entre 3 e 50 caracteres
    - descricao: opcional, máximo 200 caracteres
    """
    nome: str
    descricao: str = ""

    # Validador do campo 'nome'
    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria(
            campo="Nome",
            tamanho_minimo=3,
            tamanho_maximo=50
        )
    )

    # Validador do campo 'descricao'
    _validar_descricao = field_validator("descricao")(
        validar_comprimento(tamanho_maximo=200)
    )

    class Config:
        """Configurações do Pydantic"""
        str_strip_whitespace = True  # Remove espaços extras no início/fim


class AlterarCategoriaDTO(BaseModel):
    """
    DTO para validar dados ao editar uma categoria existente.

    Regras: mesmas do CriarCategoriaDTO
    """
    nome: str
    descricao: str = ""

    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria(
            campo="Nome",
            tamanho_minimo=3,
            tamanho_maximo=50
        )
    )

    _validar_descricao = field_validator("descricao")(
        validar_comprimento(tamanho_maximo=200)
    )

    class Config:
        str_strip_whitespace = True
```

### Explicação Detalhada

#### Pydantic

```python
from pydantic import BaseModel, field_validator
```

**Pydantic** é uma biblioteca Python que faz validação automática de dados.

Vantagens:
- Validação automática de tipos
- Mensagens de erro claras
- Muito usada no FastAPI

#### Campos

```python
class CriarCategoriaDTO(BaseModel):
    nome: str
    descricao: str = ""
```

- `nome: str` → Campo obrigatório do tipo string
- `descricao: str = ""` → Campo opcional com valor padrão vazio

#### Validadores Reutilizáveis

```python
_validar_nome = field_validator("nome")(
    validar_string_obrigatoria(
        campo="Nome",
        tamanho_minimo=3,
        tamanho_maximo=50
    )
)
```

Vamos destrinchar:

1. `field_validator("nome")`: Aplica validação ao campo `nome`
2. `validar_string_obrigatoria(...)`: Função que retorna um validador
3. Parâmetros:
   - `campo="Nome"`: Nome para exibir na mensagem de erro
   - `tamanho_minimo=3`: Mínimo de 3 caracteres
   - `tamanho_maximo=50`: Máximo de 50 caracteres

**Esta função `validar_string_obrigatoria` já existe no projeto!**
Ela está em `dtos/validators.py` e pode ser reutilizada.

#### Configurações

```python
class Config:
    str_strip_whitespace = True
```

`str_strip_whitespace = True` remove espaços extras:
- `"  Tecnologia  "` → `"Tecnologia"`
- Evita erros de usuários que digitam espaços sem querer

### Como Funciona na Prática

#### Exemplo 1: Dados Válidos ✅

```python
from dtos.categoria_dto import CriarCategoriaDTO

# Dados corretos
dados = {
    "nome": "Tecnologia",
    "descricao": "Artigos sobre tecnologia"
}

dto = CriarCategoriaDTO(**dados)
print(dto.nome)  # "Tecnologia"
print(dto.descricao)  # "Artigos sobre tecnologia"
```

#### Exemplo 2: Nome Muito Curto ❌

```python
dados = {
    "nome": "TI",  # Apenas 2 caracteres (mínimo é 3)
    "descricao": "Desc"
}

try:
    dto = CriarCategoriaDTO(**dados)
except ValidationError as e:
    print(e)
    # Erro: Nome deve ter no mínimo 3 caracteres
```

#### Exemplo 3: Nome Muito Longo ❌

```python
dados = {
    "nome": "A" * 100,  # 100 caracteres (máximo é 50)
    "descricao": "Desc"
}

try:
    dto = CriarCategoriaDTO(**dados)
except ValidationError as e:
    print(e)
    # Erro: Nome deve ter no máximo 50 caracteres
```

#### Exemplo 4: Descrição Opcional ✅

```python
# Descrição vazia é permitida
dados = {
    "nome": "Esportes",
    "descricao": ""
}

dto = CriarCategoriaDTO(**dados)
print(dto.descricao)  # ""
```

### Por que Dois DTOs?

```python
class CriarCategoriaDTO(BaseModel):
    # ...

class AlterarCategoriaDTO(BaseModel):
    # ...
```

Neste caso, as validações são iguais, mas em projetos maiores podem ser diferentes:

- **Criar**: Pode exigir senha, email de confirmação
- **Alterar**: Pode permitir mudar apenas alguns campos

É uma boa prática separar para facilitar manutenção futura.

### ✅ Checkpoint

Após criar este arquivo:

1. Verifique se o arquivo está em `dtos/categoria_dto.py`
2. Teste a validação:

```bash
python -c "
from dtos.categoria_dto import CriarCategoriaDTO

# Teste 1: Dados válidos
dto = CriarCategoriaDTO(nome='Tecnologia', descricao='Desc')
print(f'✅ Válido: {dto.nome}')

# Teste 2: Nome muito curto (deve dar erro)
try:
    dto2 = CriarCategoriaDTO(nome='AB', descricao='Desc')
except Exception as e:
    print(f'✅ Erro esperado: nome muito curto')

print('OK!')
"
```

---

## Passo 4: Criar o Repository

### Objetivo

Criar um arquivo com todas as funções que acessam o banco de dados para realizar operações CRUD.

### O que é o Padrão Repository?

**Repository** (Repositório) é um padrão de projeto que:
- Encapsula toda a lógica de acesso ao banco de dados
- Fornece uma interface simples para as outras camadas
- Facilita trocar o banco de dados no futuro

**Analogia**: Pense no repository como um **bibliotecário**:
- Você pede um livro (categoria)
- Ele busca na estante (banco de dados)
- Você não precisa saber onde está guardado

### Arquivo a Criar

📁 `repo/categoria_repo.py`

### Código Completo

```python
from typing import Optional
from model.categoria_model import Categoria
from sql.categoria_sql import *
from util.db_util import get_connection

def criar_tabela():
    """
    Cria a tabela de categorias se ela não existir.
    Deve ser chamada na inicialização do sistema.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(categoria: Categoria) -> Optional[Categoria]:
    """
    Insere uma nova categoria no banco de dados.

    Args:
        categoria: Objeto Categoria com nome e descrição

    Returns:
        Categoria com ID preenchido se sucesso, None se erro

    Exemplo:
        nova = Categoria(nome="Esportes", descricao="Notícias esportivas")
        resultado = inserir(nova)
        if resultado:
            print(f"Categoria criada com ID: {resultado.id}")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(INSERIR, (categoria.nome, categoria.descricao))

            # Pega o ID gerado automaticamente
            if cursor.lastrowid:
                categoria.id = cursor.lastrowid
                return categoria
            return None
    except Exception as e:
        print(f"Erro ao inserir categoria: {e}")
        return None


def alterar(categoria: Categoria) -> bool:
    """
    Atualiza uma categoria existente.

    Args:
        categoria: Objeto Categoria com ID, nome e descrição

    Returns:
        True se atualizou, False se erro

    Exemplo:
        cat = obter_por_id(5)
        cat.nome = "Novo Nome"
        if alterar(cat):
            print("Categoria atualizada!")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                ALTERAR,
                (categoria.nome, categoria.descricao, categoria.id)
            )
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao alterar categoria: {e}")
        return False


def excluir(id: int) -> bool:
    """
    Exclui uma categoria do banco de dados.

    Args:
        id: ID da categoria a ser excluída

    Returns:
        True se excluiu, False se erro ou não encontrou

    Exemplo:
        if excluir(5):
            print("Categoria excluída!")
        else:
            print("Categoria não encontrada")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(EXCLUIR, (id,))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao excluir categoria: {e}")
        return False


def obter_por_id(id: int) -> Optional[Categoria]:
    """
    Busca uma categoria por ID.

    Args:
        id: ID da categoria

    Returns:
        Objeto Categoria se encontrou, None se não encontrou

    Exemplo:
        cat = obter_por_id(5)
        if cat:
            print(f"Encontrada: {cat.nome}")
        else:
            print("Categoria não existe")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_POR_ID, (id,))
            row = cursor.fetchone()

            if row:
                return Categoria(
                    id=row["id"],
                    nome=row["nome"],
                    descricao=row["descricao"],
                    data_cadastro=row["data_cadastro"],
                    data_atualizacao=row["data_atualizacao"]
                )
            return None
    except Exception as e:
        print(f"Erro ao obter categoria por ID: {e}")
        return None


def obter_todos() -> list[Categoria]:
    """
    Retorna todas as categorias do banco de dados.

    Returns:
        Lista de objetos Categoria (pode ser vazia)

    Exemplo:
        categorias = obter_todos()
        for cat in categorias:
            print(f"{cat.id} - {cat.nome}")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_TODOS)
            rows = cursor.fetchall()

            return [
                Categoria(
                    id=row["id"],
                    nome=row["nome"],
                    descricao=row["descricao"],
                    data_cadastro=row["data_cadastro"],
                    data_atualizacao=row["data_atualizacao"]
                )
                for row in rows
            ]
    except Exception as e:
        print(f"Erro ao obter todas as categorias: {e}")
        return []


def obter_por_nome(nome: str) -> Optional[Categoria]:
    """
    Busca uma categoria pelo nome exato.
    Útil para verificar se já existe categoria com aquele nome.

    Args:
        nome: Nome da categoria (case-sensitive)

    Returns:
        Objeto Categoria se encontrou, None se não encontrou

    Exemplo:
        if obter_por_nome("Tecnologia"):
            print("Já existe categoria com este nome")
        else:
            print("Nome disponível")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_POR_NOME, (nome,))
            row = cursor.fetchone()

            if row:
                return Categoria(
                    id=row["id"],
                    nome=row["nome"],
                    descricao=row["descricao"],
                    data_cadastro=row["data_cadastro"],
                    data_atualizacao=row["data_atualizacao"]
                )
            return None
    except Exception as e:
        print(f"Erro ao obter categoria por nome: {e}")
        return None
```

### Explicação Detalhada

#### Context Manager: `with get_connection()`

```python
with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_QUERY, parametros)
```

O `with` garante que:
1. Conexão é aberta
2. Se tudo der certo → `COMMIT` automático (salva)
3. Se der erro → `ROLLBACK` automático (desfaz)
4. Conexão é fechada

**Sem o `with`, teríamos que fazer manualmente**:
```python
conn = sqlite3.connect("dados.db")
try:
    cursor = conn.cursor()
    cursor.execute(...)
    conn.commit()
except:
    conn.rollback()
finally:
    conn.close()
```

Muito mais trabalhoso! O `with` simplifica tudo isso.

#### Função: `criar_tabela()`

```python
def criar_tabela():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
```

- Executa a query `CRIAR_TABELA` (definida no Passo 1)
- Deve ser chamada quando o sistema inicia
- `CREATE TABLE IF NOT EXISTS` garante que não dá erro se já existir

#### Função: `inserir(categoria)`

```python
cursor.execute(INSERIR, (categoria.nome, categoria.descricao))
```

- Executa a query `INSERIR` com os valores da categoria
- `(categoria.nome, categoria.descricao)` → Tupla com valores para os `?`

```python
if cursor.lastrowid:
    categoria.id = cursor.lastrowid
    return categoria
```

- `lastrowid`: Pega o ID gerado pelo `AUTOINCREMENT`
- Preenche o ID no objeto categoria
- Retorna a categoria com ID preenchido

#### Função: `alterar(categoria)`

```python
cursor.execute(ALTERAR, (categoria.nome, categoria.descricao, categoria.id))
return cursor.rowcount > 0
```

- `rowcount`: Número de linhas afetadas
- Se `> 0`, significa que atualizou algum registro
- Se `= 0`, não encontrou registro com aquele ID

#### Função: `excluir(id)`

```python
cursor.execute(EXCLUIR, (id,))
return cursor.rowcount > 0
```

- Nota: `(id,)` → Tupla com 1 elemento (vírgula é obrigatória!)
- Retorna `True` se excluiu, `False` se não encontrou

#### Funções de Busca

```python
row = cursor.fetchone()  # Busca 1 linha
rows = cursor.fetchall()  # Busca todas as linhas
```

- `fetchone()`: Retorna uma linha ou `None`
- `fetchall()`: Retorna lista de linhas (pode ser vazia `[]`)

```python
if row:
    return Categoria(
        id=row["id"],
        nome=row["nome"],
        # ...
    )
```

- `row["id"]`: Acessa coluna por nome (graças ao row_factory)
- Cria objeto `Categoria` com os dados do banco

#### List Comprehension

```python
return [
    Categoria(...)
    for row in rows
]
```

Equivalente a:
```python
categorias = []
for row in rows:
    cat = Categoria(...)
    categorias.append(cat)
return categorias
```

Mais compacto e pythônico! 🐍

### ✅ Checkpoint

Após criar este arquivo:

1. Verifique se o arquivo está em `repo/categoria_repo.py`
2. Teste as funções:

```bash
python -c "
from repo import categoria_repo
from model.categoria_model import Categoria

# Cria tabela
categoria_repo.criar_tabela()
print('✅ Tabela criada')

# Insere categoria
nova = Categoria(nome='Teste', descricao='Descrição teste')
resultado = categoria_repo.inserir(nova)
if resultado and resultado.id:
    print(f'✅ Categoria inserida com ID: {resultado.id}')

    # Lista todas
    todas = categoria_repo.obter_todos()
    print(f'✅ Total de categorias: {len(todas)}')
else:
    print('❌ Erro ao inserir')

print('OK!')
"
```

Se tudo funcionar, avance para o próximo passo! 🎉

---

## Passo 5: Registrar o Repository no Main

### Objetivo

Fazer o sistema reconhecer e inicializar o repository de categorias quando a aplicação iniciar.

### Por que fazer isso?

- A tabela precisa ser criada antes de usar
- O main.py é o "coração" da aplicação
- Todas as funcionalidades são registradas lá

### Arquivo a Modificar

📁 `main.py`

### Mudanças a Fazer

Vamos adicionar **3 linhas** no arquivo `main.py`:

#### 1. Importar o Repository (próximo aos outros imports)

Procure a seção de imports dos repositories (deve estar perto de `from repo import usuario_repo`):

```python
from repo import usuario_repo, artigo_repo, comentario_repo
```

**Adicione** `categoria_repo`:

```python
from repo import usuario_repo, artigo_repo, comentario_repo, categoria_repo
```

#### 2. Criar a Tabela (dentro da função que cria tabelas)

Procure a função que cria as tabelas (geralmente chamada `criar_tabelas()` ou similar):

```python
def criar_tabelas():
    usuario_repo.criar_tabela()
    artigo_repo.criar_tabela()
    comentario_repo.criar_tabela()
```

**Adicione** a criação da tabela de categorias:

```python
def criar_tabelas():
    usuario_repo.criar_tabela()
    artigo_repo.criar_tabela()
    comentario_repo.criar_tabela()
    categoria_repo.criar_tabela()  # ← ADICIONE ESTA LINHA
```

### Explicação

#### Import do Repository

```python
from repo import categoria_repo
```

Isso torna todas as funções do `categoria_repo` disponíveis:
- `categoria_repo.criar_tabela()`
- `categoria_repo.inserir()`
- `categoria_repo.obter_todos()`
- etc.

#### Criação da Tabela

```python
categoria_repo.criar_tabela()
```

- Chamado quando o sistema inicia
- Cria a tabela `categoria` se não existir
- Se já existir, não faz nada (graças ao `IF NOT EXISTS`)

### ✅ Checkpoint

Após fazer essas modificações:

1. Execute a aplicação:

```bash
uvicorn main:app --reload
```

2. Verifique no terminal se não há erros
3. Acesse o banco de dados para verificar se a tabela foi criada:

```bash
sqlite3 dados.db "SELECT name FROM sqlite_master WHERE type='table' AND name='categoria';"
```

Se retornar `categoria`, a tabela foi criada com sucesso! 🎉

4. Pare a aplicação (Ctrl+C)

---

## Passo 6: Criar as Routes (Controllers)

### Objetivo

Criar os endpoints HTTP que receberão as requisições do navegador e responderão com as páginas HTML.

### O que são Routes?

**Routes** (rotas) são os **controladores** da aplicação. Eles:
- Recebem requisições HTTP (GET, POST)
- Validam os dados usando DTOs
- Chamam o Repository para acessar/modificar dados
- Retornam páginas HTML ou fazem redirects

**Analogia**: As routes são como **garçons** em um restaurante:
- Cliente faz pedido → Garçom recebe
- Garçom passa para cozinha → Repository acessa BD
- Cozinha prepara → Dados são processados
- Garçom entrega → HTML é retornado

### Arquivo a Criar

📁 `routes/admin_categorias_routes.py`

Este é o arquivo mais longo (246 linhas), mas vamos explicar cada parte.

### Estrutura Geral

```python
# Imports
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
# ... outros imports

# Configuração do Router
router = APIRouter(prefix="/admin/categorias")

# Rate Limiting (Controle de requisições)
admin_categorias_limiter = RateLimiter(...)

# Endpoints (7 funções)
1. index() - Redireciona para /listar
2. listar() - Lista todas as categorias
3. get_cadastrar() - Exibe formulário de cadastro
4. post_cadastrar() - Processa cadastro
5. get_editar() - Exibe formulário de edição
6. post_editar() - Processa edição
7. post_excluir() - Exclui categoria
```

### Código Completo - Parte 1: Imports e Configuração

```python
from typing import Optional
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from dtos.categoria_dto import CriarCategoriaDTO, AlterarCategoriaDTO
from model.categoria_model import Categoria
from repo import categoria_repo
from util.auth_util import requer_autenticacao
from util.mensagens_util import informar_sucesso, informar_erro
from util.rate_limiter import RateLimiter
from util.cliente_util import obter_identificador_cliente
from util.exceptions import FormValidationError
from model.perfil_model import Perfil

# Configura o roteador com prefixo /admin/categorias
router = APIRouter(prefix="/admin/categorias")

# Configura os templates HTML
templates = Jinja2Templates(directory="templates")

# Rate Limiter: máximo 10 operações por minuto
admin_categorias_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_categorias"
)
```

### Código Completo - Parte 2: Endpoints de Listagem

```python
@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona a raiz para /listar"""
    return RedirectResponse(
        url="/admin/categorias/listar",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """
    Lista todas as categorias.
    Acessível em: GET /admin/categorias/listar
    """
    # Busca todas as categorias do banco
    categorias = categoria_repo.obter_todos()

    # Renderiza o template com os dados
    return templates.TemplateResponse(
        "admin/categorias/listar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "categorias": categorias
        }
    )
```

### Código Completo - Parte 3: Endpoints de Cadastro

```python
@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """
    Exibe o formulário de cadastro.
    Acessível em: GET /admin/categorias/cadastrar
    """
    return templates.TemplateResponse(
        "admin/categorias/cadastro.html",
        {
            "request": request,
            "usuario_logado": usuario_logado
        }
    )


@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    usuario_logado: Optional[dict] = None,
    nome: str = Form(""),
    descricao: str = Form("")
):
    """
    Processa o cadastro de uma nova categoria.
    Acessível em: POST /admin/categorias/cadastrar
    """
    # Verifica rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            url="/admin/categorias/cadastrar",
            status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        # Valida os dados com o DTO
        dto = CriarCategoriaDTO(nome=nome, descricao=descricao)

        # Verifica se já existe categoria com este nome
        categoria_existente = categoria_repo.obter_por_nome(dto.nome)
        if categoria_existente:
            informar_erro(request, "Já existe uma categoria com este nome.")
            return RedirectResponse(
                url="/admin/categorias/cadastrar",
                status_code=status.HTTP_303_SEE_OTHER
            )

        # Cria o objeto Categoria
        nova_categoria = Categoria(
            nome=dto.nome,
            descricao=dto.descricao
        )

        # Insere no banco de dados
        categoria_inserida = categoria_repo.inserir(nova_categoria)

        if categoria_inserida:
            informar_sucesso(request, "Categoria cadastrada com sucesso!")
            return RedirectResponse(
                url="/admin/categorias/listar",
                status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            informar_erro(request, "Erro ao cadastrar categoria.")
            return RedirectResponse(
                url="/admin/categorias/cadastrar",
                status_code=status.HTTP_303_SEE_OTHER
            )

    except Exception as e:
        # Em caso de erro de validação, levanta exception
        # que será capturada pelo handler global
        raise FormValidationError(
            validation_error=e,
            template_path="admin/categorias/cadastro.html",
            dados_formulario={"nome": nome, "descricao": descricao},
            campo_padrao="nome"
        )
```

### Código Completo - Parte 4: Endpoints de Edição

```python
@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(
    request: Request,
    id: int,
    usuario_logado: Optional[dict] = None
):
    """
    Exibe o formulário de edição de uma categoria.
    Acessível em: GET /admin/categorias/editar/1
    """
    # Busca a categoria pelo ID
    categoria = categoria_repo.obter_por_id(id)

    if not categoria:
        informar_erro(request, "Categoria não encontrada.")
        return RedirectResponse(
            url="/admin/categorias/listar",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Renderiza o formulário com os dados da categoria
    return templates.TemplateResponse(
        "admin/categorias/editar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "categoria": categoria
        }
    )


@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    usuario_logado: Optional[dict] = None,
    nome: str = Form(""),
    descricao: str = Form("")
):
    """
    Processa a edição de uma categoria.
    Acessível em: POST /admin/categorias/editar/1
    """
    # Verifica rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            url=f"/admin/categorias/editar/{id}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Busca a categoria atual
    categoria_atual = categoria_repo.obter_por_id(id)
    if not categoria_atual:
        informar_erro(request, "Categoria não encontrada.")
        return RedirectResponse(
            url="/admin/categorias/listar",
            status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        # Valida os dados
        dto = AlterarCategoriaDTO(nome=nome, descricao=descricao)

        # Se o nome mudou, verifica se não existe outra categoria com o novo nome
        if dto.nome != categoria_atual.nome:
            categoria_existente = categoria_repo.obter_por_nome(dto.nome)
            if categoria_existente:
                informar_erro(request, "Já existe uma categoria com este nome.")
                return RedirectResponse(
                    url=f"/admin/categorias/editar/{id}",
                    status_code=status.HTTP_303_SEE_OTHER
                )

        # Atualiza os dados da categoria
        categoria_atual.nome = dto.nome
        categoria_atual.descricao = dto.descricao

        # Salva no banco
        if categoria_repo.alterar(categoria_atual):
            informar_sucesso(request, "Categoria alterada com sucesso!")
            return RedirectResponse(
                url="/admin/categorias/listar",
                status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            informar_erro(request, "Erro ao alterar categoria.")
            return RedirectResponse(
                url=f"/admin/categorias/editar/{id}",
                status_code=status.HTTP_303_SEE_OTHER
            )

    except Exception as e:
        raise FormValidationError(
            validation_error=e,
            template_path="admin/categorias/editar.html",
            dados_formulario={
                "nome": nome,
                "descricao": descricao,
                "id": id
            },
            campo_padrao="nome"
        )
```

### Código Completo - Parte 5: Endpoint de Exclusão

```python
@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(
    request: Request,
    id: int,
    usuario_logado: Optional[dict] = None
):
    """
    Exclui uma categoria.
    Acessível em: POST /admin/categorias/excluir/1
    """
    # Verifica rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            url="/admin/categorias/listar",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Busca a categoria
    categoria = categoria_repo.obter_por_id(id)
    if not categoria:
        informar_erro(request, "Categoria não encontrada.")
        return RedirectResponse(
            url="/admin/categorias/listar",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Exclui do banco
    if categoria_repo.excluir(id):
        informar_sucesso(request, f"Categoria '{categoria.nome}' excluída com sucesso!")
    else:
        informar_erro(request, "Erro ao excluir categoria.")

    return RedirectResponse(
        url="/admin/categorias/listar",
        status_code=status.HTTP_303_SEE_OTHER
    )
```

### Explicação Detalhada

#### Decoradores

```python
@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
```

1. `@router.get("/listar")`: Define que esta função responde a `GET /admin/categorias/listar`
2. `@requer_autenticacao([Perfil.ADMIN.value])`: Só admins podem acessar
3. `usuario_logado`: Preenchido automaticamente pelo decorator

#### Parâmetros Form

```python
async def post_cadastrar(
    request: Request,
    usuario_logado: Optional[dict] = None,
    nome: str = Form(""),
    descricao: str = Form("")
):
```

- `nome: str = Form("")`: Pega o campo `nome` do formulário HTML
- Se não existir, usa string vazia como padrão

#### Rate Limiting

```python
ip = obter_identificador_cliente(request)
if not admin_categorias_limiter.verificar(ip):
    informar_erro(request, "Muitas operações...")
```

- Limita a 10 operações por minuto por IP
- Previne spam e abuso

#### Validação com DTO

```python
try:
    dto = CriarCategoriaDTO(nome=nome, descricao=descricao)
except Exception as e:
    raise FormValidationError(...)
```

- Se dados inválidos → Pydantic lança exception
- `FormValidationError`: Re-lança como exception customizada
- Handler global processa e mostra erros no formulário

#### Verificação de Duplicidade

```python
categoria_existente = categoria_repo.obter_por_nome(dto.nome)
if categoria_existente:
    informar_erro(request, "Já existe uma categoria com este nome.")
```

- Evita categorias duplicadas
- Melhor fazer aqui do que confiar apenas no UNIQUE do BD

#### RedirectResponse

```python
return RedirectResponse(
    url="/admin/categorias/listar",
    status_code=status.HTTP_303_SEE_OTHER
)
```

- Redireciona o navegador para outra página
- `303 SEE OTHER`: Código HTTP para redirect após POST

#### TemplateResponse

```python
return templates.TemplateResponse(
    "admin/categorias/listar.html",
    {
        "request": request,
        "usuario_logado": usuario_logado,
        "categorias": categorias
    }
)
```

- Renderiza template HTML
- Passa variáveis para o template (request, usuario, categorias)

### Padrão POST-REDIRECT-GET

Todas as operações POST fazem redirect:

```
POST /cadastrar → Salva no BD → Redirect para /listar
```

**Por que?**
- Se usuário der F5 (refresh), não envia formulário novamente
- Evita duplicação de dados
- Melhor experiência de usuário

### ✅ Checkpoint

Após criar este arquivo:

1. Verifique se está em `routes/admin_categorias_routes.py`
2. Execute a aplicação:

```bash
uvicorn main:app --reload
```

3. Acesse no navegador (deve dar erro 404 de template, mas a rota existe):

```
http://localhost:8000/admin/categorias/listar
```

Se aparecer erro "Template not found", está correto! Vamos criar os templates nos próximos passos.

---

## Passo 7: Registrar as Routes no Main

### Objetivo

Fazer o FastAPI reconhecer e usar as routes de categorias.

### Arquivo a Modificar

📁 `main.py`

### Mudanças a Fazer

#### 1. Importar o Router

Procure a seção de imports dos routers:

```python
from routes.admin_artigos_routes import router as admin_artigos_router
from routes.admin_usuarios_routes import router as admin_usuarios_router
```

**Adicione**:

```python
from routes.admin_categorias_routes import router as admin_categorias_router
```

#### 2. Registrar o Router

Procure onde os routers são registrados:

```python
app.include_router(admin_artigos_router, tags=["Admin - Artigos"])
app.include_router(admin_usuarios_router, tags=["Admin - Usuários"])
```

**Adicione**:

```python
app.include_router(admin_categorias_router, tags=["Admin - Categorias"])
```

### Explicação

```python
app.include_router(admin_categorias_router, tags=["Admin - Categorias"])
```

- `include_router`: Registra todas as rotas do router
- `tags`: Organiza endpoints na documentação automática

### ✅ Checkpoint

1. Reinicie a aplicação
2. Acesse a documentação automática:

```
http://localhost:8000/docs
```

3. Procure pela seção "Admin - Categorias"
4. Deve listar os 7 endpoints criados

---

## Passo 8: Criar o Template de Listagem

### Objetivo

Criar a página HTML que exibe todas as categorias em uma tabela.

### Arquivo a Criar

📁 `templates/admin/categorias/listar.html`

Primeiro, crie a pasta:

```bash
mkdir -p templates/admin/categorias
```

### Código Completo

```html
{% extends "base_privada.html" %}

{% block titulo %}Categorias{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Gerenciar Categorias</h1>
        <a href="/admin/categorias/cadastrar" class="btn btn-primary">
            <i class="bi bi-plus-circle"></i> Nova Categoria
        </a>
    </div>

    {% if categorias %}
    <div class="table-responsive">
        <table class="table table-striped table-hover">
            <thead class="table-dark">
                <tr>
                    <th>ID</th>
                    <th>Nome</th>
                    <th>Descrição</th>
                    <th>Data Cadastro</th>
                    <th class="text-center">Ações</th>
                </tr>
            </thead>
            <tbody>
                {% for categoria in categorias %}
                <tr>
                    <td>{{ categoria.id }}</td>
                    <td><strong>{{ categoria.nome }}</strong></td>
                    <td>{{ categoria.descricao if categoria.descricao else '-' }}</td>
                    <td>
                        {% if categoria.data_cadastro %}
                            {{ categoria.data_cadastro.strftime('%d/%m/%Y %H:%M') }}
                        {% else %}
                            -
                        {% endif %}
                    </td>
                    <td class="text-center">
                        <a href="/admin/categorias/editar/{{ categoria.id }}"
                           class="btn btn-sm btn-warning"
                           title="Editar">
                            <i class="bi bi-pencil"></i>
                        </a>
                        <button type="button"
                                class="btn btn-sm btn-danger"
                                title="Excluir"
                                onclick="excluirCategoria({{ categoria.id }}, '{{ categoria.nome }}', '{{ categoria.descricao }}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% else %}
    <div class="alert alert-info">
        <i class="bi bi-info-circle"></i>
        Nenhuma categoria cadastrada ainda.
        <a href="/admin/categorias/cadastrar">Cadastre a primeira categoria</a>.
    </div>
    {% endif %}
</div>

<!-- Modal de Confirmação de Exclusão -->
<div class="modal fade" id="modalConfirmacao" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-danger text-white">
                <h5 class="modal-title">Confirmar Exclusão</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p id="mensagemConfirmacao"></p>
                <div id="detalhesConfirmacao"></div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <form id="formExcluir" method="POST" style="display:inline;">
                    <button type="submit" class="btn btn-danger">Confirmar Exclusão</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
function excluirCategoria(categoriaId, categoriaNome, categoriaDescricao) {
    // Monta os detalhes da categoria
    const detalhes = `
        <div class="alert alert-warning">
            <strong>ID:</strong> ${categoriaId}<br>
            <strong>Nome:</strong> ${categoriaNome}<br>
            <strong>Descrição:</strong> ${categoriaDescricao || '-'}
        </div>
    `;

    // Atualiza o modal
    document.getElementById('mensagemConfirmacao').textContent =
        'Tem certeza que deseja excluir esta categoria?';
    document.getElementById('detalhesConfirmacao').innerHTML = detalhes;
    document.getElementById('formExcluir').action = `/admin/categorias/excluir/${categoriaId}`;

    // Abre o modal
    const modal = new bootstrap.Modal(document.getElementById('modalConfirmacao'));
    modal.show();
}
</script>
{% endblock %}
```

### Explicação Detalhada

#### Extends e Blocks

```html
{% extends "base_privada.html" %}

{% block titulo %}Categorias{% endblock %}

{% block content %}
...
{% endblock %}
```

- `extends`: Herda o layout do template base (com menu, header, footer)
- `block titulo`: Define o título da página
- `block content`: Define o conteúdo principal

#### Loop Jinja2

```html
{% for categoria in categorias %}
<tr>
    <td>{{ categoria.id }}</td>
    <td>{{ categoria.nome }}</td>
</tr>
{% endfor %}
```

- Itera sobre a lista de categorias
- `{{ categoria.nome }}`: Exibe valor escapado (protegido contra XSS)

#### Condicionais

```html
{% if categorias %}
    <!-- Mostra tabela -->
{% else %}
    <!-- Mostra mensagem vazia -->
{% endif %}
```

#### Formatação de Data

```html
{{ categoria.data_cadastro.strftime('%d/%m/%Y %H:%M') }}
```

- Formata datetime para padrão brasileiro: 28/10/2025 14:30

#### Botão com Ícone Bootstrap

```html
<button class="btn btn-sm btn-danger" onclick="excluirCategoria(...)">
    <i class="bi bi-trash"></i>
</button>
```

- `btn btn-sm btn-danger`: Botão pequeno vermelho
- `bi bi-trash`: Ícone de lixeira do Bootstrap Icons

#### Modal Bootstrap

```html
<div class="modal fade" id="modalConfirmacao">
    <!-- Estrutura do modal -->
</div>
```

- Modal de confirmação antes de excluir
- Evita exclusões acidentais

#### JavaScript

```javascript
function excluirCategoria(categoriaId, categoriaNome, categoriaDescricao) {
    // Preenche os detalhes no modal
    document.getElementById('detalhesConfirmacao').innerHTML = detalhes;

    // Define a action do form
    document.getElementById('formExcluir').action = `/admin/categorias/excluir/${categoriaId}`;

    // Abre o modal
    const modal = new bootstrap.Modal(document.getElementById('modalConfirmacao'));
    modal.show();
}
```

- Preenche dinamicamente o modal com dados da categoria
- Define a URL de exclusão correta

### ✅ Checkpoint

1. Execute a aplicação:

```bash
uvicorn main:app --reload
```

2. Acesse como admin:

```
http://localhost:8000/admin/categorias/listar
```

3. Deve aparecer a mensagem "Nenhuma categoria cadastrada ainda"
4. Clique em "Nova Categoria" (vai dar erro porque não criamos o template ainda - próximo passo!)

---

## Passo 9: Criar o Template de Cadastro

### Objetivo

Criar o formulário HTML para cadastrar novas categorias.

### Arquivo a Criar

📁 `templates/admin/categorias/cadastro.html`

### Código Completo

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Cadastrar Categoria{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Cadastrar Categoria</h1>
        <a href="/admin/categorias/listar" class="btn btn-secondary">
            <i class="bi bi-arrow-left"></i> Voltar
        </a>
    </div>

    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card">
                <div class="card-body">
                    <form method="POST" action="/admin/categorias/cadastrar">
                        {{ field(
                            name='nome',
                            label='Nome da Categoria',
                            type='text',
                            required=true,
                            placeholder='Ex: Tecnologia, Esportes, Política...',
                            help_text='Nome único para identificar a categoria (3-50 caracteres)'
                        ) }}

                        {{ field(
                            name='descricao',
                            label='Descrição',
                            type='textarea',
                            required=false,
                            placeholder='Descrição opcional da categoria...',
                            help_text='Breve descrição sobre o que essa categoria abrange (máx 200 caracteres)',
                            rows=3
                        ) }}

                        <div class="d-flex justify-content-end gap-2 mt-4">
                            <a href="/admin/categorias/listar" class="btn btn-secondary">
                                Cancelar
                            </a>
                            <button type="submit" class="btn btn-primary">
                                <i class="bi bi-check-circle"></i> Cadastrar
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Explicação Detalhada

#### Import de Macro

```html
{% from "macros/form_fields.html" import field with context %}
```

- Importa a macro `field` do arquivo `macros/form_fields.html`
- `with context`: A macro tem acesso às variáveis do template (como `dados`, `erros`)

#### Macro `field`

```html
{{ field(
    name='nome',
    label='Nome da Categoria',
    type='text',
    required=true,
    placeholder='Ex: Tecnologia...',
    help_text='Texto de ajuda...'
) }}
```

Esta macro gera automaticamente:

1. **Label** com o texto e asterisco (se required)
2. **Input/Textarea** com classes Bootstrap
3. **Mensagem de erro** (se houver erro de validação)
4. **Help text** (texto de ajuda abaixo do campo)
5. **Valor pré-preenchido** (se formulário voltar com erro)

**Equivalente manual** (muito mais código!):

```html
<div class="mb-3">
    <label for="nome" class="form-label">
        Nome da Categoria <span class="text-danger">*</span>
    </label>
    <input
        type="text"
        class="form-control {% if erros.nome %}is-invalid{% endif %}"
        id="nome"
        name="nome"
        value="{{ dados.nome if dados else '' }}"
        required
        placeholder="Ex: Tecnologia...">
    {% if erros.nome %}
    <div class="invalid-feedback">{{ erros.nome }}</div>
    {% endif %}
    <small class="form-text text-muted">Texto de ajuda...</small>
</div>
```

A macro economiza muito código! 🎉

#### Parâmetros da Macro `field`

| Parâmetro | Tipo | Descrição | Exemplo |
|-----------|------|-----------|---------|
| `name` | str | Nome do campo (usado no form e no dict de erros) | `'nome'` |
| `label` | str | Texto do label | `'Nome da Categoria'` |
| `type` | str | Tipo do campo: `'text'`, `'textarea'`, `'email'`, etc. | `'text'` |
| `required` | bool | Se é obrigatório (mostra asterisco) | `true` |
| `placeholder` | str | Texto de exemplo no campo | `'Ex: Tecnologia...'` |
| `help_text` | str | Texto de ajuda abaixo do campo | `'Nome único...'` |
| `rows` | int | Número de linhas (só para textarea) | `3` |

#### Form Action

```html
<form method="POST" action="/admin/categorias/cadastrar">
```

- `method="POST"`: Envia dados via POST (seguro)
- `action="/admin/categorias/cadastrar"`: Endpoint que processará os dados

#### Botões

```html
<div class="d-flex justify-content-end gap-2 mt-4">
    <a href="/admin/categorias/listar" class="btn btn-secondary">
        Cancelar
    </a>
    <button type="submit" class="btn btn-primary">
        <i class="bi bi-check-circle"></i> Cadastrar
    </button>
</div>
```

- `d-flex justify-content-end gap-2`: Flexbox com gap entre botões
- Botão Cancelar → Link para voltar à listagem
- Botão Cadastrar → Submit do formulário

### Como Funciona o Fluxo de Erro

1. **Usuário preenche formulário incorretamente** (ex: nome com 1 letra)
2. **POST /cadastrar** → Route valida com DTO
3. **Pydantic detecta erro** → Lança ValidationError
4. **FormValidationError** é capturada pelo handler global
5. **Handler re-renderiza o template** passando:
   - `erros`: Dict com mensagens de erro por campo
   - `dados`: Dict com valores preenchidos (para não perder)
6. **Macro `field` exibe**:
   - Campo com borda vermelha (`is-invalid`)
   - Mensagem de erro abaixo do campo
   - Valor preenchido mantido

**Exemplo visual**:

```
┌────────────────────────────────────┐
│ Nome da Categoria *                │
│ ┌────────────────────────────────┐ │
│ │ Te                             │ │ ← Valor mantido
│ └────────────────────────────────┘ │
│ ❌ Nome deve ter no mínimo 3       │ ← Erro exibido
│    caracteres                      │
└────────────────────────────────────┘
```

### ✅ Checkpoint

1. Execute a aplicação
2. Acesse:

```
http://localhost:8000/admin/categorias/cadastrar
```

3. Teste o formulário:
   - Tente cadastrar com nome vazio → Deve mostrar erro
   - Tente com nome muito curto ("AB") → Deve mostrar erro
   - Cadastre com dados válidos → Deve salvar e redirecionar

---

## Passo 10: Criar o Template de Edição

### Objetivo

Criar o formulário HTML para editar categorias existentes.

### Arquivo a Criar

📁 `templates/admin/categorias/editar.html`

### Código Completo

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Editar Categoria{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Editar Categoria</h1>
        <a href="/admin/categorias/listar" class="btn btn-secondary">
            <i class="bi bi-arrow-left"></i> Voltar
        </a>
    </div>

    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card">
                <div class="card-body">
                    <form method="POST" action="/admin/categorias/editar/{{ categoria.id }}">
                        {{ field(
                            name='nome',
                            label='Nome da Categoria',
                            type='text',
                            required=true,
                            placeholder='Ex: Tecnologia, Esportes, Política...',
                            help_text='Nome único para identificar a categoria (3-50 caracteres)',
                            value=categoria.nome
                        ) }}

                        {{ field(
                            name='descricao',
                            label='Descrição',
                            type='textarea',
                            required=false,
                            placeholder='Descrição opcional da categoria...',
                            help_text='Breve descrição sobre o que essa categoria abrange (máx 200 caracteres)',
                            rows=3,
                            value=categoria.descricao
                        ) }}

                        <div class="d-flex justify-content-end gap-2 mt-4">
                            <a href="/admin/categorias/listar" class="btn btn-secondary">
                                Cancelar
                            </a>
                            <button type="submit" class="btn btn-warning">
                                <i class="bi bi-pencil"></i> Salvar Alterações
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Diferenças em Relação ao Cadastro

#### 1. Form Action Dinâmica

```html
<form method="POST" action="/admin/categorias/editar/{{ categoria.id }}">
```

- Usa o ID da categoria na URL
- Exemplo: `/admin/categorias/editar/5`

#### 2. Valores Pré-preenchidos

```html
{{ field(
    name='nome',
    ...
    value=categoria.nome  ← Preenche com valor atual
) }}
```

- `value=categoria.nome`: Campo começa com o nome atual
- `value=categoria.descricao`: Campo começa com a descrição atual

Se houver erro de validação, a macro usa `dados.nome` (do formulário) em vez de `categoria.nome`.

#### 3. Botão Diferente

```html
<button type="submit" class="btn btn-warning">
    <i class="bi bi-pencil"></i> Salvar Alterações
</button>
```

- `btn-warning`: Botão amarelo (padrão para edição)
- Texto: "Salvar Alterações" em vez de "Cadastrar"

### Como a Route Passa os Dados

Na route `get_editar()`:

```python
categoria = categoria_repo.obter_por_id(id)

return templates.TemplateResponse(
    "admin/categorias/editar.html",
    {
        "request": request,
        "usuario_logado": usuario_logado,
        "categoria": categoria  ← Objeto disponível no template
    }
)
```

No template, podemos acessar:
- `{{ categoria.id }}`
- `{{ categoria.nome }}`
- `{{ categoria.descricao }}`

### ✅ Checkpoint

1. Cadastre uma categoria
2. Na listagem, clique no botão de editar (ícone de lápis)
3. Verifique:
   - Campos estão pré-preenchidos
   - URL tem o ID da categoria
   - Ao salvar, volta para listagem com mensagem de sucesso

---

## Passo 11: Adicionar Link no Menu

### Objetivo

Adicionar o link "Categorias" no menu de administração para facilitar a navegação.

### Arquivo a Modificar

📁 `templates/base_privada.html`

### Mudança a Fazer

Procure a seção do menu de administração. Deve haver algo como:

```html
<li class="nav-item">
    <a class="nav-link" href="/admin/usuarios/listar">
        <i class="bi bi-people"></i> Usuários
    </a>
</li>
<li class="nav-item">
    <a class="nav-link" href="/admin/artigos/listar">
        <i class="bi bi-file-earmark-text"></i> Artigos
    </a>
</li>
```

**Adicione** após os outros itens:

```html
<li class="nav-item">
    <a class="nav-link" href="/admin/categorias/listar">
        <i class="bi bi-tags"></i> Categorias
    </a>
</li>
```

### Explicação

```html
<li class="nav-item">
    <a class="nav-link" href="/admin/categorias/listar">
        <i class="bi bi-tags"></i> Categorias
    </a>
</li>
```

- `nav-item` e `nav-link`: Classes Bootstrap para itens de menu
- `bi bi-tags`: Ícone de etiquetas (representa categorias)
- `href="/admin/categorias/listar"`: Link para a página de listagem

### Ícones Bootstrap Comuns

| Ícone | Classe | Uso Comum |
|-------|--------|-----------|
| 👥 | `bi bi-people` | Usuários |
| 📄 | `bi bi-file-earmark-text` | Artigos |
| 🏷️ | `bi bi-tags` | Categorias/Tags |
| 💬 | `bi bi-chat` | Comentários |
| ⚙️ | `bi bi-gear` | Configurações |
| 📊 | `bi bi-graph-up` | Estatísticas |

### ✅ Checkpoint

1. Reinicie a aplicação (ou apenas recarregue a página)
2. Entre como administrador
3. Verifique o menu lateral/superior
4. Deve aparecer o item "Categorias" com ícone de etiqueta
5. Clique nele → Deve ir para `/admin/categorias/listar`

---

## Passo 12: Testar o CRUD Completo

### Objetivo

Realizar testes end-to-end (ponta a ponta) para garantir que tudo funciona corretamente.

### Checklist de Testes

#### ✅ Teste 1: Listar Categorias Vazias

1. Acesse: `http://localhost:8000/admin/categorias/listar`
2. **Esperado**: Mensagem "Nenhuma categoria cadastrada ainda"

#### ✅ Teste 2: Cadastrar Categoria Válida

1. Clique em "Nova Categoria"
2. Preencha:
   - **Nome**: Tecnologia
   - **Descrição**: Artigos sobre tecnologia e inovação
3. Clique em "Cadastrar"
4. **Esperado**:
   - Redireciona para listagem
   - Toast de sucesso: "Categoria cadastrada com sucesso!"
   - Categoria aparece na tabela

#### ✅ Teste 3: Cadastrar com Nome Muito Curto

1. Clique em "Nova Categoria"
2. Preencha:
   - **Nome**: AB (apenas 2 caracteres)
3. Clique em "Cadastrar"
4. **Esperado**:
   - Volta para formulário
   - Campo nome com borda vermelha
   - Mensagem: "Nome deve ter no mínimo 3 caracteres"
   - Valor "AB" mantido no campo

#### ✅ Teste 4: Cadastrar com Nome Duplicado

1. Tente cadastrar outra categoria com nome "Tecnologia"
2. **Esperado**:
   - Toast de erro: "Já existe uma categoria com este nome"
   - Volta para formulário

#### ✅ Teste 5: Editar Categoria

1. Na listagem, clique no botão amarelo (editar) da categoria "Tecnologia"
2. **Esperado**: Formulário pré-preenchido com dados atuais
3. Altere:
   - **Nome**: Tecnologia e Inovação
   - **Descrição**: Artigos sobre o mundo tech
4. Clique em "Salvar Alterações"
5. **Esperado**:
   - Redireciona para listagem
   - Toast: "Categoria alterada com sucesso!"
   - Nome atualizado na tabela

#### ✅ Teste 6: Excluir Categoria

1. Na listagem, clique no botão vermelho (excluir)
2. **Esperado**: Modal de confirmação aparece com:
   - Título: "Confirmar Exclusão"
   - Detalhes da categoria (ID, nome, descrição)
3. Clique em "Cancelar" → Modal fecha, nada acontece
4. Clique novamente no botão de excluir
5. Clique em "Confirmar Exclusão"
6. **Esperado**:
   - Modal fecha
   - Redireciona para listagem
   - Toast: "Categoria 'Tecnologia e Inovação' excluída com sucesso!"
   - Categoria não aparece mais na tabela

#### ✅ Teste 7: Rate Limiting

1. Tente cadastrar 11 categorias rapidamente (menos de 1 minuto)
2. **Esperado**:
   - Na 11ª tentativa, toast de erro: "Muitas operações em pouco tempo..."
   - Aguarde 1 minuto
   - Tente novamente → Deve funcionar

#### ✅ Teste 8: Validação de Descrição Longa

1. Tente cadastrar com descrição de 250 caracteres
2. **Esperado**:
   - Erro: "Descrição deve ter no máximo 200 caracteres"

#### ✅ Teste 9: Persistência de Dados

1. Pare a aplicação (Ctrl+C)
2. Reinicie: `uvicorn main:app --reload`
3. Acesse a listagem
4. **Esperado**: Categorias cadastradas continuam lá (salvas no BD)

#### ✅ Teste 10: Acesso Não Autorizado

1. Faça logout
2. Tente acessar: `http://localhost:8000/admin/categorias/listar`
3. **Esperado**: Redireciona para página de login

### Teste no Terminal

Você também pode testar via linha de comando:

```bash
# Teste 1: Listar (precisa estar logado como admin)
curl -X GET http://localhost:8000/admin/categorias/listar

# Teste 2: Criar (POST)
curl -X POST http://localhost:8000/admin/categorias/cadastrar \
  -d "nome=Esportes&descricao=Notícias esportivas"

# Teste 3: Ver documentação automática
# Acesse: http://localhost:8000/docs
# Procure por "Admin - Categorias"
```

### ✅ Checkpoint Final

Se todos os testes passaram, **parabéns!** 🎉

Você implementou com sucesso um **CRUD completo e funcional** com:
- ✅ Backend (FastAPI + SQLite)
- ✅ Frontend (HTML + Bootstrap)
- ✅ Validação de dados
- ✅ Mensagens de feedback
- ✅ Segurança (autenticação, rate limiting, SQL injection prevention)
- ✅ UX (confirmação de exclusão, campos pré-preenchidos)

---

## Padrões e Boas Práticas

### 1. Convenções de Nomenclatura

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| **Arquivos** | `snake_case` | `categoria_repo.py`, `admin_categorias_routes.py` |
| **Classes** | `PascalCase` | `Categoria`, `CriarCategoriaDTO` |
| **Funções** | `snake_case` | `obter_por_id()`, `criar_tabela()` |
| **Constantes** | `UPPER_SNAKE_CASE` | `CRIAR_TABELA`, `INSERIR` |
| **Variáveis** | `snake_case` | `categoria_existente`, `nova_categoria` |
| **Parâmetros** | `snake_case` | `tamanho_minimo`, `campo_padrao` |

### 2. Estrutura de Pastas

```
SimpleBlog/
├── sql/              # Queries SQL
├── model/            # Modelos de domínio (entidades)
├── dtos/             # Data Transfer Objects (validação)
├── repo/             # Repositories (acesso a dados)
├── routes/           # Controllers (endpoints HTTP)
├── templates/        # Views (HTML)
│   ├── admin/        # Templates de admin
│   └── macros/       # Componentes reutilizáveis
└── util/             # Utilidades (auth, db, etc)
```

### 3. Fluxo de Dados (Data Flow)

```
Usuário preenche formulário
        ↓
Form POST → Route recebe dados
        ↓
Route valida com DTO
        ↓
DTO aprova ou rejeita
        ↓
Route chama Repository
        ↓
Repository executa SQL
        ↓
Database salva
        ↓
Repository retorna resultado
        ↓
Route redireciona com mensagem
        ↓
Usuário vê feedback
```

### 4. Tratamento de Erros

#### Camadas de Validação

1. **Frontend**: HTML5 validation (required, maxlength)
2. **DTO**: Pydantic validation (tipos, tamanhos, formatos)
3. **Route**: Business logic (duplicidade, permissões)
4. **Database**: Constraints (UNIQUE, NOT NULL, FK)

#### Exemplo de Erro

```
Usuário digita nome "AB"
  ↓
HTML5 não bloqueia (apenas 2 chars é válido em HTML)
  ↓
POST enviado
  ↓
DTO: ValidationError("Nome deve ter no mínimo 3 caracteres")
  ↓
FormValidationError capturada
  ↓
Handler re-renderiza formulário com erro
  ↓
Usuário vê campo vermelho e mensagem
```

### 5. Segurança

#### SQL Injection Prevention

```python
# ✅ SEGURO (parameterized query)
cursor.execute("SELECT * FROM categoria WHERE nome=?", (nome,))

# ❌ INSEGURO (string concatenation)
cursor.execute(f"SELECT * FROM categoria WHERE nome='{nome}'")
```

Se `nome = "'; DROP TABLE categoria; --"`:
- Seguro → Busca literal por esse texto
- Inseguro → Executa DROP TABLE! 💣

#### XSS Prevention

```html
<!-- ✅ SEGURO (Jinja2 escapa automaticamente) -->
{{ categoria.nome }}

<!-- Se nome = "<script>alert('XSS')</script>" -->
<!-- Renderiza como: &lt;script&gt;alert('XSS')&lt;/script&gt; -->

<!-- ❌ INSEGURO (raw HTML) -->
{{ categoria.nome|safe }}
```

#### CSRF Protection

- Formulários POST são protegidos por sessão
- Só aceita requisições do mesmo domínio

#### Rate Limiting

```python
admin_categorias_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_categorias"
)
```

Previne:
- Brute force
- Spam
- DoS (Denial of Service)

### 6. Padrões de Código

#### Repository Pattern

✅ **Com Repository**:
```python
# Route
categorias = categoria_repo.obter_todos()
```

- Simples de usar
- Fácil de testar (mock)
- Pode trocar BD sem mudar a route

❌ **Sem Repository**:
```python
# Route tem que saber SQL, conexão, etc.
conn = sqlite3.connect("dados.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM categoria")
rows = cursor.fetchall()
conn.close()
```

#### DTO Pattern

✅ **Com DTO**:
```python
dto = CriarCategoriaDTO(nome=nome, descricao=descricao)
# Se inválido, lança exception
# Se válido, dto.nome e dto.descricao estão limpos
```

- Validação centralizada
- Mensagens de erro consistentes
- Reutilizável

❌ **Sem DTO**:
```python
if not nome or len(nome) < 3:
    return "Nome inválido"
if len(nome) > 50:
    return "Nome muito longo"
# Repetir isso em cada endpoint? ❌
```

### 7. Comentários e Documentação

#### Docstrings

```python
def obter_por_id(id: int) -> Optional[Categoria]:
    """
    Busca uma categoria por ID.

    Args:
        id: ID da categoria

    Returns:
        Objeto Categoria se encontrou, None se não encontrou

    Exemplo:
        cat = obter_por_id(5)
        if cat:
            print(f"Encontrada: {cat.nome}")
    """
```

#### Comentários Inline

```python
# Pega o ID gerado automaticamente
if cursor.lastrowid:
    categoria.id = cursor.lastrowid
```

Use comentários para explicar **por que**, não **o que**.

❌ Ruim:
```python
# Incrementa i
i += 1
```

✅ Bom:
```python
# Pula o cabeçalho da primeira linha
i += 1
```

---

## Troubleshooting

### Problema 1: Erro "Template not found"

**Sintoma**:
```
jinja2.exceptions.TemplateNotFound: admin/categorias/listar.html
```

**Soluções**:
1. Verifique se a pasta existe: `templates/admin/categorias/`
2. Verifique se o arquivo existe: `listar.html`
3. Verifique o nome exato (case-sensitive)
4. Verifique se `templates` está configurado no FastAPI:
   ```python
   templates = Jinja2Templates(directory="templates")
   ```

### Problema 2: Categoria não salva no banco

**Sintoma**: Após cadastrar, lista continua vazia

**Soluções**:
1. Verifique se `categoria_repo.criar_tabela()` foi chamado no `main.py`
2. Verifique se o commit está sendo feito:
   ```python
   with get_connection() as conn:  # ← Context manager faz commit automático
   ```
3. Verifique o banco de dados:
   ```bash
   sqlite3 dados.db "SELECT * FROM categoria;"
   ```
4. Verifique erros no terminal

### Problema 3: Import Error

**Sintoma**:
```
ModuleNotFoundError: No module named 'dtos.categoria_dto'
```

**Soluções**:
1. Verifique se o arquivo existe no caminho correto
2. Verifique se há `__init__.py` na pasta `dtos/`
3. Execute do diretório raiz do projeto
4. Reinstale dependências: `pip install -r requirements.txt`

### Problema 4: Erro 404 ao acessar rota

**Sintoma**: `http://localhost:8000/admin/categorias/listar` retorna 404

**Soluções**:
1. Verifique se o router foi registrado no `main.py`:
   ```python
   app.include_router(admin_categorias_router)
   ```
2. Verifique o prefixo do router:
   ```python
   router = APIRouter(prefix="/admin/categorias")
   ```
3. Reinicie a aplicação
4. Acesse `/docs` para ver todas as rotas disponíveis

### Problema 5: Validação não funciona

**Sintoma**: Consegue cadastrar categoria com nome vazio

**Soluções**:
1. Verifique se o DTO está sendo usado:
   ```python
   dto = CriarCategoriaDTO(nome=nome, descricao=descricao)
   ```
2. Verifique se FormValidationError está sendo capturada
3. Verifique se há `try/except` ao redor da validação
4. Verifique os validadores no DTO

### Problema 6: Modal de exclusão não abre

**Sintoma**: Clica em excluir, nada acontece

**Soluções**:
1. Abra o Console do navegador (F12) → Procure por erros JavaScript
2. Verifique se o Bootstrap JS está carregado:
   ```html
   <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
   ```
3. Verifique o ID do modal: `id="modalConfirmacao"`
4. Verifique a função `excluirCategoria()` no `{% block scripts %}`

### Problema 7: Erro "UNIQUE constraint failed"

**Sintoma**:
```
sqlite3.IntegrityError: UNIQUE constraint failed: categoria.nome
```

**Solução**:
Isso é esperado! Significa que a constraint UNIQUE está funcionando.

Mas você deve **tratar esse erro antes** verificando:
```python
categoria_existente = categoria_repo.obter_por_nome(dto.nome)
if categoria_existente:
    informar_erro(request, "Já existe uma categoria com este nome.")
```

### Problema 8: Rate Limiter sempre bloqueia

**Sintoma**: Primeira requisição já é bloqueada

**Soluções**:
1. Verifique o limite configurado:
   ```python
   RateLimiter(max_tentativas=10, janela_minutos=1)
   ```
2. Limpe o cache do rate limiter (reinicie a aplicação)
3. Verifique se `obter_identificador_cliente()` está funcionando

### Problema 9: Estilos não aparecem

**Sintoma**: Página sem formatação (sem cores, sem layout)

**Soluções**:
1. Verifique se o Bootstrap está sendo carregado no `base_privada.html`:
   ```html
   <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
   ```
2. Verifique a conexão com internet (Bootstrap vem de CDN)
3. Abra o Console → Aba Network → Procure por erros 404

### Problema 10: Mensagens (toasts) não aparecem

**Sintoma**: Categoria cadastrada mas não vê toast de sucesso

**Soluções**:
1. Verifique se está usando `informar_sucesso()` na route
2. Verifique se `base_privada.html` tem o sistema de toasts
3. Verifique se há JavaScript para mostrar os toasts
4. Abra o Console → Procure por erros

---

## Exercícios Propostos

Agora que você domina CRUD, pratique implementando outros CRUDs!

### Exercício 1: CRUD de Tags ⭐

Implemente um CRUD de Tags com:
- **Campos**: id, nome, cor (hex color)
- **Validação**: nome 2-30 chars, cor formato #XXXXXX
- **Extra**: Mostrar preview da cor na listagem

<details>
<summary>💡 Dica</summary>

1. Copie os arquivos de categoria
2. Substitua "categoria" por "tag" em todos os lugares
3. Adicione campo `cor` na tabela e no Model
4. Adicione validação de cor no DTO
5. No template de listagem, adicione:
   ```html
   <td>
       <span class="badge" style="background-color: {{ tag.cor }}">
           {{ tag.nome }}
       </span>
   </td>
   ```
</details>

### Exercício 2: CRUD de Autores ⭐⭐

Implemente um CRUD de Autores com:
- **Campos**: id, nome, biografia, email, foto_url
- **Validação**: email válido, biografia máx 500 chars
- **Extra**: Upload de foto de perfil

### Exercício 3: Relacionamento Artigo-Categoria ⭐⭐⭐

Adicione categorias aos artigos:
1. Tabela `artigo_categoria` (muitos-para-muitos)
2. Ao criar/editar artigo, selecione categorias
3. Na listagem de artigos, mostre suas categorias
4. Crie página pública: "Artigos da categoria X"

### Exercício 4: Soft Delete ⭐⭐

Implementar exclusão lógica:
1. Adicione campo `excluido` (boolean) na tabela
2. `excluir()` → Apenas marca como excluído
3. `obter_todos()` → Filtra excluídos
4. Crie rota "Lixeira" para recuperar

### Exercício 5: Paginação ⭐⭐⭐

Adicione paginação na listagem:
1. Aceite parâmetro `?pagina=1` na URL
2. `obter_todos()` → Aceite `limite` e `offset`
3. Template → Botões "Anterior" e "Próximo"
4. Mostre "Página X de Y"

### Exercício 6: Busca e Filtros ⭐⭐⭐

Adicione busca na listagem:
1. Campo de busca no topo da tabela
2. Aceite parâmetro `?busca=termo`
3. SQL: `WHERE nome LIKE ?` com `%termo%`
4. Mantenha busca ao paginar

### Exercício 7: Exportar CSV ⭐⭐

Adicione botão "Exportar CSV":
1. Nova rota `/admin/categorias/exportar`
2. Gere CSV com todas as categorias
3. Retorne como download:
   ```python
   from fastapi.responses import StreamingResponse
   ```

### Exercício 8: Importar CSV ⭐⭐⭐

Adicione formulário para importar categorias de CSV:
1. Upload de arquivo
2. Parse CSV com `csv` module
3. Valide cada linha
4. Insira no banco
5. Retorne relatório (X inseridas, Y erros)

### Exercício 9: Hierarquia de Categorias ⭐⭐⭐⭐

Categorias com sub-categorias:
1. Adicione campo `categoria_pai_id`
2. Ao criar, selecione categoria pai (opcional)
3. Na listagem, mostre hierarquia com indentação
4. Crie função recursiva `obter_filhos()`

### Exercício 10: Testes Automatizados ⭐⭐⭐⭐

Escreva testes com pytest:
1. Teste unitário: DTOs validam corretamente
2. Teste unitário: Repository CRUD funciona
3. Teste integração: Routes retornam status corretos
4. Teste E2E: Selenium/Playwright testa UI

<details>
<summary>💡 Exemplo de teste</summary>

```python
import pytest
from dtos.categoria_dto import CriarCategoriaDTO
from pydantic import ValidationError

def test_dto_valida_nome_curto():
    with pytest.raises(ValidationError):
        CriarCategoriaDTO(nome="AB", descricao="Teste")

def test_dto_aceita_nome_valido():
    dto = CriarCategoriaDTO(nome="Tecnologia", descricao="Desc")
    assert dto.nome == "Tecnologia"
```
</details>

---

## Conclusão

🎉 **Parabéns!** Você concluiu o tutorial completo de CRUD no SimpleBlog!

### O que Você Aprendeu

✅ Arquitetura em camadas (SQL → Model → DTO → Repository → Routes → Templates)
✅ Validação de dados com Pydantic
✅ Padrões de projeto (Repository, DTO, MVC)
✅ Segurança (SQL injection, XSS, rate limiting)
✅ Frontend com Bootstrap e Jinja2
✅ Tratamento de erros e feedback ao usuário
✅ Boas práticas de código Python

### Próximos Passos

1. **Pratique**: Implemente os exercícios propostos
2. **Expanda**: Adicione recursos avançados (busca, paginação, etc.)
3. **Teste**: Escreva testes automatizados
4. **Documente**: Crie documentação da API
5. **Deploy**: Coloque em produção (Heroku, Railway, etc.)

### Recursos Adicionais

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **Bootstrap Docs**: https://getbootstrap.com/docs/
- **Jinja2 Docs**: https://jinja.palletsprojects.com/
- **SQLite Docs**: https://www.sqlite.org/docs.html

### Dúvidas?

Se encontrar problemas:
1. Releia a seção de [Troubleshooting](#troubleshooting)
2. Consulte os logs de erro no terminal
3. Use o debugger do VS Code (F5)
4. Pesquise no Stack Overflow
5. Peça ajuda ao professor/colegas

**Bons estudos e bons códigos!** 💻✨
