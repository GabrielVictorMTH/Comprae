/**
 * PasswordValidator - Sistema de feedback visual de senha
 *
 * Funcionalidades:
 * - Toggle de visibilidade de senha
 * - Medição de força de senha
 * - Atualização visual de requisitos
 * - Feedback visual de senhas coincidentes
 *
 * IMPORTANTE: Este componente fornece APENAS feedback visual.
 * A validação real é feita server-side através de DTOs Pydantic.
 * NÃO bloqueia envio do formulário com alerts.
 */

class PasswordValidator {
    /**
     * @param {Object} config - Configuração do validador
     * @param {string} config.passwordFieldId - ID do campo de senha
     * @param {string} config.confirmPasswordFieldId - ID do campo de confirmação (opcional)
     * @param {string} config.strengthBarId - ID da barra de progresso (opcional)
     * @param {string} config.strengthTextId - ID do texto de força (opcional)
     * @param {string} config.matchMessageId - ID da mensagem de coincidência (opcional)
     * @param {Object} config.requirements - IDs dos elementos de requisitos (opcional)
     * @param {number} config.minLength - Tamanho mínimo da senha (padrão: 8)
     * @param {boolean} config.showStrength - Exibir medidor de força (padrão: false)
     * @param {boolean} config.showRequirements - Exibir requisitos visuais (padrão: false)
     * @param {Function} config.onValidate - Callback customizado de validação (opcional)
     */
    constructor(config) {
        this.config = {
            minLength: 8,
            showStrength: false,
            showRequirements: false,
            ...config
        };

        this.passwordField = document.getElementById(this.config.passwordFieldId);
        this.confirmPasswordField = this.config.confirmPasswordFieldId
            ? document.getElementById(this.config.confirmPasswordFieldId)
            : null;

        if (!this.passwordField) {
            console.error(`Campo de senha com ID "${this.config.passwordFieldId}" não encontrado`);
            return;
        }

        this.init();
    }

    init() {
        // Configurar eventos de força de senha
        if (this.config.showStrength) {
            this.strengthBar = document.getElementById(this.config.strengthBarId);
            this.strengthText = document.getElementById(this.config.strengthTextId);

            if (this.strengthBar && this.strengthText) {
                this.passwordField.addEventListener('input', () => this.checkPasswordStrength());
            }
        }

        // Configurar eventos de senha coincidente
        if (this.confirmPasswordField && this.config.matchMessageId) {
            this.matchMessage = document.getElementById(this.config.matchMessageId);

            if (this.matchMessage) {
                this.confirmPasswordField.addEventListener('input', () => this.checkPasswordMatch());
            }
        }
    }

