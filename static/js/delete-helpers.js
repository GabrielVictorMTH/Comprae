/**
 * Delete Helpers
 *
 * Módulo para auxiliar na confirmação de exclusão de entidades com modal de confirmação.
 * Elimina código JavaScript duplicado em templates de listagem.
 *
 * Dependências:
 * - Bootstrap 5 (para modais)
 * - components/modal_confirmacao.html (deve estar incluído no template)
 * - modal-alerta.js (função abrirModalConfirmacao)
 *
 * @version 1.0.0
 * @author DefaultWebApp
 */

/**
 * Confirma exclusão de uma entidade com modal de confirmação customizável
 *
 * @param {Object} config - Configuração da confirmação
 * @param {number} config.id - ID da entidade a ser excluída
 * @param {string} config.nome - Nome/identificador principal da entidade
 * @param {string} config.urlBase - URL base para exclusão (ex: '/admin/usuarios')
 * @param {string} [config.entidade='item'] - Nome da entidade (ex: 'usuário', 'tarefa', 'chamado')
 * @param {Object} [config.camposDetalhes={}] - Objeto com campos a exibir (chave: label, valor: conteúdo HTML)
 * @param {string} [config.mensagem=null] - Mensagem customizada (null = usa mensagem padrão)
 * @param {string} [config.urlExclusao=null] - URL completa de exclusão (null = usa urlBase + id + '/excluir')
 *
 * @example
 * // Uso básico
 * confirmarExclusao({
 *     id: 1,
 *     nome: 'João Silva',
 *     urlBase: '/admin/usuarios',
 *     entidade: 'usuário'
 * });
 *
 * @example
 * // Uso com detalhes customizados
 * confirmarExclusao({
 *     id: 1,
 *     nome: 'João Silva',
 *     urlBase: '/admin/usuarios',
 *     entidade: 'usuário',
 *     camposDetalhes: {
 *         'Nome': 'João Silva',
 *         'Email': 'joao@email.com',
 *         'Perfil': '<span class="badge bg-danger">Administrador</span>'
 *     }
 * });
 *
 * @example
 * // Uso com URL customizada
 * confirmarExclusao({
 *     id: 1,
 *     nome: 'Tarefa #1',
 *     urlExclusao: '/tarefas/excluir/1',
 *     entidade: 'tarefa',
 *     camposDetalhes: {
 *         'Título': 'Implementar funcionalidade X',
 *         'Status': '<span class="badge bg-primary">Pendente</span>'
 *     }
 * });
 */
function confirmarExclusao(config) {
    // Validação de parâmetros obrigatórios
    if (!config.id) {
        console.error('confirmarExclusao: parâmetro "id" é obrigatório');
        return;
    }

    // Extração de parâmetros com valores padrão
    const {
        id,
        nome = 'item',
        urlBase = '',
        entidade = 'item',
        camposDetalhes = {},
        mensagem = null,
        urlExclusao = null
    } = config;

    // Construir URL de exclusão
    const url = urlExclusao || `${urlBase}/excluir/${id}`;

    // Validar URL
    if (!url || url === '/excluir/' + id) {
        console.error('confirmarExclusao: URL de exclusão inválida. Forneça "urlBase" ou "urlExclusao"');
        return;
    }

    // Construir HTML dos detalhes se houver campos
    let detalhesHtml = '';
    if (Object.keys(camposDetalhes).length > 0) {
        detalhesHtml = `
            <div class="card bg-light mt-3">
                <div class="card-body">
                    <table class="table table-sm table-borderless mb-0">
        `;

        // Adicionar cada campo à tabela
        for (const [label, valor] of Object.entries(camposDetalhes)) {
            detalhesHtml += `
                        <tr>
                            <th scope="row" width="30%">${label}:</th>
                            <td>${valor}</td>
                        </tr>
            `;
        }

        detalhesHtml += `
                    </table>
                </div>
            </div>
        `;
    }

    // Mensagem padrão ou customizada
    const mensagemFinal = mensagem || `Tem certeza que deseja excluir ${entidade === 'item' ? 'este' : 'este(a)'} <strong>${entidade}</strong>?`;

    // Abrir modal de confirmação
    abrirModalConfirmacao({
        url: url,
        mensagem: mensagemFinal,
        detalhes: detalhesHtml
    });
}

