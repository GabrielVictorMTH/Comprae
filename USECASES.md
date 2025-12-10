# Casos de Uso - Sistema Comprae

Este documento descreve todos os casos de uso de requisitos funcionais presentes no sistema Comprae, organizados por perfil de usuário.

---

## Perfis de Usuário

O sistema possui **3 perfis de usuário** distintos:

| Perfil | Descrição |
|--------|-----------|
| **Administrador** | Acesso total ao sistema. Gerencia usuários, produtos, pedidos, categorias e tickets de suporte. |
| **Comprador** | Usuário que navega por produtos, cria pedidos de compra e se comunica com vendedores. |
| **Vendedor** | Usuário que cadastra produtos para venda, gerencia seus anúncios e processa pedidos recebidos. |

---

## Casos de Uso Públicos (Usuário Não Autenticado)

Ações disponíveis para qualquer visitante do sistema, sem necessidade de login.

| ID | Caso de Uso | Descrição |
|----|-------------|-----------|
| UC-001 | Visualizar Página Inicial | Acessar a página inicial com os anúncios mais recentes |
| UC-002 | Visualizar Página Sobre | Acessar informações sobre o projeto acadêmico |
| UC-003 | Navegar por Produtos | Listar produtos ativos com busca, filtros e paginação |
| UC-004 | Visualizar Detalhes do Produto | Ver informações completas de um produto (preço, estoque, vendedor) |
| UC-005 | Cadastrar-se no Sistema | Registrar-se como Comprador ou Vendedor |
| UC-006 | Fazer Login | Autenticar-se no sistema |
| UC-007 | Solicitar Recuperação de Senha | Solicitar token de redefinição de senha via e-mail |
| UC-008 | Redefinir Senha | Definir nova senha usando token válido |

---

## Casos de Uso do Comprador

### Gerenciamento de Perfil

| ID | Caso de Uso | Perfis Permitidos | Descrição |
|----|-------------|-------------------|-----------|
| UC-101 | Visualizar Dashboard | Comprador, Vendedor | Acessar painel pessoal com contadores de pedidos e tickets |
| UC-102 | Visualizar Perfil | Comprador, Vendedor | Ver informações pessoais e endereço cadastrado |
| UC-103 | Editar Perfil | Comprador, Vendedor | Atualizar nome e e-mail |
| UC-104 | Alterar Senha | Comprador, Vendedor | Modificar senha da conta |
| UC-105 | Atualizar Foto de Perfil | Comprador, Vendedor | Fazer upload de foto de perfil recortada |

### Gerenciamento de Endereço

| ID | Caso de Uso | Perfis Permitidos | Descrição |
|----|-------------|-------------------|-----------|
| UC-111 | Visualizar Endereço | Comprador, Vendedor | Ver endereço cadastrado |
| UC-112 | Cadastrar Endereço | Comprador, Vendedor | Registrar endereço de entrega (limite de um por usuário) |
| UC-113 | Editar Endereço | Comprador, Vendedor | Atualizar informações do endereço |
| UC-114 | Excluir Endereço | Comprador, Vendedor | Remover endereço cadastrado |

### Gerenciamento de Pedidos (Fluxo de Compra)

| ID | Caso de Uso | Perfis Permitidos | Descrição |
|----|-------------|-------------------|-----------|
| UC-121 | Listar Meus Pedidos | Comprador | Visualizar todos os pedidos realizados com status |
| UC-122 | Visualizar Detalhes do Pedido | Comprador | Ver informações detalhadas de um pedido |
| UC-123 | Criar Pedido | Comprador | Iniciar negociação com vendedor (status: Negociando) |
| UC-124 | Pagar Pedido | Comprador | Simular pagamento (Pendente → Pago) |
| UC-125 | Cancelar Pedido | Comprador | Cancelar pedido (apenas se Negociando ou Pendente) |
| UC-126 | Confirmar Entrega | Comprador | Marcar pedido como entregue (Enviado → Entregue) |

**Fluxo de Status do Pedido (Comprador):**
```
1. Comprador cria pedido → NEGOCIANDO
2. Vendedor define preço → PENDENTE
3. Comprador paga → PAGO
4. Vendedor envia → ENVIADO
5. Comprador confirma → ENTREGUE
```

### Comunicação

