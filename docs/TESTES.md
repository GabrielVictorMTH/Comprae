# Guia de Testes do DefaultWebApp

## 📊 Visão Geral

O projeto possui **165 testes automatizados** cobrindo 100% das rotas da aplicação, garantindo qualidade, segurança e prevenção de regressões.

## 🚀 Executando os Testes

### Comandos Básicos

```bash
# Executar todos os testes
pytest tests/

# Executar com verbose
pytest tests/ -v

# Executar apenas um arquivo
pytest tests/test_perfil.py

# Executar apenas uma classe
pytest tests/test_perfil.py::TestEditarPerfil

# Executar apenas um teste específico
pytest tests/test_perfil.py::TestEditarPerfil::test_editar_perfil_com_dados_validos

# Executar com stacktrace curto
pytest tests/ --tb=short

# Executar sem stacktrace (apenas resumo)
pytest tests/ --tb=no

# Executar modo silencioso
pytest tests/ -q

# Executar com cobertura (se pytest-cov instalado)
pytest tests/ --cov=. --cov-report=html
```

### Filtros Úteis

```bash
# Executar apenas testes de autenticação
pytest tests/test_auth.py

# Executar apenas testes de admin
pytest tests/test_admin_*.py

# Executar apenas testes que contenham "senha" no nome
pytest tests/ -k senha

# Executar com markers (se configurados)
pytest tests/ -m auth
```

## 📁 Estrutura dos Testes

```
tests/
├── conftest.py                  # Fixtures compartilhadas
├── test_auth.py                 # Autenticação (24 testes)
├── test_tarefas.py              # CRUD de Tarefas (25 testes)
├── test_perfil.py               # Gerenciamento de Perfil (21 testes)
├── test_usuario.py              # Dashboard do Usuário (5 testes)
├── test_admin_usuarios.py       # Gestão de Usuários (23 testes)
├── test_admin_configuracoes.py  # Temas e Auditoria (21 testes)
├── test_admin_backups.py        # Gestão de Backups (23 testes)
└── test_public.py               # Rotas Públicas (23 testes)
```

## 🧪 Fixtures Disponíveis

### Fixtures de Cliente

- **`client`**: Cliente HTTP básico sem autenticação
- **`cliente_autenticado`**: Cliente autenticado como CLIENTE
- **`admin_autenticado`**: Cliente autenticado como ADMIN
- **`vendedor_autenticado`**: Cliente autenticado como VENDEDOR

### Fixtures de Dados

- **`usuario_teste`**: Dados de um usuário CLIENTE de teste
- **`admin_teste`**: Dados de um usuário ADMIN de teste
- **`vendedor_teste`**: Dados de um usuário VENDEDOR de teste
- **`tarefa_teste`**: Dados de uma tarefa de teste
- **`foto_teste_base64`**: Imagem PNG válida em base64

### Fixtures de Helpers

- **`criar_usuario`**: Função para criar usuários via endpoint
- **`fazer_login`**: Função para fazer login
- **`criar_tarefa`**: Função para criar tarefas
- **`criar_backup`**: Função para criar backups

## 📋 Categorias de Testes

### 1. Testes de Autenticação (`test_auth.py`)

**Classes:**
- `TestLogin`: Login com credenciais válidas/inválidas
- `TestCadastro`: Cadastro de novos usuários
- `TestLogout`: Logout e limpeza de sessão
- `TestRecuperacaoSenha`: Esqueci senha e redefinição
- `TestAutorizacao`: Controle de acesso por perfil
- `TestRateLimiting`: Limite de tentativas

**Exemplo:**
```python
def test_login_com_credenciais_validas(self, client, criar_usuario, usuario_teste):
    """Deve fazer login com credenciais válidas"""
    criar_usuario(
        usuario_teste["nome"],
        usuario_teste["email"],
        usuario_teste["senha"]
    )

    response = client.post("/login", data={
        "email": usuario_teste["email"],
        "senha": usuario_teste["senha"]
    }, follow_redirects=False)

    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["location"] == "/usuario"
```

### 2. Testes de Perfil (`test_perfil.py`)

