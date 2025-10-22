# Convenções de Frontend - DefaultWebApp

Este documento define os padrões e convenções para o desenvolvimento frontend da aplicação, garantindo consistência visual e manutenibilidade do código.

---

## 📋 Índice

- [Bootstrap 5.3.8](#bootstrap-538)
- [Padrões de Espaçamento](#padrões-de-espaçamento)
- [Padrões de Grid](#padrões-de-grid)
- [Padrões de Cards](#padrões-de-cards)
- [Padrões de Formulários](#padrões-de-formulários)
- [Padrões de Tabelas](#padrões-de-tabelas)
- [Padrões de Botões](#padrões-de-botões)
- [Padrões de Modais](#padrões-de-modais)
- [Acessibilidade](#acessibilidade)
- [JavaScript](#javascript)
- [CSS Customizado](#css-customizado)

---

## 🎨 Bootstrap 5.3.8

### Framework Base

A aplicação utiliza **Bootstrap 5.3.8** como framework CSS principal.

**Carregamento:**
```html
<!-- Bootstrap CSS (local - permite troca de temas) -->
<link href="/static/css/bootstrap.min.css" rel="stylesheet">

<!-- Bootstrap Icons (CDN) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css">

<!-- Bootstrap JS Bundle (CDN) -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
```

### Temas Bootswatch

A aplicação suporta 28+ temas via Bootswatch (armazenados em `static/css/bootswatch/`).

**Temas disponíveis:**
- **Light**: Cerulean, Cosmo, Flatly, Journal, Litera, Lumen, Minty, Pulse, Sandstone, Simplex, United, Yeti, Zephyr, Brite, Morph, Quartz, Spacelab
- **Dark**: Cyborg, Darkly, Slate, Solar, Superhero, Vapor
- **Unique**: Lux, Materia, Sketchy

**Preview**: `/exemplos/bootswatch`

---

## 📏 Padrões de Espaçamento

### Margens Verticais

**Convenção**: Sempre usar `mb-3` (margin-bottom) para espaçamento vertical consistente.

```html
<!-- ✅ CORRETO -->
<div class="mb-3">
    <label>Nome</label>
    <input type="text" class="form-control">
</div>

<div class="mb-3">
    <label>Email</label>
    <input type="email" class="form-control">
</div>

<!-- ❌ EVITAR - inconsistente -->
<div class="mb-2">...</div>
<div class="mb-4">...</div>
<div>...</div>  <!-- Sem margem -->
```

### Exceções

**Cards**: Use `mb-4` para separação maior entre cards
```html
<div class="card mb-4">...</div>
```

**Seções**: Use `mb-5` para separação entre seções principais
```html
<section class="mb-5">...</section>
```

**Último elemento**: Use `mb-0` para remover margem do último elemento
```html
<div class="card-body">
    <p class="mb-3">Parágrafo 1</p>
    <p class="mb-0">Último parágrafo</p>
</div>
```

### Padding

**Containers**: Sempre usar padding padrão do Bootstrap
```html
<!-- ✅ CORRETO -->
<div class="container">...</div>

<!-- ❌ EVITAR -->
<div class="container" style="padding: 20px;">...</div>
```

---

## 📐 Padrões de Grid

### Mobile-First

**SEMPRE especificar `col-12` primeiro** e depois breakpoints maiores.

```html
<!-- ✅ CORRETO - Mobile first -->
<div class="row">
    <div class="col-12 col-md-6 col-lg-4">Item 1</div>
    <div class="col-12 col-md-6 col-lg-4">Item 2</div>
    <div class="col-12 col-md-6 col-lg-4">Item 3</div>
</div>

<!-- ❌ EVITAR - sem mobile -->
<div class="row">
    <div class="col-md-6">Item 1</div>
    <div class="col-md-6">Item 2</div>
</div>
```

### Breakpoints

| Breakpoint | Class | Viewport | Uso |
|------------|-------|----------|-----|
| Extra small | `col-*` | <576px | Mobile (padrão) |
| Small | `col-sm-*` | ≥576px | Mobile landscape |
| Medium | `col-md-*` | ≥768px | Tablets |
| Large | `col-lg-*` | ≥992px | Desktops |
| Extra large | `col-xl-*` | ≥1200px | Large desktops |
| Extra extra large | `col-xxl-*` | ≥1400px | Extra large screens |

### Espaçamento no Grid

```html
<!-- Com gutters (padrão) -->
<div class="row">
    <div class="col-12 col-md-6">...</div>
</div>

<!-- Sem gutters -->
<div class="row g-0">
    <div class="col-12 col-md-6">...</div>
</div>

<!-- Gutters customizados -->
<div class="row g-3">  <!-- gap de 1rem -->
    <div class="col-12 col-md-6">...</div>
</div>
```

---

## 🎴 Padrões de Cards

### Estrutura Básica

```html
<div class="card shadow-sm mb-4">
    <div class="card-header">
        <h5 class="card-title mb-0">Título do Card</h5>
    </div>
    <div class="card-body">
        <p class="card-text">Conteúdo do card...</p>
    </div>
    <div class="card-footer text-muted">
        Rodapé (opcional)
    </div>
</div>
```

### Shadow

**Convenção**: Use `shadow-sm` para cards regulares.

```html
<!-- ✅ CORRETO - Sombra sutil -->
<div class="card shadow-sm">...</div>

<!-- ⚠️ USO ESPECÍFICO - Apenas em landing pages/destaques -->
<div class="card shadow">...</div>

<!-- ❌ EVITAR - Muito forte -->
<div class="card shadow-lg">...</div>
```

### Cards com Imagem

```html
<div class="card shadow-sm">
    <img src="..." class="card-img-top" alt="Descrição da imagem">
    <div class="card-body">
        <h5 class="card-title">Título</h5>
        <p class="card-text">Texto do card</p>
        <a href="#" class="btn btn-primary">Ação</a>
    </div>
</div>
```

### Grid de Cards

```html
<div class="row">
    <div class="col-12 col-md-6 col-lg-4 mb-4">
        <div class="card shadow-sm h-100">
            <!-- Conteúdo -->
        </div>
    </div>
    <!-- Mais cards... -->
</div>
```

**Nota**: Use `h-100` para cards de altura igual.

---

## 📝 Padrões de Formulários

### Uso de Macros

**SEMPRE use macros** de `macros/form_fields.html` para campos de formulário.

```html
{% from 'macros/form_fields.html' import input_text, input_email, input_password, select %}

<!-- ✅ CORRETO - Usando macro -->
{{ input_text(
    name='nome',
    label='Nome Completo',
    value=dados.nome if dados else '',
    required=true,
    erro=erros.nome if erros else None
) }}

<!-- ❌ EVITAR - HTML manual -->
<div class="mb-3">
    <label for="nome" class="form-label">Nome</label>
    <input type="text" class="form-control" id="nome" name="nome">
</div>
```

### Estrutura de Form

```html
<form method="POST" action="/rota">
    <div class="mb-3">
        {{ input_text(...) }}
    </div>

    <div class="mb-3">
        {{ input_email(...) }}
    </div>

    <div class="d-grid gap-2">
        <button type="submit" class="btn btn-primary">
            <i class="bi bi-check-circle"></i> Salvar
        </button>
    </div>
</form>
```

### Error Display

Erros são exibidos automaticamente pelos macros:

```html
<!-- Erro de campo específico -->
{{ input_text(name='email', erro=erros.email) }}

<!-- Erro geral do formulário -->
{% if erros.geral %}
<div class="alert alert-danger" role="alert">
    <i class="bi bi-exclamation-triangle"></i> {{ erros.geral }}
</div>
{% endif %}
```

---

## 📊 Padrões de Tabelas

### Estrutura Básica

```html
<div class="table-responsive">
    <table class="table table-hover">
        <thead>
            <tr>
                <th scope="col">Nome</th>
                <th scope="col">Email</th>
                <th scope="col" class="text-end">Ações</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>João Silva</td>
                <td>joao@example.com</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-primary">
                        <i class="bi bi-pencil"></i>
                    </button>
                </td>
            </tr>
        </tbody>
    </table>
</div>
```

### Convenções Importantes

1. **SEMPRE use `scope="col"`** em headers (`<th>`)
2. **SEMPRE envolva em `div.table-responsive`** para mobile
3. **Use `table-hover`** para feedback visual
4. **Alinhe ações à direita** com `text-end`

### Variações

```html
<!-- Tabela striped (zebra) -->
<table class="table table-striped">...</table>

<!-- Tabela bordered -->
<table class="table table-bordered">...</table>

<!-- Tabela small (compacta) -->
<table class="table table-sm">...</table>

<!-- Combinação -->
<table class="table table-hover table-striped">...</table>
```

### Badges em Tabelas

```html
<td>
    {% if usuario.ativo %}
        <span class="badge bg-success">Ativo</span>
    {% else %}
        <span class="badge bg-danger">Inativo</span>
    {% endif %}
</td>
```

---

## 🔘 Padrões de Botões

### Cores e Contextos

```html
<!-- Primário - Ação principal -->
<button class="btn btn-primary">Salvar</button>

<!-- Secundário - Ação alternativa -->
<button class="btn btn-secondary">Cancelar</button>

<!-- Sucesso - Confirmações -->
<button class="btn btn-success">Confirmar</button>

<!-- Perigo - Ações destrutivas -->
<button class="btn btn-danger">Excluir</button>

<!-- Warning - Atenção -->
<button class="btn btn-warning">Restaurar</button>

<!-- Info - Informações -->
<button class="btn btn-info">Detalhes</button>
```

### Tamanhos

```html
<!-- Grande -->
<button class="btn btn-primary btn-lg">Grande</button>

<!-- Normal (padrão) -->
<button class="btn btn-primary">Normal</button>

<!-- Pequeno -->
<button class="btn btn-primary btn-sm">Pequeno</button>
```

### Botões com Ícones

**Sempre inclua ícone antes do texto** para melhor UX:

```html
<!-- ✅ CORRETO -->
<button class="btn btn-primary">
    <i class="bi bi-plus-circle"></i> Novo
</button>

<button class="btn btn-danger">
    <i class="bi bi-trash"></i> Excluir
</button>

<!-- ⚠️ Icon-only - SEMPRE adicionar aria-label -->
<button class="btn btn-primary btn-sm" aria-label="Editar">
    <i class="bi bi-pencil"></i>
</button>
```

### Botões Full-Width

```html
<div class="d-grid gap-2">
    <button class="btn btn-primary">Botão Full Width</button>
</div>
```

### Grupos de Botões

```html
<div class="btn-group" role="group" aria-label="Ações">
    <button class="btn btn-outline-primary">
        <i class="bi bi-eye"></i> Ver
    </button>
    <button class="btn btn-outline-primary">
        <i class="bi bi-pencil"></i> Editar
    </button>
    <button class="btn btn-outline-danger">
        <i class="bi bi-trash"></i> Excluir
    </button>
</div>
```

---

## 🪟 Padrões de Modais

### Uso de Componentes

**SEMPRE use componentes reutilizáveis** em vez de criar modais customizados:

```html
<!-- Confirmação de ação -->
{% include 'components/modal_confirmacao.html' %}

<!-- Alerta -->
{% include 'components/modal_alerta.html' %}

<!-- Corte de imagem -->
{% include 'components/modal_corte_imagem.html' %}
```

### Invocação via JavaScript

```javascript
// Modal de confirmação
abrirModalConfirmacao({
    url: '/rota/excluir/123',
    mensagem: 'Tem certeza que deseja excluir?',
    detalhes: 'Esta ação não pode ser desfeita.',
    tipo: 'danger'  // ou 'warning'
});

// Modal de alerta
exibirErro('Ocorreu um erro ao processar a solicitação.');
exibirSucesso('Operação realizada com sucesso!');
exibirAviso('Atenção: esta ação requer cuidado.');
```

### Estrutura (apenas se necessário criar custom)

```html
<div class="modal fade" id="meuModal" tabindex="-1" aria-labelledby="meuModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="meuModalLabel">Título</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>
            </div>
            <div class="modal-body">
                Conteúdo do modal
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <button type="button" class="btn btn-primary">Confirmar</button>
            </div>
        </div>
    </div>
</div>
```

---

## ♿ Acessibilidade

### Princípios Fundamentais

1. **Semantic HTML** - Use tags apropriadas (`<nav>`, `<main>`, `<article>`, etc.)
2. **Keyboard Navigation** - Todos elementos interativos acessíveis via teclado
3. **Screen Reader Support** - ARIA labels e roles apropriados
4. **Color Contrast** - Seguir WCAG 2.1 AA (4.5:1 para texto normal)

### Tabelas

**SEMPRE use `scope` em headers:**

```html
<!-- ✅ CORRETO -->
<thead>
    <tr>
        <th scope="col">Nome</th>
        <th scope="col">Email</th>
    </tr>
</thead>

<!-- ❌ ERRADO -->
<thead>
    <tr>
        <th>Nome</th>
        <th>Email</th>
    </tr>
</thead>
```

### Botões Icon-Only

**SEMPRE adicione `aria-label`:**

```html
<!-- ✅ CORRETO -->
<button class="btn btn-sm btn-primary" aria-label="Editar usuário">
    <i class="bi bi-pencil"></i>
</button>

<!-- ❌ ERRADO - Screen reader não sabe o que faz -->
<button class="btn btn-sm btn-primary">
    <i class="bi bi-pencil"></i>
</button>
```

### Formulários

**SEMPRE associe labels com inputs:**

```html
<!-- ✅ CORRETO - label com for -->
<label for="email" class="form-label">Email</label>
<input type="email" class="form-control" id="email" name="email">

<!-- ⚠️ ACEITÁVEL - label wrapper -->
<label class="form-label">
    Email
    <input type="email" class="form-control" name="email">
</label>

<!-- ❌ ERRADO - sem associação -->
<label class="form-label">Email</label>
<input type="email" class="form-control" name="email">
```

### Imagens

**SEMPRE adicione `alt` text:**

```html
<!-- ✅ CORRETO - alt descritivo -->
<img src="/static/img/logo.png" alt="Logo do Sistema WebApp">

<!-- ✅ CORRETO - alt vazio para imagem decorativa -->
<img src="/static/img/decoracao.png" alt="">

<!-- ❌ ERRADO - sem alt -->
<img src="/static/img/logo.png">
```

### Links

**Links devem ter texto descritivo:**

```html
<!-- ✅ CORRETO -->
<a href="/sobre">Saiba mais sobre nossos serviços</a>

<!-- ❌ EVITAR -->
<a href="/sobre">Clique aqui</a>
```

### Modais

**SEMPRE use atributos ARIA:**

```html
<div class="modal fade"
     id="meuModal"
     tabindex="-1"
     aria-labelledby="meuModalLabel"
     aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="meuModalLabel">Título</h5>
                <button type="button"
                        class="btn-close"
                        data-bs-dismiss="modal"
                        aria-label="Fechar"></button>
            </div>
            <!-- ... -->
        </div>
    </div>
</div>
```

---

## 💻 JavaScript

### Organização

**NUNCA use inline scripts para lógica complexa:**

```html
<!-- ❌ EVITAR -->
<button onclick="excluirUsuario(123)">Excluir</button>

<!-- ✅ CORRETO -->
<button class="btn-excluir" data-usuario-id="123">Excluir</button>

<script src="/static/js/usuarios.js"></script>
```

### Event Delegation

```javascript
// ✅ CORRETO - Event delegation
document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(e) {
        if (e.target.matches('.btn-excluir')) {
            const usuarioId = e.target.dataset.usuarioId;
            excluirUsuario(usuarioId);
        }
    });
});
```

### Modules Disponíveis

```javascript
// Toasts
exibirToast('Mensagem', 'success');

// Modal de alerta
exibirErro('Erro!');
exibirSucesso('Sucesso!');
exibirAviso('Atenção!');

// Modal de confirmação
abrirModalConfirmacao({...});

// Input masks
InputMask.MASKS.CPF
InputMask.MASKS.TELEFONE
DecimalMask.format(1234.56)

// Password validator
new PasswordValidator(inputSenha, inputConfirma);
```

---

## 🎨 CSS Customizado

### Arquivo

Estilos customizados em: `static/css/custom.css`

### Convenções

1. **Use classes utilitárias do Bootstrap** quando possível
2. **Crie classes custom apenas quando necessário**
3. **Prefixe classes custom com `.custom-`**
4. **Documente classes custom**

```css
/* ✅ CORRETO - Classe custom documentada */
/**
 * Card de destaque na homepage
 * Usado em: templates/index.html
 */
.custom-hero-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

/* ❌ EVITAR - Classe genérica sem contexto */
.box {
    padding: 20px;
}
```

### Prioridade

1. **Primeiro**: Classes utilitárias Bootstrap
2. **Segundo**: Classes de componentes Bootstrap
3. **Terceiro**: Classes custom (com prefixo)
4. **Último**: Inline styles (apenas quando absolutamente necessário)

---

## 📱 Responsividade

### Testes Obrigatórios

Sempre testar em:
- 📱 Mobile (375px - iPhone SE)
- 📱 Mobile Large (414px - iPhone Pro Max)
- 📱 Tablet (768px - iPad)
- 💻 Desktop (1024px+)

### Breakpoints Comuns

```html
<!-- 2 colunas em tablet, 3 em desktop -->
<div class="col-12 col-md-6 col-lg-4">...</div>

<!-- 1 coluna em mobile, 2 em tablet+ -->
<div class="col-12 col-md-6">...</div>

<!-- Full width em mobile, metade em desktop -->
<div class="col-12 col-lg-6">...</div>
```

### Utilitários de Display

```html
<!-- Ocultar em mobile, mostrar em desktop -->
<div class="d-none d-lg-block">...</div>

<!-- Mostrar em mobile, ocultar em desktop -->
<div class="d-block d-lg-none">...</div>
```

---

## ✅ Checklist de Qualidade

Antes de fazer commit de um template novo/modificado:

- [ ] Usa macros para campos de formulário
- [ ] Tabelas têm `scope="col"` em headers
- [ ] Botões icon-only têm `aria-label`
- [ ] Imagens têm `alt` text apropriado
- [ ] Labels associados corretamente com inputs
- [ ] Grid usa mobile-first (`col-12` primeiro)
- [ ] Cards usam `shadow-sm`
- [ ] Espaçamento consistente (`mb-3` padrão)
- [ ] Sem inline styles (exceto quando estritamente necessário)
- [ ] Sem inline scripts complexos
- [ ] Testado em mobile e desktop
- [ ] Sem erros no console do navegador

---

## 📚 Referências

- **Bootstrap 5.3.8 Docs**: https://getbootstrap.com/docs/5.3/
- **Bootstrap Icons**: https://icons.getbootstrap.com/
- **Bootswatch Themes**: https://bootswatch.com/
- **WCAG 2.1**: https://www.w3.org/WAI/WCAG21/quickref/
- **MDN Accessibility**: https://developer.mozilla.org/en-US/docs/Web/Accessibility

---

**Última atualização**: 2025-10-22
**Versão**: 1.0
**Mantenedor**: Equipe de Desenvolvimento