| ID | Caso de Uso | Perfis Permitidos | Descrição |
|----|-------------|-------------------|-----------|
| UC-131 | Abrir Chamado de Suporte | Comprador, Vendedor | Criar solicitação de suporte |
| UC-132 | Listar Meus Chamados | Comprador, Vendedor | Ver todos os chamados pessoais |
| UC-133 | Visualizar Chamado | Comprador, Vendedor | Ver chamado com histórico de interações |
| UC-134 | Responder Chamado | Comprador, Vendedor | Adicionar mensagem ao chamado |
| UC-135 | Excluir Chamado | Comprador, Vendedor | Excluir chamado próprio (se aberto e sem respostas do admin) |
| UC-141 | Iniciar Chat | Comprador, Vendedor | Criar/obter sala de chat com outro usuário |
| UC-142 | Enviar Mensagem | Comprador, Vendedor | Enviar mensagem no chat |
| UC-143 | Visualizar Conversas | Comprador, Vendedor | Listar salas de chat com contagem de não lidas |
| UC-144 | Visualizar Mensagens | Comprador, Vendedor | Ver histórico de mensagens de uma conversa |
| UC-145 | Marcar como Lida | Comprador, Vendedor | Marcar mensagens como lidas |

---

## Casos de Uso do Vendedor

### Gerenciamento de Produtos (Anúncios)

| ID | Caso de Uso | Perfis Permitidos | Descrição |
|----|-------------|-------------------|-----------|
| UC-201 | Listar Meus Produtos | Vendedor | Ver todos os anúncios criados pelo vendedor |
| UC-202 | Cadastrar Produto | Vendedor | Criar novo anúncio de produto com foto |
| UC-203 | Editar Produto | Vendedor | Atualizar detalhes, preço e estoque do produto |
| UC-204 | Excluir Produto | Vendedor | Remover produto (se não houver pedidos vinculados) |
| UC-205 | Ativar/Desativar Produto | Vendedor | Alternar visibilidade do produto |

### Gerenciamento de Pedidos (Fluxo de Venda)

| ID | Caso de Uso | Perfis Permitidos | Descrição |
|----|-------------|-------------------|-----------|
| UC-211 | Listar Pedidos Recebidos | Vendedor | Ver todos os pedidos dos produtos do vendedor |
| UC-212 | Definir Preço Final | Vendedor | Definir preço negociado (Negociando → Pendente) |
| UC-213 | Enviar Pedido | Vendedor | Marcar como enviado com código de rastreio (Pago → Enviado) |
| UC-214 | Cancelar Pedido | Vendedor | Cancelar pedido (se Negociando ou Pendente) |

**Fluxo de Status do Pedido (Vendedor):**
```
1. Recebe pedido → NEGOCIANDO
2. Define preço final → PENDENTE
3. Recebe pagamento → PAGO
4. Envia produto → ENVIADO
5. Comprador confirma → ENTREGUE
```

### Perfil e Comunicação

O Vendedor também tem acesso a todos os casos de uso de:
- Gerenciamento de Perfil (UC-101 a UC-105)
- Gerenciamento de Endereço (UC-111 a UC-114)
- Comunicação (UC-131 a UC-145)

---

## Casos de Uso do Administrador

### Gerenciamento de Usuários

| ID | Caso de Uso | Perfis Permitidos | Descrição |
|----|-------------|-------------------|-----------|
| UC-301 | Listar Usuários | Administrador | Ver todos os usuários cadastrados |
| UC-302 | Cadastrar Usuário | Administrador | Registrar novo usuário (qualquer perfil) |
| UC-303 | Editar Usuário | Administrador | Atualizar nome, e-mail e perfil do usuário |
| UC-304 | Excluir Usuário | Administrador | Remover usuário (não pode excluir a si mesmo) |

### Gerenciamento de Produtos

| ID | Caso de Uso | Perfis Permitidos | Descrição |
|----|-------------|-------------------|-----------|
| UC-311 | Listar Todos os Produtos | Administrador | Ver todos os anúncios (ativos/inativos) |
| UC-312 | Moderar Produtos | Administrador | Ver produtos pendentes de moderação |
| UC-313 | Aprovar Produto | Administrador | Ativar produto pendente |
| UC-314 | Reprovar Produto | Administrador | Manter inativo com motivo |
| UC-315 | Editar Produto | Administrador | Modificar qualquer produto |
| UC-316 | Excluir Produto | Administrador | Remover produto |

### Gerenciamento de Pedidos

| ID | Caso de Uso | Perfis Permitidos | Descrição |
|----|-------------|-------------------|-----------|
| UC-321 | Listar Todos os Pedidos | Administrador | Ver todos os pedidos com filtro de status |
| UC-322 | Visualizar Detalhes do Pedido | Administrador | Ver informações completas do pedido |
| UC-323 | Cancelar Pedido | Administrador | Cancelamento administrativo |
| UC-324 | Visualizar Estatísticas | Administrador | Dashboard de estatísticas de pedidos |

### Gerenciamento de Categorias

