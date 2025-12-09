"""
Testes para o modelo UsuarioLogado (model/usuario_logado_model.py)

Testa todos os métodos do dataclass UsuarioLogado incluindo
verificação de perfis, serialização e desserialização.
"""

import pytest
from unittest.mock import MagicMock

from model.usuario_logado_model import UsuarioLogado
from util.perfis import Perfil


class TestUsuarioLogadoInstanciacao:
    """Testes de criação de instâncias"""

    def test_criar_usuario_logado(self):
        """Deve criar instância com todos os campos"""
        usuario = UsuarioLogado(
            id=1,
            nome="João Silva",
            email="joao@teste.com",
            perfil=Perfil.COMPRADOR.value,
        )

        assert usuario.id == 1
        assert usuario.nome == "João Silva"
        assert usuario.email == "joao@teste.com"
        assert usuario.perfil == "Comprador"

    def test_usuario_logado_imutavel(self):
        """UsuarioLogado deve ser imutável (frozen=True)"""
        usuario = UsuarioLogado(
            id=1, nome="João", email="joao@teste.com", perfil=Perfil.COMPRADOR.value
        )

        with pytest.raises(AttributeError):
            usuario.nome = "Novo Nome"


class TestIsAdmin:
    """Testes para o método is_admin()"""

    def test_admin_retorna_true(self):
        """Admin deve retornar True"""
        admin = UsuarioLogado(
            id=1, nome="Admin", email="admin@teste.com", perfil=Perfil.ADMIN.value
        )

        assert admin.is_admin() is True

    def test_comprador_retorna_false(self):
        """Comprador não deve ser admin"""
        comprador = UsuarioLogado(
            id=1,
            nome="Comprador",
            email="comprador@teste.com",
            perfil=Perfil.COMPRADOR.value,
        )

        assert comprador.is_admin() is False

    def test_vendedor_retorna_false(self):
        """Vendedor não deve ser admin"""
        vendedor = UsuarioLogado(
            id=1,
            nome="Vendedor",
            email="vendedor@teste.com",
            perfil=Perfil.VENDEDOR.value,
        )

        assert vendedor.is_admin() is False


class TestIsComprador:
    """Testes para o método is_comprador()"""

    def test_comprador_retorna_true(self):
        """Comprador deve retornar True"""
        comprador = UsuarioLogado(
            id=1,
            nome="Comprador",
            email="comprador@teste.com",
            perfil=Perfil.COMPRADOR.value,
        )

        assert comprador.is_comprador() is True

    def test_admin_retorna_false(self):
        """Admin não deve ser comprador"""
        admin = UsuarioLogado(
            id=1, nome="Admin", email="admin@teste.com", perfil=Perfil.ADMIN.value
        )

        assert admin.is_comprador() is False

    def test_vendedor_retorna_false(self):
        """Vendedor não deve ser comprador"""
        vendedor = UsuarioLogado(
            id=1,
            nome="Vendedor",
            email="vendedor@teste.com",
            perfil=Perfil.VENDEDOR.value,
        )

        assert vendedor.is_comprador() is False


class TestIsVendedor:
    """Testes para o método is_vendedor()"""

    def test_vendedor_retorna_true(self):
        """Vendedor deve retornar True"""
        vendedor = UsuarioLogado(
            id=1,
            nome="Vendedor",
            email="vendedor@teste.com",
            perfil=Perfil.VENDEDOR.value,
        )

        assert vendedor.is_vendedor() is True

    def test_admin_retorna_false(self):
        """Admin não deve ser vendedor"""
        admin = UsuarioLogado(
            id=1, nome="Admin", email="admin@teste.com", perfil=Perfil.ADMIN.value
        )

        assert admin.is_vendedor() is False

    def test_comprador_retorna_false(self):
        """Comprador não deve ser vendedor"""
        comprador = UsuarioLogado(
            id=1,
            nome="Comprador",
            email="comprador@teste.com",
            perfil=Perfil.COMPRADOR.value,
        )

        assert comprador.is_vendedor() is False


