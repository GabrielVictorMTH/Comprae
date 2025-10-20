# ANÁLISE INICIAL DO PROJETO COMPRAÊ

## 1. RESUMO EXECUTIVO

Este documento apresenta uma análise detalhada do estado atual do projeto **Compraê** e identifica todas as implementações necessárias para transformá-lo na solução descrita no documento de especificação (docs/Compraê.pdf).

- **Data da Análise:** 20/10/2025
- **Versão do Projeto:** Em desenvolvimento
- **Stack Tecnológico:** Python 3.12 + FastAPI + Jinja2 + Supabase (SQLite local) + Bootstrap 5

---

## 2. VISÃO GERAL DA SOLUÇÃO PROPOSTA

O **Compraê** é uma plataforma de e-commerce regional que visa conectar pequenos comerciantes, produtores locais e prestadores de serviços diretamente aos consumidores de uma mesma região. A plataforma oferece:

### 2.1. Funcionalidades Core
- **Marketplace:** Catálogo de produtos com busca e filtros
- **Gestão de Anúncios:** Vendedores podem cadastrar e gerenciar produtos
- **Sistema de Pedidos:** Fluxo completo de compra e venda
- **Avaliações:** Sistema de feedback entre compradores e vendedores
- **Mensagens:** Comunicação direta entre usuários
- **Multi-perfil:** Anônimo, Usuário, Comprador, Vendedor e Administrador

### 2.2. Modelo de Negócio
- Plano Gratuito: até 10 produtos
- Plano Intermediário (R$ 44/mês): até 50 produtos + domínio próprio + 3 autores
- Plano Avançado (R$ 59/mês): produtos ilimitados + 15 autores + recursos premium

---

## 3. ESTADO ATUAL DO PROJETO

### 3.1. ESTRUTURA IMPLEMENTADA

#### 3.1.1. Models (Entidades) ✅
Todos os models necessários **JÁ ESTÃO CRIADOS**:
- ✅ `Usuario` - model/usuario_model.py
- ✅ `Categoria` - model/categoria_model.py
- ✅ `Anuncio` - model/anuncio_model.py
- ✅ `Pedido` - model/pedido_model.py
- ✅ `Endereco` - model/endereco_model.py
- ✅ `Mensagem` - model/mensagem_model.py
- ✅ `Configuracao` - model/configuracao_model.py
- ✅ `Tarefa` - model/tarefa_model.py (exemplo de referência)

#### 3.1.2. Repositórios Implementados ⚠️
**Existentes:**
- ✅ `usuario_repo` - repo/usuario_repo.py
- ✅ `configuracao_repo` - repo/configuracao_repo.py
- ✅ `tarefa_repo` - repo/tarefa_repo.py

**Faltam:**
- ❌ `categoria_repo`
- ❌ `anuncio_repo`
- ❌ `pedido_repo`
- ❌ `endereco_repo`
- ❌ `mensagem_repo`

#### 3.1.3. SQL (Queries) ⚠️
**Existentes:**
- ✅ `usuario_sql` - sql/usuario_sql.py
- ✅ `configuracao_sql` - sql/configuracao_sql.py
- ✅ `tarefa_sql` - sql/tarefa_sql.py

**Faltam:**
- ❌ `categoria_sql`
- ❌ `anuncio_sql`
- ❌ `pedido_sql`
- ❌ `endereco_sql`
- ❌ `mensagem_sql`

#### 3.1.4. DTOs (Data Transfer Objects) ⚠️
**Existentes:**
- ✅ `auth_dto` - dtos/auth_dto.py
- ✅ `usuario_dto` - dtos/usuario_dto.py
- ✅ `perfil_dto` - dtos/perfil_dto.py
- ✅ `tarefa_dto` - dtos/tarefa_dto.py
- ✅ `validators` - dtos/validators.py

**Faltam:**
- ❌ `categoria_dto`
- ❌ `anuncio_dto`
- ❌ `pedido_dto`
- ❌ `endereco_dto`
- ❌ `mensagem_dto`

