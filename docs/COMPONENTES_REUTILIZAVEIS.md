# Componentes Reutilizáveis - DefaultWebApp

Este documento cataloga todos os componentes reutilizáveis disponíveis no projeto, incluindo macros de templates, helpers backend e módulos JavaScript.

## 📋 Índice

1. [Macros de Template](#macros-de-template)
   - [Badges](#badges)
   - [Action Buttons](#action-buttons)
   - [Empty States](#empty-states)
2. [Helpers Backend](#helpers-backend)
   - [Rate Limiting](#rate-limiting)
   - [Repository Helpers](#repository-helpers)
   - [Permission Helpers](#permission-helpers)
3. [Módulos JavaScript](#módulos-javascript)
   - [Delete Helpers](#delete-helpers)

---

## Macros de Template

### Badges

**Arquivo:** `templates/macros/badges.html`

Macros para renderizar badges com cores e estilos consistentes.

#### Importação

```jinja2
{% from 'macros/badges.html' import badge_status_chamado, badge_prioridade, badge_perfil, badge_mensagens_nao_lidas, badge, badge_booleano %}
```

#### Macros Disponíveis

##### `badge_status_chamado(status)`
Badge para status de chamados.

**Cores:**
- Aberto → `bg-primary` (azul)
- Em Análise → `bg-info` (ciano)
- Resolvido → `bg-success` (verde)
- Fechado → `bg-secondary` (cinza)

```jinja2
{{ badge_status_chamado(chamado.status) }}
```

##### `badge_prioridade(prioridade)`
Badge para prioridades.

**Cores:**
- Urgente → `bg-danger` (vermelho)
- Alta → `bg-warning` (amarelo)
- Média → `bg-info` (ciano)
- Baixa → `bg-secondary` (cinza)

```jinja2
{{ badge_prioridade(chamado.prioridade) }}
```

##### `badge_perfil(perfil)`
Badge para perfis de usuário.

**Cores:**
- Administrador → `bg-danger` (vermelho)
- Vendedor → `bg-warning` (amarelo)
- Cliente → `bg-info` (ciano)

```jinja2
{{ badge_perfil(usuario.perfil) }}
```

##### `badge_mensagens_nao_lidas(count)`
Badge para contador de mensagens não lidas (exibe apenas se count > 0).

```jinja2
{{ badge_mensagens_nao_lidas(chamado.mensagens_nao_lidas) }}
```

##### `badge(texto, cor='secondary', icon=none)`
Badge genérico customizável.

```jinja2
{{ badge('Novo', 'success', 'star-fill') }}
{{ badge('Pendente', 'warning') }}
```

##### `badge_booleano(valor, texto_true='Sim', texto_false='Não', cor_true='success', cor_false='secondary')`
Badge para valores booleanos.

```jinja2
{{ badge_booleano(usuario.ativo, 'Ativo', 'Inativo') }}
```

---

### Action Buttons

**Arquivo:** `templates/macros/action_buttons.html`

Macros para renderizar botões de ação com estilos e acessibilidade consistentes.

#### Importação

```jinja2
{% from 'macros/action_buttons.html' import btn_icon, btn_group_crud, btn_text, btn_voltar %}
```

#### Macros Disponíveis

##### `btn_group_crud(entity_id, entity_name, base_url, delete_function='', show_view=false, show_edit=true, show_delete=true, extra_buttons='', size='sm')`

Grupo de botões CRUD padrão.

**Exemplo básico:**
```jinja2
{{ btn_group_crud(
    usuario.id,
    'usuário ' ~ usuario.nome,
    '/admin/usuarios',
    "excluirUsuario(%d, '%s', '%s', '%s')" | format(
        usuario.id,
        usuario.nome|replace("'", "\\'"),
        usuario.email,
        usuario.perfil
    )
) }}
```

**Com botões extras:**
```jinja2
{{ btn_group_crud(
    chamado.id,
    'chamado #' ~ chamado.id,
    '/chamados',
    "excluirChamado(%d)" | format(chamado.id),
    extra_buttons=btn_icon('/chamados/' ~ chamado.id ~ '/mensagens', 'chat', 'info', 'Mensagens')
) }}
```

##### `btn_icon(url, icon, variant='primary', title='', aria_label='', size='sm', onclick='', extra_classes='')`

Botão com ícone (link ou button).

```jinja2
{{ btn_icon('/tarefas/editar/1', 'pencil', 'primary', 'Editar', size='md') }}
{{ btn_icon('#', 'trash', 'danger', 'Excluir', onclick='excluir(1)') }}
```

##### `btn_text(url, texto, icon='', variant='primary', size='md', onclick='', extra_classes='')`

Botão com texto e ícone opcional.

```jinja2
{{ btn_text('/tarefas/cadastrar', 'Nova Tarefa', 'plus-circle', 'success') }}
```

##### `btn_voltar(url, texto='Voltar', variant='secondary', size='md')`

Botão de voltar/cancelar padronizado.

```jinja2
{{ btn_voltar('/tarefas/listar') }}
{{ btn_voltar('/admin/usuarios/listar', 'Cancelar') }}
```

---

### Empty States

**Arquivo:** `templates/macros/empty_states.html`

Macros para renderizar mensagens de estado vazio.

#### Importação

```jinja2
{% from 'macros/empty_states.html' import empty_state, empty_search_result, empty_filtered_result, empty_permission_denied %}
```

#### Macros Disponíveis

##### `empty_state(title, message, action_url='', action_text='', icon='info-circle', variant='info', show_icon=true)`

Estado vazio genérico.

```jinja2
{{ empty_state(
    'Nenhuma tarefa cadastrada',
    'Você ainda não possui tarefas. Clique no botão abaixo para começar!',
    action_url='/tarefas/cadastrar',
    action_text='Cadastrar Primeira Tarefa',
    icon='clipboard-x'
) }}
```

##### `empty_search_result(search_term='', back_url='')`

Estado vazio para resultados de busca.

```jinja2
{{ empty_search_result('Python', '/tarefas/listar') }}
```

##### `empty_filtered_result(filter_description='', clear_url='')`

Estado vazio para listagens filtradas.

```jinja2
{{ empty_filtered_result('Status: Aberto', '/chamados/listar') }}
```

##### `empty_permission_denied(message='', back_url='')`

Estado para acesso negado.

```jinja2
{{ empty_permission_denied('Você não tem permissão para visualizar estes dados.', '/home') }}
```

---

## Helpers Backend

### Rate Limiting

**Arquivo:** `util/rate_limit_decorator.py`

Decorator para aplicar rate limiting de forma centralizada.

#### Importação

```python
from util.rate_limit_decorator import aplicar_rate_limit, aplicar_rate_limit_async
from util.rate_limiter import RateLimiter
```

#### Uso

**1. Criar limiter (nível de módulo):**

```python
tarefa_criar_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="tarefa_criar"
)
```

**2. Aplicar decorator:**

```python
@router.post("/cadastrar")
@aplicar_rate_limit(
    limiter=tarefa_criar_limiter,
    mensagem_erro="Muitas tentativas. Aguarde 1 minuto.",
    redirect_url="/tarefas/listar"
)
@requer_autenticacao()
async def post_cadastrar(request: Request, ...):
    # Lógica da rota SEM código de rate limiting
    pass
```

**Para APIs (retorna JSON):**

```python
@router.post("/api/tasks")
@aplicar_rate_limit_async(
    limiter=api_limiter,
    mensagem_erro="API rate limit exceeded"
)
async def create_task(request: Request, ...):
    pass
```

#### Benefícios

- ✅ Elimina ~100 linhas de código duplicado
- ✅ Logging automático de tentativas bloqueadas
- ✅ Flash messages automáticos
- ✅ Suporte a redirecionamento ou JSON

---

### Repository Helpers

**Arquivo:** `util/repository_helpers.py`

Funções auxiliares para operações comuns com repositórios.

#### Importação

```python
from util.repository_helpers import obter_ou_404, obter_lista_ou_vazia, validar_inteiro_positivo, executar_operacao_repo
```

#### Funções Disponíveis

##### `obter_ou_404(entity, request, mensagem, redirect_url, log_erro=True)`

Verifica se entidade existe e redireciona se não existir.

```python
@router.get("/editar/{id}")
@requer_autenticacao()
async def get_editar(request: Request, id: int, usuario_logado: dict):
    # Obter usuário ou retornar 404
    usuario = obter_ou_404(
        usuario_repo.obter_por_id(id),
        request,
        "Usuário não encontrado",
        "/admin/usuarios/listar"
    )
    if isinstance(usuario, RedirectResponse):
        return usuario

    # Usuario existe, pode usar
    return templates.TemplateResponse("editar.html", {...})
```

##### `obter_lista_ou_vazia(lista, request=None, mensagem_aviso=None, log_aviso=False)`

Garante que lista nunca seja None.

```python
tarefas = obter_lista_ou_vazia(
    tarefa_repo.obter_por_usuario(usuario_id),
    request,
    "Nenhuma tarefa encontrada"
)
# tarefas sempre será list, mesmo que vazia
```

##### `validar_inteiro_positivo(valor, request, nome_campo="ID", redirect_url="/")`

Valida IDs antes de passar para repository.

```python
id_valido = validar_inteiro_positivo(
    id,
    request,
    "ID do usuário",
    "/admin/usuarios/listar"
)
if isinstance(id_valido, RedirectResponse):
    return id_valido
```

##### `executar_operacao_repo(operacao, request, mensagem_erro, redirect_url, log_exception=True)`

Executa operação com tratamento de erros.

```python
resultado = executar_operacao_repo(
    lambda: usuario_repo.inserir(usuario),
    request,
    "Erro ao cadastrar usuário",
    "/admin/usuarios/listar"
)
if isinstance(resultado, RedirectResponse):
    return resultado
```

#### Benefícios

- ✅ Elimina ~60 linhas de código duplicado
- ✅ Tratamento de erros consistente
- ✅ Mensagens e logs padronizados

---

### Permission Helpers

**Arquivo:** `util/permission_helpers.py`

Funções para verificação de permissões e propriedade.

#### Importação

```python
from util.permission_helpers import verificar_propriedade, verificar_propriedade_ou_admin, verificar_perfil, verificar_multiplas_condicoes
```

#### Funções Disponíveis

##### `verificar_propriedade(entity, usuario_id, request, mensagem_erro, redirect_url, campo_usuario='usuario_id', log_tentativa=True)`

Verifica se usuário é proprietário da entidade.

```python
@router.post("/tarefas/excluir/{id}")
@requer_autenticacao()
async def post_excluir(request: Request, id: int, usuario_logado: dict):
    tarefa = obter_ou_404(...)
    if isinstance(tarefa, RedirectResponse):
        return tarefa

    # Verificar propriedade
    if not verificar_propriedade(
        tarefa,
        usuario_logado["id"],
        request,
        "Você não pode excluir esta tarefa",
        "/tarefas/listar"
    ):
        return RedirectResponse("/tarefas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Usuário é dono, pode excluir
    tarefa_repo.excluir(id)
```

##### `verificar_propriedade_ou_admin(entity, usuario_logado, request, mensagem_erro, redirect_url, campo_usuario='usuario_id', log_tentativa=True)`

Verifica se usuário é proprietário OU admin.

```python
# Admin pode editar qualquer recurso, dono também pode
if not verificar_propriedade_ou_admin(
    chamado,
    usuario_logado,
    request,
    "Você não pode editar este chamado",
    "/chamados/listar"
):
    return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)
```

##### `verificar_perfil(usuario_perfil, perfis_permitidos, request, mensagem_erro, redirect_url, log_tentativa=True)`

Verifica se perfil está na lista permitida.

```python
from util.perfis import Perfil

if not verificar_perfil(
    usuario_logado["perfil"],
    [Perfil.ADMIN.value, Perfil.VENDEDOR.value],
    request,
    "Apenas administradores e vendedores podem acessar",
    "/home"
):
    return RedirectResponse("/home", status_code=status.HTTP_303_SEE_OTHER)
```

**Nota:** Considere usar `@requer_autenticacao([perfis])` ao invés desta função.

##### `verificar_multiplas_condicoes(condicoes, request, mensagem_erro_padrao, redirect_url, operador='AND')`

Verifica múltiplas condições com operador lógico.

```python
# AND: todas devem passar
if not verificar_multiplas_condicoes([
    (chamado.usuario_id == usuario_logado["id"], "Não é seu chamado"),
    (chamado.status != "Fechado", "Chamado já está fechado")
], request, redirect_url="/chamados/listar"):
    return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

# OR: pelo menos uma deve passar
if not verificar_multiplas_condicoes([
    (tarefa.usuario_id == usuario_logado["id"], "Não é sua tarefa"),
    (usuario_logado["perfil"] == Perfil.ADMIN.value, "Não é administrador")
], request, redirect_url="/tarefas/listar", operador="OR"):
    return RedirectResponse("/tarefas/listar", status_code=status.HTTP_303_SEE_OTHER)
```

#### Benefícios

- ✅ Elimina ~30 linhas de código duplicado
- ✅ Verificações de segurança consistentes
- ✅ Logging automático de tentativas negadas

---

## Módulos JavaScript

### Delete Helpers

**Arquivo:** `static/js/delete-helpers.js`

Módulo para confirmação de exclusão com modal customizável.

**Já incluído em:** `templates/base_privada.html`

#### Funções Disponíveis

##### `confirmarExclusao(config)`

Função genérica para confirmação de exclusão.

**Parâmetros:**
- `id` (number): ID da entidade
- `nome` (string): Nome/identificador
- `urlBase` (string): URL base (ex: '/admin/usuarios')
- `entidade` (string): Nome da entidade (ex: 'usuário', 'tarefa')
- `camposDetalhes` (object): Campos a exibir no modal
- `mensagem` (string, opcional): Mensagem customizada
- `urlExclusao` (string, opcional): URL completa de exclusão

**Exemplo básico:**
```javascript
confirmarExclusao({
    id: 1,
    nome: 'João Silva',
    urlBase: '/admin/usuarios',
    entidade: 'usuário'
});
```

**Exemplo com detalhes:**
```javascript
confirmarExclusao({
    id: 1,
    nome: 'João Silva',
    urlBase: '/admin/usuarios',
    entidade: 'usuário',
    camposDetalhes: {
        'Nome': 'João Silva',
        'Email': 'joao@email.com',
        'Perfil': '<span class="badge bg-danger">Administrador</span>'
    }
});
```

##### Helpers Específicos

**`excluirUsuario(id, nome, email, perfil, urlBase='/admin/usuarios')`**

```javascript
excluirUsuario(1, 'João Silva', 'joao@email.com', 'Administrador');
```

**`excluirTarefa(id, titulo, status, urlBase='/tarefas')`**

```javascript
excluirTarefa(1, 'Implementar feature X', 'Pendente');
```

**`excluirChamado(id, titulo, status, prioridade, urlBase='/chamados')`**

```javascript
excluirChamado(1, 'Bug no login', 'Aberto', 'Alta');
```

#### Benefícios

- ✅ Elimina ~200 linhas de JavaScript duplicado
- ✅ Modais consistentes em todo o sistema
- ✅ Escape automático de HTML (segurança)
- ✅ Fácil customização de campos

---

## Resumo de Impacto

### Código Eliminado

- **Templates**: ~300 linhas (badges + buttons + empty states)
- **JavaScript**: ~200 linhas (delete confirmations)
- **Python Routes**: ~100 linhas (rate limiting)
- **Python Routes**: ~60 linhas (entity checks)
- **Total**: **~760 linhas** de código duplicado eliminadas

### Arquivos Criados

**Templates (3):**
- `templates/macros/badges.html`
- `templates/macros/action_buttons.html`
- `templates/macros/empty_states.html`

**JavaScript (1):**
- `static/js/delete-helpers.js`

**Python (3):**
- `util/rate_limit_decorator.py`
- `util/repository_helpers.py`
- `util/permission_helpers.py`

### Arquivos Migrados (Exemplos)

**Templates:**
- `templates/tarefas/listar.html`
- `templates/admin/usuarios/listar.html`
- `templates/chamados/listar.html`

**Rotas:**
- `routes/tarefas_routes.py`

---

## Próximos Passos

Para migrar código existente para usar estes componentes, consulte `docs/GUIA_MIGRACAO.md`.

Para adicionar novos CRUDs, todos os componentes já estão disponíveis para uso imediato!