class TestTemPerfil:
    """Testes para o método tem_perfil()"""

    def test_tem_perfil_unico(self):
        """Deve retornar True quando tem o perfil"""
        admin = UsuarioLogado(
            id=1, nome="Admin", email="admin@teste.com", perfil=Perfil.ADMIN.value
        )

        assert admin.tem_perfil(Perfil.ADMIN.value) is True

    def test_nao_tem_perfil(self):
        """Deve retornar False quando não tem o perfil"""
        comprador = UsuarioLogado(
            id=1,
            nome="Comprador",
            email="comprador@teste.com",
            perfil=Perfil.COMPRADOR.value,
        )

        assert comprador.tem_perfil(Perfil.ADMIN.value) is False

    def test_tem_perfil_multiplos(self):
        """Deve retornar True quando tem um dos perfis"""
        vendedor = UsuarioLogado(
            id=1,
            nome="Vendedor",
            email="vendedor@teste.com",
            perfil=Perfil.VENDEDOR.value,
        )

        # Vendedor está na lista
        assert vendedor.tem_perfil(Perfil.ADMIN.value, Perfil.VENDEDOR.value) is True

    def test_nao_tem_nenhum_perfil(self):
        """Deve retornar False quando não tem nenhum dos perfis"""
        comprador = UsuarioLogado(
            id=1,
            nome="Comprador",
            email="comprador@teste.com",
            perfil=Perfil.COMPRADOR.value,
        )

        # Comprador não é admin nem vendedor
        assert comprador.tem_perfil(Perfil.ADMIN.value, Perfil.VENDEDOR.value) is False


class TestToDict:
    """Testes para o método to_dict()"""

    def test_converte_para_dict(self):
        """Deve converter para dicionário"""
        usuario = UsuarioLogado(
            id=42, nome="Teste", email="teste@email.com", perfil="Comprador"
        )

        resultado = usuario.to_dict()

        assert resultado == {
            "id": 42,
            "nome": "Teste",
            "email": "teste@email.com",
            "perfil": "Comprador",
        }


class TestFromDict:
    """Testes para o método from_dict()"""

    def test_cria_de_dict_completo(self):
        """Deve criar instância de dicionário completo"""
        dados = {
            "id": 1,
            "nome": "João",
            "email": "joao@email.com",
            "perfil": "Comprador",
        }

        usuario = UsuarioLogado.from_dict(dados)

        assert usuario is not None
        assert usuario.id == 1
        assert usuario.nome == "João"
        assert usuario.email == "joao@email.com"
        assert usuario.perfil == "Comprador"

    def test_retorna_none_para_none(self):
        """Deve retornar None quando data é None"""
        resultado = UsuarioLogado.from_dict(None)

        assert resultado is None

    def test_levanta_erro_campo_faltando(self):
        """Deve levantar ValueError quando campo está faltando"""
        dados_incompletos = {
            "id": 1,
            "nome": "João",
            # falta email e perfil
        }

        with pytest.raises(ValueError) as exc_info:
            UsuarioLogado.from_dict(dados_incompletos)

        assert "Campos obrigatórios ausentes" in str(exc_info.value)

    def test_levanta_erro_mostra_campos_faltantes(self):
        """Mensagem de erro deve mostrar quais campos faltam"""
        dados_incompletos = {
            "id": 1,
            "nome": "João",
            "email": "joao@email.com",
            # falta perfil
        }

        with pytest.raises(ValueError) as exc_info:
            UsuarioLogado.from_dict(dados_incompletos)

        assert "perfil" in str(exc_info.value)


class TestFromUsuario:
    """Testes para o método from_usuario()"""

    def test_cria_de_usuario(self):
        """Deve criar UsuarioLogado de objeto Usuario"""
        # Mock do objeto Usuario
        usuario_mock = MagicMock()
        usuario_mock.id = 123
        usuario_mock.nome = "Maria"
        usuario_mock.email = "maria@email.com"
        usuario_mock.perfil = "Vendedor"

        usuario_logado = UsuarioLogado.from_usuario(usuario_mock)

        assert usuario_logado.id == 123
        assert usuario_logado.nome == "Maria"
        assert usuario_logado.email == "maria@email.com"
        assert usuario_logado.perfil == "Vendedor"