**Classes:**
- `TestVisualizarPerfil`: Visualização de dados do perfil
- `TestEditarPerfil`: Edição de nome e email
- `TestAlterarSenha`: Alteração de senha com validações
- `TestAtualizarFoto`: Upload de foto de perfil

**Validações Testadas:**
- Email único (não pode duplicar)
- Senha atual correta
- Nova senha diferente da atual
- Senhas coincidem
- Força da senha
- Tamanho da foto (máx 10MB)

### 3. Testes de Usuário (`test_usuario.py`)

**Classes:**
- `TestDashboard`: Acesso ao dashboard por diferentes perfis

### 4. Testes de Admin - Usuários (`test_admin_usuarios.py`)

**Classes:**
- `TestListarUsuarios`: Listagem (ADMIN only)
- `TestCadastrarUsuario`: Criação com qualquer perfil
- `TestEditarUsuario`: Edição de dados
- `TestExcluirUsuario`: Exclusão (com proteção de auto-exclusão)

**Segurança:**
- Cliente não pode acessar áreas de admin
- Vendedor não pode acessar áreas de admin
- Admin não pode excluir a si mesmo

### 5. Testes de Admin - Configurações (`test_admin_configuracoes.py`)

**Classes:**
- `TestTema`: Seleção e aplicação de temas Bootswatch
- `TestAuditoria`: Visualização e filtro de logs
- `TestSegurancaConfiguracoes`: Controle de acesso

**Filtros de Log:**
- Por data (formato YYYY-MM-DD)
- Por nível (INFO, WARNING, ERROR, DEBUG, CRITICAL, TODOS)

### 6. Testes de Admin - Backups (`test_admin_backups.py`)

**Classes:**
- `TestListarBackups`: Listagem de backups
- `TestCriarBackup`: Criação de backups
- `TestRestaurarBackup`: Restauração com backup automático
- `TestExcluirBackup`: Exclusão de backups
- `TestDownloadBackup`: Download de arquivos
- `TestFluxoCompletoBackup`: Testes de integração

**Recursos:**
- Nome com timestamp (backup_YYYYMMDD_HHMMSS.db)
- Backup automático antes de restaurar
- Validação de existência de arquivo

### 7. Testes de Tarefas (`test_tarefas.py`)

**Classes:**
- `TestListarTarefas`: Listagem de tarefas do usuário
- `TestCriarTarefa`: Criação com validações
- `TestConcluirTarefa`: Marcar como concluída
- `TestExcluirTarefa`: Exclusão
- `TestIsolamentoTarefas`: Segurança entre usuários
- `TestValidacoesTarefa`: Validações específicas

**Isolamento:**
- Usuário A não vê tarefas de usuário B
- Usuário A não pode concluir tarefas de usuário B
- Usuário A não pode excluir tarefas de usuário B

### 8. Testes de Rotas Públicas (`test_public.py`)

**Classes:**
- `TestRotasPublicas`: Landing page, sobre
- `TestRotasPublicasComUsuarioLogado`: Acesso por usuários logados
- `TestExemplos`: Páginas de demonstração
- `TestHealthCheck`: Endpoint de health check
- `TestErros`: Páginas de erro 404

## 🎯 Padrões de Código dos Testes

### Organização em Classes

```python
class TestFuncionalidade:
    """Descrição da funcionalidade"""

    def test_caso_de_uso_especifico(self, fixture1, fixture2):
        """Docstring explicando o que deve acontecer"""
        # Arrange (preparar)
        dados = {"campo": "valor"}

        # Act (executar)
        response = client.post("/rota", data=dados)

        # Assert (verificar)
        assert response.status_code == status.HTTP_200_OK
```

### Nomenclatura de Testes

- Começar com `test_`
- Usar snake_case
- Ser descritivo e específico
- Indicar o comportamento esperado

**Exemplos:**
- ✅ `test_login_com_credenciais_validas`
- ✅ `test_cadastro_com_email_duplicado`
- ✅ `test_admin_nao_pode_excluir_a_si_mesmo`
- ❌ `test_login`
- ❌ `test_erro`

### Assertions Comuns