#### 3.1.5. Rotas (Routes) ⚠️
**Existentes:**
- ✅ `auth_routes` - Autenticação (login, cadastro, redefinir senha)
- ✅ `usuario_routes` - Operações de usuário
- ✅ `perfil_routes` - Gerenciamento de perfil
- ✅ `admin_usuarios_routes` - Admin: gerenciar usuários
- ✅ `admin_configuracoes_routes` - Admin: configurações do sistema
- ✅ `public_routes` - Rotas públicas (home, sobre)
- ✅ `tarefas_routes` - Exemplo de CRUD completo
- ✅ `examples_routes` - Exemplos de UI

**Faltam:**
- ❌ `catalogo_routes` - Catálogo público de produtos
- ❌ `anuncio_routes` - Gerenciar anúncios (vendedor)
- ❌ `categoria_routes` - Gerenciar categorias (admin/vendedor)
- ❌ `pedido_routes` - Gerenciar pedidos (comprador/vendedor)
- ❌ `endereco_routes` - Gerenciar endereços (usuário)
- ❌ `mensagem_routes` - Sistema de mensagens
- ❌ `carrinho_routes` - Carrinho de compras
- ❌ `admin_categorias_routes` - Admin: gerenciar categorias
- ❌ `admin_anuncios_routes` - Admin: moderar anúncios

#### 3.1.6. Templates (Views) ⚠️
**Existentes:**
- ✅ Base templates (base_publica.html, base_privada.html)
- ✅ Auth templates (login, cadastro, redefinir senha)
- ✅ Perfil templates (visualizar, editar, alterar senha)
- ✅ Admin templates (usuários, configurações)
- ✅ Tarefas templates (exemplo de referência)
- ✅ Examples templates (vários exemplos de UI)
- ✅ Components (modais, galeria de fotos, form fields)

**Faltam:**
- ❌ templates/catalogo/ (listagem de produtos, detalhes, busca)
- ❌ templates/anuncio/ (criar, editar, listar vendedor)
- ❌ templates/categoria/ (gerenciar categorias)
- ❌ templates/pedido/ (listar, detalhes, histórico)
- ❌ templates/endereco/ (cadastrar, listar, editar)
- ❌ templates/mensagem/ (caixa de entrada, enviar, conversa)
- ❌ templates/carrinho/ (visualizar carrinho, checkout)
- ❌ templates/admin/categorias/
- ❌ templates/admin/anuncios/

### 3.2. INFRAESTRUTURA E UTILITÁRIOS ✅

**Todos os utilitários necessários já existem:**
- ✅ `auth_decorator` - Decorador de autenticação com suporte a perfis
- ✅ `db_util` - Gerenciamento de conexão com banco de dados
- ✅ `foto_util` - Upload e manipulação de imagens
- ✅ `flash_messages` - Sistema de mensagens temporárias
- ✅ `security` - Funções de segurança
- ✅ `senha_util` - Hash e validação de senhas
- ✅ `email_service` - Envio de e-mails
- ✅ `template_util` - Helper para templates
- ✅ `logger_config` - Configuração de logs
- ✅ `perfis` - Enum de perfis de usuário

---

## 4. ANÁLISE DE GAPS (O QUE FALTA)

### 4.1. MODELS - AJUSTES NECESSÁRIOS

#### 4.1.1. Usuario Model ⚠️
**Campos faltantes no banco:**
- ❌ `data_nascimento` (DATE)
- ❌ `numero_documento` (VARCHAR) - CPF/CNPJ
- ❌ `telefone` (VARCHAR)
- ❌ `confirmado` (BOOLEAN) - Para confirmação de e-mail

**Campos existentes:**
- ✅ id, nome, email, senha, perfil
- ✅ token_redefinicao, data_token, data_cadastro

#### 4.1.2. Perfis de Usuário ⚠️
**Arquivo:** util/perfis.py

Atualmente possui:
- ✅ ADMIN
- ✅ CLIENTE