/**
 * Função auxiliar para escapar HTML em strings
 * Previne injeção de HTML não intencional
 *
 * @param {string} texto - Texto a ser escapado
 * @returns {string} Texto com caracteres HTML escapados
 *
 * @example
 * escapeHtml('<script>alert("xss")</script>');
 * // Retorna: "&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;"
 */
function escapeHtml(texto) {
    const div = document.createElement('div');
    div.textContent = texto;
    return div.innerHTML;
}

/**
 * Confirma exclusão de usuário (helper específico)
 *
 * @param {number} id - ID do usuário
 * @param {string} nome - Nome do usuário
 * @param {string} email - Email do usuário
 * @param {string} perfil - Perfil do usuário
 * @param {string} [urlBase='/admin/usuarios'] - URL base
 *
 * @example
 * excluirUsuario(1, 'João Silva', 'joao@email.com', 'Administrador');
 */
function excluirUsuario(id, nome, email, perfil, urlBase = '/admin/usuarios') {
    // Determinar cor do badge baseado no perfil
    let corBadge = 'info';
    if (perfil === 'Administrador') {
        corBadge = 'danger';
    } else if (perfil === 'Vendedor') {
        corBadge = 'warning text-dark';
    }

    confirmarExclusao({
        id: id,
        nome: nome,
        urlBase: urlBase,
        entidade: 'usuário',
        camposDetalhes: {
            'Nome': escapeHtml(nome),
            'Email': escapeHtml(email),
            'Perfil': `<span class="badge bg-${corBadge}">${escapeHtml(perfil)}</span>`
        }
    });
}

/**
 * Confirma exclusão de tarefa (helper específico)
 *
 * @param {number} id - ID da tarefa
 * @param {string} titulo - Título da tarefa
 * @param {string} status - Status da tarefa
 * @param {string} [urlBase='/tarefas'] - URL base
 *
 * @example
 * excluirTarefa(1, 'Implementar funcionalidade X', 'Pendente');
 */
function excluirTarefa(id, titulo, status, urlBase = '/tarefas') {
    // Determinar cor do badge baseado no status
    let corBadge = 'secondary';
    if (status === 'Pendente') {
        corBadge = 'warning';
    } else if (status === 'Em Andamento') {
        corBadge = 'primary';
    } else if (status === 'Concluída') {
        corBadge = 'success';
    }

    confirmarExclusao({
        id: id,
        nome: titulo,
        urlBase: urlBase,
        entidade: 'tarefa',
        camposDetalhes: {
            'Título': escapeHtml(titulo),
            'Status': `<span class="badge bg-${corBadge}">${escapeHtml(status)}</span>`
        }
    });
}

/**
 * Confirma exclusão de chamado (helper específico)
 *
 * @param {number} id - ID do chamado
 * @param {string} titulo - Título do chamado
 * @param {string} status - Status do chamado
 * @param {string} prioridade - Prioridade do chamado
 * @param {string} [urlBase='/chamados'] - URL base
 *
 * @example
 * excluirChamado(1, 'Bug no login', 'Aberto', 'Alta');
 */
function excluirChamado(id, titulo, status, prioridade, urlBase = '/chamados') {
    // Determinar cor do badge de status
    let corStatus = 'secondary';
    if (status === 'Aberto') {
        corStatus = 'primary';
    } else if (status === 'Em Análise') {
        corStatus = 'info';
    } else if (status === 'Resolvido') {
        corStatus = 'success';
    }

    // Determinar cor do badge de prioridade
    let corPrioridade = 'secondary';
    if (prioridade === 'Urgente') {
        corPrioridade = 'danger';
    } else if (prioridade === 'Alta') {
        corPrioridade = 'warning text-dark';
    } else if (prioridade === 'Média') {
        corPrioridade = 'info';
    }

    confirmarExclusao({
        id: id,
        nome: `#${id}`,
        urlBase: urlBase,
        entidade: 'chamado',
        camposDetalhes: {
            'Título': escapeHtml(titulo),
            'Status': `<span class="badge bg-${corStatus}">${escapeHtml(status)}</span>`,
            'Prioridade': `<span class="badge bg-${corPrioridade}">${escapeHtml(prioridade)}</span>`
        }
    });
}

// Exportar funções para uso global
window.confirmarExclusao = confirmarExclusao;
window.excluirUsuario = excluirUsuario;
window.excluirTarefa = excluirTarefa;
window.excluirChamado = excluirChamado;
window.escapeHtml = escapeHtml;