| ID | Caso de Uso | Perfis Permitidos | Descrição |
|----|-------------|-------------------|-----------|
| UC-331 | Listar Categorias | Administrador | Ver todas as categorias de produtos |
| UC-332 | Cadastrar Categoria | Administrador | Adicionar nova categoria |
| UC-333 | Editar Categoria | Administrador | Atualizar categoria |
| UC-334 | Excluir Categoria | Administrador | Remover categoria |

### Gerenciamento de Endereços

| ID | Caso de Uso | Perfis Permitidos | Descrição |
|----|-------------|-------------------|-----------|
| UC-341 | Listar Todos os Endereços | Administrador | Ver todos os endereços cadastrados |
| UC-342 | Visualizar Detalhes do Endereço | Administrador | Ver informações do endereço |
| UC-343 | Excluir Endereço | Administrador | Remover endereço |

### Gerenciamento de Curtidas

| ID | Caso de Uso | Perfis Permitidos | Descrição |
|----|-------------|-------------------|-----------|
| UC-351 | Listar Todas as Curtidas | Administrador | Ver todas as curtidas de usuários |
| UC-352 | Excluir Curtida | Administrador | Remover curtida |

### Gerenciamento de Chamados de Suporte

| ID | Caso de Uso | Perfis Permitidos | Descrição |
|----|-------------|-------------------|-----------|
| UC-361 | Listar Todos os Chamados | Administrador | Ver todos os chamados de suporte |
| UC-362 | Visualizar Chamado | Administrador | Ver detalhes do chamado com histórico |
| UC-363 | Responder Chamado | Administrador | Adicionar resposta e alterar status |
| UC-364 | Fechar Chamado | Administrador | Marcar como fechado |
| UC-365 | Reabrir Chamado | Administrador | Reabrir chamado fechado |

### Gerenciamento do Sistema

| ID | Caso de Uso | Perfis Permitidos | Descrição |
|----|-------------|-------------------|-----------|
| UC-371 | Visualizar Configurações | Administrador | Ver configurações do sistema |
| UC-372 | Editar Configuração | Administrador | Atualizar configuração |
| UC-373 | Criar Backup | Administrador | Gerar backup do banco de dados |
| UC-374 | Listar Backups | Administrador | Ver backups disponíveis |
| UC-375 | Restaurar Backup | Administrador | Restaurar a partir de backup |
| UC-376 | Download de Backup | Administrador | Baixar arquivo de backup |

---

## Matriz de Permissões por Perfil

| Área Funcional | Público | Comprador | Vendedor | Administrador |
|----------------|:-------:|:---------:|:--------:|:-------------:|
| Navegação Pública | ✓ | ✓ | ✓ | ✓ |
| Cadastro/Login | ✓ | - | - | - |
| Gerenciamento de Perfil | - | ✓ | ✓ | - |
| Gerenciamento de Endereço | - | ✓ | ✓ | - |
| Criar Pedidos | - | ✓ | - | - |
| Pagar/Confirmar Entrega | - | ✓ | - | - |
| Gerenciar Produtos Próprios | - | - | ✓ | - |
| Processar Pedidos Recebidos | - | - | ✓ | - |
| Chat | - | ✓ | ✓ | - |
| Chamados de Suporte | - | ✓ | ✓ | ✓ |
| Gerenciar Usuários | - | - | - | ✓ |
| Gerenciar Todos os Produtos | - | - | - | ✓ |
| Gerenciar Todos os Pedidos | - | - | - | ✓ |
| Gerenciar Categorias | - | - | - | ✓ |
| Gerenciar Sistema | - | - | - | ✓ |

---

## Resumo Estatístico

| Categoria | Quantidade |
|-----------|------------|
| **Total de Casos de Uso** | 76 |
| Casos de Uso Públicos | 8 |
| Casos de Uso do Comprador | 26 |
| Casos de Uso do Vendedor | 30 (incluindo os compartilhados com Comprador) |
| Casos de Uso do Administrador | 32 |

---

## Regras de Negócio Importantes

### Pedidos
- Pedidos só podem ser cancelados nos status "Negociando" ou "Pendente"
- O comprador precisa ter endereço cadastrado para criar pedidos
- O vendedor define o preço final após a criação do pedido pelo comprador

### Produtos
- Vendedores só podem editar/excluir seus próprios produtos
- Produtos com pedidos vinculados não podem ser excluídos
- Produtos inativos não aparecem nas listagens públicas

### Endereços
- Cada usuário pode ter apenas um endereço cadastrado

### Chat
- Usuários não podem conversar consigo mesmos
- Usuários não podem iniciar chat com administradores (usar chamados de suporte)

### Chamados de Suporte
- Usuários só podem excluir chamados próprios se:
  - Status = "Aberto"
  - Não houver respostas do administrador

---

*Documento gerado automaticamente para o projeto Comprae - Sistema de Marketplace Acadêmico*