**Falta adicionar:**
- ❌ VENDEDOR

#### 4.1.3. Anuncio Model ⚠️
**Problemas identificados:**
- ⚠️ Typo: `discricao` → deve ser `descricao`
- ⚠️ Tipo do campo `estoque`: está como `str`, deveria ser `int`
- ⚠️ Tipo do campo `peso`: está como `str`, deveria ser `float`
- ⚠️ Falta campo para múltiplas imagens (atualmente não modelado)

#### 4.1.4. Pedido Model ⚠️
**Problemas identificados:**
- ⚠️ Campos datetime podem ser `Optional` (nem todos são preenchidos imediatamente)
- ⚠️ Campo `status` deveria ter um Enum definido
- ⚠️ Falta relacionamento com quantidade (um pedido pode ter apenas 1 item)

### 4.2. FUNCIONALIDADES A IMPLEMENTAR

#### 4.2.1. Módulo de Catálogo (Público) - ALTA PRIORIDADE
**RF3: Visualizar catálogo de produtos**

**Arquivos a criar:**
1. `repo/anuncio_repo.py` - CRUD de anúncios
2. `sql/anuncio_sql.py` - Queries SQL
3. `routes/catalogo_routes.py` - Rotas públicas do catálogo
4. `templates/catalogo/` - Templates de visualização

**Funcionalidades:**
- Listar produtos ativos com paginação
- Busca por nome/descrição
- Filtros por categoria e localização
- Detalhes do produto
- Adicionar ao carrinho (para anônimos e autenticados)

#### 4.2.2. Módulo de Anúncios (Vendedor) - ALTA PRIORIDADE
**RF7: Gerenciar produtos (vendedor)**

**Arquivos a criar:**
1. `dtos/anuncio_dto.py` - Validações de entrada
2. `routes/anuncio_routes.py` - CRUD de anúncios (vendedor)
3. `templates/anuncio/` - Templates de gerenciamento

**Funcionalidades:**
- Cadastrar novo anúncio
- Editar anúncio existente
- Excluir anúncio (com confirmação)
- Upload de múltiplas imagens
- Listar meus anúncios
- Ativar/desativar anúncio

#### 4.2.3. Módulo de Categorias - ALTA PRIORIDADE
**RF8: Gerenciar categorias (admin/vendedor)**

**Arquivos a criar:**
1. `repo/categoria_repo.py`
2. `sql/categoria_sql.py`
3. `dtos/categoria_dto.py`
4. `routes/categoria_routes.py`
5. `routes/admin_categorias_routes.py`
6. `templates/categoria/`
7. `templates/admin/categorias/`

**Funcionalidades:**
- Admin: criar, editar, excluir categorias
- Vendedor: visualizar categorias para uso
- Listar todas as categorias

#### 4.2.4. Módulo de Pedidos - ALTA PRIORIDADE
**RF4: Realizar pedido (comprador)**
**RF5: Consultar pedidos (comprador)**
**RF6: Gerenciar pedidos (vendedor)**

**Arquivos a criar:**
1. `repo/pedido_repo.py`
2. `sql/pedido_sql.py`
3. `dtos/pedido_dto.py`
4. `routes/pedido_routes.py`
5. `routes/carrinho_routes.py`
6. `templates/pedido/`
7. `templates/carrinho/`

**Funcionalidades:**
- **Comprador:**
  - Adicionar produtos ao carrinho
  - Visualizar carrinho
  - Finalizar pedido (escolher endereço)
  - Ver histórico de pedidos
  - Ver detalhes do pedido
  - Avaliar vendedor após recebimento

- **Vendedor:**
  - Ver pedidos recebidos
  - Atualizar status do pedido
  - Adicionar código de rastreio
  - Ver histórico de vendas

#### 4.2.5. Módulo de Endereços - MÉDIA PRIORIDADE
**RF11: Gerenciar endereços**