```python
# Status HTTP
assert response.status_code == status.HTTP_200_OK
assert response.status_code == status.HTTP_303_SEE_OTHER
assert response.status_code == status.HTTP_403_FORBIDDEN

# Redirecionamentos
assert response.headers["location"] == "/destino"

# Conteúdo da resposta
assert "texto esperado" in response.text
assert "erro" in response.text.lower()

# Dados no banco
assert usuario is not None
assert usuario.email == "teste@example.com"
assert len(tarefas) == 0
```

## 🔍 Debugging de Testes

### Ver Output Completo

```bash
# Mostrar prints e logs
pytest tests/ -s

# Mostrar stacktrace completo
pytest tests/ --tb=long

# Parar no primeiro erro
pytest tests/ -x

# Modo verboso + stacktrace
pytest tests/ -vv --tb=long
```

### Executar Teste Específico

```bash
# Por nome exato
pytest tests/test_perfil.py::TestEditarPerfil::test_editar_perfil_com_dados_validos

# Com breakpoint (pdb)
pytest tests/test_perfil.py::TestEditarPerfil::test_editar_perfil_com_dados_validos --pdb
```

### Adicionar Prints Temporários

```python
def test_exemplo(self, cliente_autenticado):
    response = cliente_autenticado.get("/rota")
    print(f"Status: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Body: {response.text[:500]}")  # Primeiros 500 chars
    assert response.status_code == 200
```

## ⚙️ Configuração

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --tb=short
    --disable-warnings
markers =
    auth: Testes de autenticação
    crud: Testes de CRUD
    integration: Testes de integração
    unit: Testes unitários
```

### conftest.py

O arquivo `conftest.py` contém:
- Configuração do banco de dados de teste
- Fixtures compartilhadas
- Setup e teardown automáticos
- Limpeza de rate limiters
- Limpeza de tabelas entre testes

## 🐛 Bugs Identificados pelos Testes

Durante a criação dos testes, foi identificado e corrigido o seguinte bug:

**Localização:** `routes/admin_backups_routes.py:162`

**Problema:** Faltava o parâmetro `request: Request` na função `get_download`, causando `IndexError: tuple index out of range` no decorador `@requer_autenticacao`.

**Correção:**
```python
# ANTES (bugado)
async def get_download(
    nome_arquivo: str,
    usuario_logado: Optional[dict] = None
):

# DEPOIS (corrigido)
async def get_download(
    request: Request,  # ← Adicionado
    nome_arquivo: str,
    usuario_logado: Optional[dict] = None
):
```

## 📈 Métricas

- **Total de Testes:** 165
- **Taxa de Sucesso:** 100%
- **Tempo de Execução:** ~61 segundos
- **Linhas de Código:** ~1.346
- **Cobertura de Rotas:** 100%
- **Arquivos de Teste:** 8

## 🔄 Integração Contínua (CI/CD)

### GitHub Actions (exemplo)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run tests
      run: |
        pytest tests/ -v --tb=short
```

## 📚 Boas Práticas

1. **Execute os testes antes de commitar:**
   ```bash
   pytest tests/ --tb=short
   ```

2. **Adicione testes para novos recursos:**
   - Seguir o padrão dos testes existentes
   - Testar casos de sucesso e falha
   - Testar validações
   - Testar permissões

3. **Mantenha os testes independentes:**
   - Cada teste deve funcionar isoladamente
   - Não depender da ordem de execução
   - Limpar dados após cada teste

4. **Use fixtures para reutilização:**
   - Criar fixtures para dados comuns
   - Compartilhar lógica repetitiva

5. **Documente comportamentos complexos:**
   - Adicionar comentários explicativos
   - Descrever casos de borda

## 🆘 Troubleshooting

### Banco de dados travado

```bash
# Remover banco de teste manualmente
rm /tmp/test_*.db
```

### Rate limiting bloqueando testes

O `conftest.py` já limpa os rate limiters automaticamente. Se ainda houver problema:

```python
# Em conftest.py, verificar fixture limpar_rate_limiter
@pytest.fixture(scope="function", autouse=True)
def limpar_rate_limiter():
    # ... limpeza automática
```

### Sessão não limpa entre testes

Verificar se o banco está sendo limpo no `conftest.py`:

```python
@pytest.fixture(scope="function", autouse=True)
def limpar_banco_dados():
    # ... limpeza automática
```

## 🎓 Recursos Adicionais

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Testing Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