    /**
     * Verifica a força da senha e atualiza indicadores visuais
     */
    checkPasswordStrength() {
        const password = this.passwordField.value;
        let strength = 0;
        let color = 'danger';
        let text = 'Muito fraca';

        // Verificar requisitos
        const requirements = {
            length: password.length >= this.config.minLength,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        // Atualizar indicadores visuais de requisitos
        if (this.config.showRequirements && this.config.requirements) {
            this.updateRequirementIndicators(requirements);
        }

        // Calcular força (20% para cada requisito)
        if (requirements.length) strength += 20;
        if (requirements.uppercase) strength += 20;
        if (requirements.lowercase) strength += 20;
        if (requirements.number) strength += 20;
        if (requirements.special) strength += 20;

        // Definir texto e cor baseado na força
        if (strength >= 80) {
            color = 'success';
            text = 'Forte';
        } else if (strength >= 60) {
            color = 'info';
            text = 'Média';
        } else if (strength >= 40) {
            color = 'warning';
            text = 'Fraca';
        }

        // Atualizar barra de progresso
        if (this.strengthBar) {
            this.strengthBar.style.width = strength + '%';
            this.strengthBar.className = 'progress-bar bg-' + color;
        }

        // Atualizar texto de força
        if (this.strengthText) {
            this.strengthText.textContent = text;
            this.strengthText.className = 'text-' + color;
        }

        return { strength, requirements };
    }

    /**
     * Atualiza indicadores visuais de requisitos de senha
     * SEGURANÇA: Usa createElement em vez de innerHTML para prevenir XSS
     */
    updateRequirementIndicators(requirements) {
        const reqMap = {
            length: this.config.requirements.length,
            uppercase: this.config.requirements.uppercase,
            lowercase: this.config.requirements.lowercase,
            number: this.config.requirements.number,
            special: this.config.requirements.special
        };

        Object.keys(reqMap).forEach(key => {
            const elementId = reqMap[key];
            if (!elementId) return;

            const element = document.getElementById(elementId);
            if (!element) return;

            const isMet = requirements[key];

            // Extrair texto original (sem ícones)
            const originalText = element.textContent
                .replace(/✓ /g, '')
                .replace(/<i.*?<\/i>/g, '')
                .trim();

            // Limpar conteúdo atual
            element.innerHTML = '';

            if (isMet) {
                // Criar ícone de sucesso usando createElement
                const icon = document.createElement('i');
                icon.className = 'bi bi-check-circle-fill';
                element.appendChild(icon);

                // Adicionar espaço e texto
                element.appendChild(document.createTextNode(' ' + originalText));
                element.classList.add('text-success');
            } else {
                // Apenas texto, sem ícone
                element.textContent = originalText;
                element.classList.remove('text-success');
            }
        });
    }

    /**
     * Verifica se as senhas coincidem
     * SEGURANÇA: Usa createElement em vez de innerHTML para prevenir XSS
     */
    checkPasswordMatch() {
        if (!this.confirmPasswordField || !this.matchMessage) return true;

        const password = this.passwordField.value;
        const confirmPassword = this.confirmPasswordField.value;

        if (confirmPassword.length === 0) {
            this.matchMessage.textContent = '';
            return true;
        }

        // Limpar conteúdo anterior
        this.matchMessage.innerHTML = '';

        // Criar span wrapper
        const span = document.createElement('span');

        if (password === confirmPassword) {
            // Senhas coincidem - feedback positivo
            span.className = 'text-success';

            const icon = document.createElement('i');
            icon.className = 'bi bi-check-circle';
            span.appendChild(icon);

            span.appendChild(document.createTextNode(' As senhas coincidem'));
            this.matchMessage.appendChild(span);
            return true;
        } else {
            // Senhas não coincidem - feedback negativo
            span.className = 'text-danger';

            const icon = document.createElement('i');
            icon.className = 'bi bi-x-circle';
            span.appendChild(icon);

            span.appendChild(document.createTextNode(' As senhas não coincidem'));
            this.matchMessage.appendChild(span);
            return false;
        }
    }

    /**
     * Retorna informações sobre a força da senha (para uso programático)
     * @returns {Object} Objeto com força (0-100) e requisitos atendidos
     */
    getPasswordStrength() {
        const password = this.passwordField.value;
        let strength = 0;

        // Verificar requisitos
        const requirements = {
            length: password.length >= this.config.minLength,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        // Calcular força (20% para cada requisito)
        if (requirements.length) strength += 20;
        if (requirements.uppercase) strength += 20;
        if (requirements.lowercase) strength += 20;
        if (requirements.number) strength += 20;
        if (requirements.special) strength += 20;

        return {
            strength,
            requirements,
            isStrong: strength >= 80,
            isMedium: strength >= 60,
            isWeak: strength < 60
        };
    }

    /**
     * Retorna se as senhas coincidem (para uso programático)
     * @returns {boolean} True se senhas coincidem ou não há confirmação
     */
    doPasswordsMatch() {
        if (!this.confirmPasswordField) return true;

        const password = this.passwordField.value;
        const confirmPassword = this.confirmPasswordField.value;

        return password === confirmPassword;
    }
}

/**
 * Função global para toggle de visibilidade de senha
 * @param {string} fieldId - ID do campo de senha
 */
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const icon = document.getElementById('icon_' + fieldId);

    if (!field) {
        console.error(`Campo com ID "${fieldId}" não encontrado`);
        return;
    }

    if (field.type === 'password') {
        field.type = 'text';
        if (icon) {
            icon.classList.remove('bi-eye');
            icon.classList.add('bi-eye-slash');
        }
    } else {
        field.type = 'password';
        if (icon) {
            icon.classList.remove('bi-eye-slash');
            icon.classList.add('bi-eye');
        }
    }
}

/**
 * Inicializar namespace global do app
 */
window.App = window.App || {};
window.App.Password = window.App.Password || {};

/**
 * API pública do módulo Password
 */
window.App.Password.Validator = PasswordValidator;
window.App.Password.toggle = togglePassword;

/**
 * DEPRECATED: Manter retrocompatibilidade
 * @deprecated Use window.App.Password.Validator em vez disso
 */
window.PasswordValidator = PasswordValidator;

/**
 * @deprecated Use window.App.Password.toggle() em vez disso
 */
window.togglePassword = togglePassword;