**Arquivos a criar:**
1. `repo/endereco_repo.py`
2. `sql/endereco_sql.py`
3. `dtos/endereco_dto.py`
4. `routes/endereco_routes.py`
5. `templates/endereco/`

**Funcionalidades:**
- Cadastrar novo endereço
- Listar meus endereços
- Editar endereço
- Excluir endereço
- Marcar endereço como padrão

#### 4.2.6. Módulo de Mensagens - MÉDIA PRIORIDADE
**Comunicação entre usuários**

**Arquivos a criar:**
1. `repo/mensagem_repo.py`
2. `sql/mensagem_sql.py`
3. `dtos/mensagem_dto.py`
4. `routes/mensagem_routes.py`
5. `templates/mensagem/`

**Funcionalidades:**
- Enviar mensagem para vendedor (sobre um produto)
- Listar conversas
- Ver detalhes da conversa
- Marcar como lida
- Notificação de novas mensagens

#### 4.2.7. Módulo Admin - Moderação - BAIXA PRIORIDADE
**RF16: Moderar conteúdo**

**Arquivos a criar:**
1. `routes/admin_anuncios_routes.py`
2. `templates/admin/anuncios/`

**Funcionalidades:**
- Listar todos os anúncios
- Aprovar/reprovar anúncios
- Desativar anúncios inadequados
- Ver relatórios de vendas

---

## 5. ANÁLISE DE REQUISITOS

### 5.1. REQUISITOS FUNCIONAIS - STATUS

#### Alta Prioridade (Obrigatório)

| ID | Requisito | Status | Observações |
|----|-----------|--------|-------------|
| RF1 | Login, redefinir senha | ✅ COMPLETO | Implementado em auth_routes |
| RF2 | Cadastro de usuários | ✅ COMPLETO | Implementado em auth_routes |
| RF3 | Catálogo de produtos | ❌ FALTA | Precisa criar catalogo_routes |
| RF4 | Realizar compra | ❌ FALTA | Precisa criar pedido_routes e carrinho_routes |
| RF5 | Consultar pedidos (cliente) | ❌ FALTA | Precisa criar pedido_routes |
| RF6 | Consultar pedidos (vendedor) | ❌ FALTA | Precisa criar pedido_routes |
| RF7 | Gerenciar produtos | ❌ FALTA | Precisa criar anuncio_routes |
| RF8 | Gerenciar categorias | ❌ FALTA | Precisa criar categoria_routes |

#### Média Prioridade

| ID | Requisito | Status | Observações |
|----|-----------|--------|-------------|
| RF9 | Cancelar pedido | ❌ FALTA | Adicionar em pedido_routes |
| RF10 | Acompanhar status pedido | ❌ FALTA | Adicionar em pedido_routes |
| RF11 | Alterar dados perfil | ✅ COMPLETO | Implementado em perfil_routes |
| RF12 | Alterar senha | ✅ COMPLETO | Implementado em perfil_routes |

#### Baixa Prioridade

| ID | Requisito | Status | Observações |
|----|-----------|--------|-------------|
| RF13 | Notificações automáticas | ⚠️ PARCIAL | email_service existe, falta integrar |
| RF14 | Relatórios de vendas | ❌ FALTA | Nova funcionalidade |
| RF15 | Busca avançada | ❌ FALTA | Adicionar em catalogo_routes |
| RF16 | Moderação de conteúdo | ❌ FALTA | admin_anuncios_routes |

### 5.2. REQUISITOS NÃO-FUNCIONAIS - STATUS

