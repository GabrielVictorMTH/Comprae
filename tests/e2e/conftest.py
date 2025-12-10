"""
Configuracoes e fixtures para testes E2E com Playwright.

Gerencia o ciclo de vida do servidor FastAPI e fornece fixtures
para interacao com o browser via Playwright.

Testes E2E simulam interacoes reais do usuario via browser,
testando fluxos completos da aplicacao.

IMPORTANTE: Fixtures com scope="module" reiniciam o servidor
a cada arquivo de teste, garantindo estabilidade em execucao batch.
"""

import os
import signal
import socket
import sqlite3
import subprocess
import tempfile
import time
from typing import Generator

import pytest
from playwright.sync_api import Page


# Configuracoes do servidor E2E
E2E_SERVER_HOST = "127.0.0.1"
E2E_SERVER_PORT = 8403
E2E_BASE_URL = f"http://{E2E_SERVER_HOST}:{E2E_SERVER_PORT}"
E2E_SERVER_STARTUP_TIMEOUT = 30


def _porta_disponivel(host: str, port: int) -> bool:
    """Verifica se a porta esta disponivel."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def _liberar_porta(port: int, max_tentativas: int = 3) -> bool:
    """Tenta liberar a porta matando processos que a estao usando."""
    for tentativa in range(max_tentativas):
        try:
            # Encontra PIDs usando a porta
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if not result.stdout.strip():
                return True  # Porta ja esta livre

            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except (ProcessLookupError, ValueError):
                    pass

            time.sleep(2)  # Aguarda mais tempo para porta ser liberada

            # Verifica se liberou
            if _porta_disponivel("127.0.0.1", port):
                return True

        except Exception:
            pass

    return False


def _aguardar_servidor_online(host: str, port: int, timeout: int = 30) -> bool:
    """Aguarda o servidor ficar disponivel."""
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((host, port))
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            time.sleep(0.5)
    return False


def _aguardar_porta_livre(host: str, port: int, timeout: int = 10) -> bool:
    """Aguarda a porta ficar disponivel."""
    inicio = time.time()
    while time.time() - inicio < timeout:
        if _porta_disponivel(host, port):
            return True
        time.sleep(0.3)
    return False


@pytest.fixture(scope="module")
def e2e_test_database():
    """
    Cria banco de dados de teste isolado para E2E.
    Module-scoped para persistir durante cada arquivo de teste.
    """
    test_db = tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix="_e2e.db", prefix="test_"
    )
    test_db_path = test_db.name
    test_db.close()

    # Criar tabela configuracao e inserir rate limits usando SQL direto
    from sql.configuracao_sql import CRIAR_TABELA, INSERIR

    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    cursor.execute(CRIAR_TABELA)

    # Inserir rate limits muito altos para evitar bloqueios nos testes
    configs = [
        ("rate_limit_cadastro_max", "10000", "Rate limit cadastro - maximo"),
        ("rate_limit_cadastro_minutos", "1", "Rate limit cadastro - janela"),
        ("rate_limit_login_max", "10000", "Rate limit login - maximo"),
        ("rate_limit_login_minutos", "1", "Rate limit login - janela"),
    ]

    for chave, valor, descricao in configs:
        cursor.execute(INSERIR, (chave, valor, descricao))

    conn.commit()
    conn.close()

    yield test_db_path

    try:
        os.unlink(test_db_path)
    except Exception:
        pass


@pytest.fixture(scope="module")
def e2e_server(e2e_test_database) -> Generator[str, None, None]:
    """
    Inicia servidor FastAPI para testes E2E.

    Module-scoped para reiniciar o servidor a cada arquivo de teste,
    garantindo estabilidade em execucoes batch longas.
    Retorna a URL base do servidor.
    """
    # Libera a porta se estiver em uso (cleanup de execucoes anteriores)
    if not _porta_disponivel(E2E_SERVER_HOST, E2E_SERVER_PORT):
        if not _liberar_porta(E2E_SERVER_PORT, max_tentativas=5):
            if not _aguardar_porta_livre(E2E_SERVER_HOST, E2E_SERVER_PORT, timeout=15):
                pytest.skip(f"Porta {E2E_SERVER_PORT} nao pode ser liberada")

    env = os.environ.copy()
    env.update(
        {
            "DATABASE_PATH": e2e_test_database,
            "HOST": E2E_SERVER_HOST,
            "PORT": str(E2E_SERVER_PORT),
            "RUNNING_MODE": "Development",
            "RESEND_API_KEY": "",
            "LOG_LEVEL": "ERROR",
            "RELOAD": "False",
            # Rate limits muito altos para evitar bloqueios durante testes
            "RATE_LIMIT_CADASTRO_MAX": "1000",
            "RATE_LIMIT_CADASTRO_MINUTOS": "1",
            "RATE_LIMIT_LOGIN_MAX": "1000",
            "RATE_LIMIT_LOGIN_MINUTOS": "1",
        }
    )

    process = subprocess.Popen(
        ["python", "main.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    )

    if not _aguardar_servidor_online(
        E2E_SERVER_HOST, E2E_SERVER_PORT, E2E_SERVER_STARTUP_TIMEOUT
    ):
        process.terminate()
        process.wait()
        stdout, stderr = process.communicate()
        pytest.fail(
            f"Servidor nao iniciou em {E2E_SERVER_STARTUP_TIMEOUT}s.\n"
            f"stdout: {stdout.decode()}\n"
            f"stderr: {stderr.decode()}"
        )

    yield E2E_BASE_URL

    # Cleanup: encerra o servidor de forma robusta
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()

    # Garante que a porta seja liberada para o proximo modulo
    _aguardar_porta_livre(E2E_SERVER_HOST, E2E_SERVER_PORT, timeout=10)


@pytest.fixture(scope="session")
def browser_context_args():
    """Configuracoes do contexto do browser."""
    return {
        "viewport": {"width": 1280, "height": 720},
        "locale": "pt-BR",
        "timezone_id": "America/Sao_Paulo",
    }


@pytest.fixture(scope="function")
def e2e_page(page: Page, e2e_server: str) -> Page:
    """
    Fixture que fornece uma pagina Playwright configurada.

    Function-scoped para garantir isolamento entre testes.
    """
    page.set_default_timeout(10000)
    page.set_default_navigation_timeout(15000)
    page.base_url = e2e_server  # type: ignore
    yield page


@pytest.fixture(scope="function")
def limpar_banco_e2e(e2e_test_database):
    """
    Limpa o banco de dados E2E antes de cada teste.

    Garante isolamento entre testes E2E.
    """

    def _limpar():
        try:
            conn = sqlite3.connect(e2e_test_database)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%'"
            )
            tabelas = [row[0] for row in cursor.fetchall()]

            # Nao limpar 'configuracao' para manter rate limits altos
            ordem_limpeza = [
                "chamado_interacao",
                "chamado",
                "chat_mensagem",
                "chat_participante",
                "chat_sala",
                "usuario",
            ]

            for tabela in ordem_limpeza:
                if tabela in tabelas:
                    cursor.execute(f"DELETE FROM {tabela}")

            if "sqlite_sequence" in [
                row[0]
                for row in cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            ]:
                cursor.execute("DELETE FROM sqlite_sequence")

            conn.commit()
            conn.close()
        except Exception:
            pass

    _limpar()
    yield
    _limpar()


@pytest.fixture
def usuario_e2e_dados():
    """Dados de usuario para testes E2E."""
    return {
        "perfil": "Comprador",
        "nome": "Usuario E2E Teste",
        "email": "e2e_teste@example.com",
        "senha": "SenhaE2E@123",
    }


# Marca todos os testes nesta pasta como e2e
def pytest_collection_modifyitems(items):
    """Adiciona marca 'e2e' a todos os testes nesta pasta."""
    for item in items:
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