| ID | Requisito | Status | Observações |
|----|-----------|--------|-------------|
| RNF1 | Segurança (auth/autorização) | ✅ COMPLETO | auth_decorator implementado |
| RNF2 | LGPD | ⚠️ PARCIAL | Implementar termo de uso e política |
| RNF3 | Compatibilidade navegadores | ✅ COMPLETO | Bootstrap 5 garante |
| RNF4 | Responsividade | ✅ COMPLETO | Bootstrap 5 garante |
| RNF5 | Desempenho (<2s) | ✅ COMPLETO | FastAPI é rápido |
| RNF6 | Capacidade (dezenas usuários) | ✅ COMPLETO | SQLite suporta |
| RNF7 | Confiabilidade | ⚠️ PARCIAL | Implementar backups |
| RNF8 | Manutenibilidade | ✅ COMPLETO | Código bem estruturado |
| RNF9 | Usabilidade | ✅ COMPLETO | Templates Bootstrap |
| RNF10 | Testabilidade | ⚠️ PARCIAL | Testes existem, ampliar cobertura |
| RNF11 | Backup | ❌ FALTA | Implementar rotina de backup |
| RNF12 | Logs | ✅ COMPLETO | logger_config implementado |
| RNF13 | Criptografia | ✅ COMPLETO | Senhas com bcrypt |
| RNF14 | Histórico de ações | ❌ FALTA | Implementar auditoria |
| RNF15 | Compressão | ✅ COMPLETO | FastAPI faz automaticamente |
| RNF16 | APIs futuras | ⚠️ PLANEJADO | FastAPI já expõe APIs |

---

## 6. PADRÕES DO PROJETO A SEGUIR

O projeto segue padrões bem definidos que **DEVEM SER MANTIDOS**:

### 6.1. Arquitetura em Camadas
```
Model (dataclasses) → SQL (queries) → Repo (DAL) → DTO (validation) → Routes (controllers) → Templates (views)
```

### 6.2. Nomenclatura de Arquivos
- Models: `{entidade}_model.py`
- Repositórios: `{entidade}_repo.py`
- SQL: `{entidade}_sql.py`
- DTOs: `{entidade}_dto.py`
- Routes: `{contexto}_routes.py`

### 6.3. Padrão de Rotas
```python
from fastapi import APIRouter, Request, Form
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro

router = APIRouter(prefix="/contexto")
templates = criar_templates("templates/contexto")

@router.get("/listar")
@requer_autenticacao()  # ou @requer_autenticacao(perfis=[Perfil.ADMIN])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    # lógica
    return templates.TemplateResponse("contexto/listar.html", {"request": request})
```

### 6.4. Padrão de Repositório
```python
def criar_tabela() -> bool:
    """Cria tabela se não existir"""

def inserir(entidade) -> Optional[int]:
    """Insere e retorna o ID"""

def alterar(entidade) -> bool:
    """Atualiza e retorna sucesso"""

def excluir(id: int) -> bool:
    """Exclui e retorna sucesso"""

def obter_por_id(id: int) -> Optional[Entidade]:
    """Busca por ID"""

def obter_todos() -> list[Entidade]:
    """Lista todas"""
```

### 6.5. Padrão de DTOs
```python
from pydantic import BaseModel, field_validator

class CriarEntidadeDTO(BaseModel):
    campo1: str
    campo2: int

    @field_validator('campo1')
    @classmethod
    def validar_campo1(cls, valor: str) -> str:
        # validação
        return valor
```

### 6.6. Padrão de Templates
- Usar `base_publica.html` para páginas públicas
- Usar `base_privada.html` para páginas autenticadas
- Usar macros de `macros/form_fields.html`
- Usar modais de `components/`

---

## 7. BANCO DE DADOS

### 7.1. Tabelas Existentes
- ✅ `usuario`
- ✅ `configuracao`
- ✅ `tarefa` (exemplo)

### 7.2. Tabelas a Criar
- ❌ `categoria`
- ❌ `anuncio`
- ❌ `endereco`
- ❌ `pedido`
- ❌ `mensagem`

### 7.3. Alterações na Tabela Usuario
Adicionar colunas:
```sql
ALTER TABLE usuario ADD COLUMN data_nascimento DATE;
ALTER TABLE usuario ADD COLUMN numero_documento VARCHAR(20);
ALTER TABLE usuario ADD COLUMN telefone VARCHAR(20);
ALTER TABLE usuario ADD COLUMN confirmado BOOLEAN DEFAULT FALSE;
```

---

## 8. ESTIMATIVA DE ESFORÇO

### 8.1. Por Módulo

| Módulo | Arquivos | Complexidade | Estimativa |
|--------|----------|--------------|------------|
| Categoria | 6 arquivos | Baixa | 4-6 horas |
| Anúncios | 8 arquivos | Média | 12-16 horas |
| Catálogo | 4 arquivos | Média | 8-10 horas |
| Endereços | 6 arquivos | Baixa | 4-6 horas |
| Carrinho | 4 arquivos | Média | 6-8 horas |
| Pedidos | 8 arquivos | Alta | 16-20 horas |
| Mensagens | 6 arquivos | Média | 10-12 horas |
| Admin (moderação) | 4 arquivos | Baixa | 4-6 horas |
| Ajustes Usuario | 3 arquivos | Baixa | 2-3 horas |
| **TOTAL** | **49 arquivos** | - | **66-87 horas** |

### 8.2. Ordem de Implementação Recomendada

**FASE 1 - Fundação (20-26h)**
1. Ajustes no Usuario + Perfil VENDEDOR (2-3h)
2. Módulo de Categoria (4-6h)
3. Módulo de Anúncios (12-16h)
4. Módulo de Endereços (4-6h)

**FASE 2 - Marketplace (14-18h)**
5. Módulo de Catálogo Público (8-10h)
6. Módulo de Carrinho (6-8h)

**FASE 3 - Transações (16-20h)**
7. Módulo de Pedidos (16-20h)

**FASE 4 - Comunicação e Admin (14-18h)**
8. Módulo de Mensagens (10-12h)
9. Admin - Moderação (4-6h)

---

## 9. RISCOS E CONSIDERAÇÕES

### 9.1. Riscos Técnicos
- ⚠️ **Carrinho de compras:** Decidir se armazena em sessão ou banco de dados
- ⚠️ **Upload de múltiplas imagens:** Adaptar foto_util para suportar múltiplos arquivos por anúncio
- ⚠️ **Sincronização de estoque:** Garantir que pedidos não excedam estoque disponível
- ⚠️ **Status de pedido:** Definir máquina de estados bem clara

### 9.2. Decisões de Design a Tomar
- 📋 Carrinho: sessão vs banco de dados?
- 📋 Um pedido = um produto ou múltiplos produtos?
- 📋 Sistema de pagamento: simulado ou integração real?
- 📋 Notificações: apenas email ou também in-app?

### 9.3. Funcionalidades Fora do Escopo (Fase 1)
- Sistema de pagamento integrado (Stripe, PagSeguro, etc.)
- Cálculo de frete automático
- Chat em tempo real (WebSocket)
- Notificações push
- App mobile
- Planos de assinatura (billing)

---

## 10. CONCLUSÕES E PRÓXIMOS PASSOS

### 10.1. Situação Atual
O projeto **Compraê** possui uma base sólida e bem estruturada:
- ✅ Todos os models estão criados
- ✅ Sistema de autenticação funcionando
- ✅ Infraestrutura completa (utils, decorators, templates base)
- ✅ Exemplos de referência (tarefas, admin usuários)

### 10.2. Gap Identificado
Faltam implementar **49 arquivos** distribuídos em **8 módulos** principais, representando aproximadamente **66-87 horas** de desenvolvimento.

### 10.3. Próximos Passos
1. ✅ Revisar e aprovar esta análise
2. 📋 Criar o GUIA.md com instruções detalhadas de implementação
3. 🔨 Começar implementação pela FASE 1 (Fundação)

### 10.4. Recomendações
- Implementar em fases para ter entregas incrementais
- Seguir rigorosamente os padrões existentes no projeto
- Criar testes para cada módulo implementado
- Revisar o DER (Diagrama Entidade-Relacionamento) antes de criar as tabelas
- Documentar decisões importantes no README.md

---

**Documento elaborado por:** Claude Code
**Data:** 20/10/2025
**Versão:** 1.0
