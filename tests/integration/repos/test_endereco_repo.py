"""
Testes para o repositório de endereços.

Testa todas as operações CRUD do endereco_repo e validações do model/SQL.
"""

import pytest
from repo import endereco_repo, usuario_repo
from model.endereco_model import Endereco
from model.usuario_model import Usuario
from util.security import criar_hash_senha


@pytest.fixture
def usuario_teste():
    """Fixture para criar usuário de teste"""
    usuario = Usuario(
        id=0,
        nome="Usuário Teste Endereco",
        email=f"usuario_endereco_{id(Usuario)}@test.com",
        senha=criar_hash_senha("senha123"),
        perfil="Comprador",
    )
    usuario_id = usuario_repo.inserir(usuario)
    return usuario_id


class TestCriarTabela:
    """Testes de criação de tabela"""

    def test_criar_tabela_sucesso(self):
        """Testa criação da tabela endereco"""
        resultado = endereco_repo.criar_tabela()
        assert resultado is True


class TestInserir:
    """Testes de inserção de endereços"""

    def test_inserir_endereco_valido(self, usuario_teste):
        """Testa inserção de endereço válido"""
        endereco = Endereco(
            id=0,
            id_usuario=usuario_teste,
            titulo="Casa",
            logradouro="Rua das Flores",
            numero="123",
            bairro="Centro",
            cidade="São Paulo",
            uf="SP",
            cep="01234-567",
            complemento="Apto 101",
            usuario=None,
        )
        endereco_id = endereco_repo.inserir(endereco)

        assert endereco_id is not None
        assert endereco_id > 0

    def test_inserir_endereco_sem_complemento(self, usuario_teste):
        """Testa inserção sem complemento (campo opcional)"""
        endereco = Endereco(
            id=0,
            id_usuario=usuario_teste,
            titulo="Trabalho",
            logradouro="Av Principal",
            numero="456",
            bairro="Comercial",
            cidade="Rio de Janeiro",
            uf="RJ",
            cep="20000-000",
            complemento=None,
            usuario=None,
        )
        endereco_id = endereco_repo.inserir(endereco)

        assert endereco_id is not None

        # Verificar que complemento pode ser None
        end_recuperado = endereco_repo.obter_por_id(endereco_id)
        assert end_recuperado.complemento is None

    def test_inserir_endereco_usuario_inexistente(self):
        """Testa inserção com FK inválida (deve falhar)"""
        endereco = Endereco(
            id=0,
            id_usuario=99999,  # Usuário inexistente
            titulo="Teste",
            logradouro="Rua Teste",
            numero="1",
            bairro="Teste",
            cidade="Teste",
            uf="SP",
            cep="00000-000",
            usuario=None,
        )

        with pytest.raises(Exception):
            endereco_repo.inserir(endereco)

    def test_inserir_endereco_todos_campos(self, usuario_teste):
        """Testa inserção com todos os campos preenchidos"""
        endereco = Endereco(
            id=0,
            id_usuario=usuario_teste,
            titulo="Casa de Praia",
            logradouro="Avenida Beira Mar",
            numero="789",
            bairro="Praia Grande",
            cidade="Santos",
            uf="SP",
            cep="11065-001",
            complemento="Casa 2, Condomínio Sol",
            usuario=None,
        )
        endereco_id = endereco_repo.inserir(endereco)
        assert endereco_id is not None


class TestAlterar:
    """Testes de alteração de endereços"""

    def test_alterar_endereco_existente(self, usuario_teste):
        """Testa alteração de endereço existente"""
        # Criar endereço
        endereco = Endereco(
            id=0,
            id_usuario=usuario_teste,
            titulo="Original",
            logradouro="Rua Original",
            numero="100",
            bairro="Bairro Original",
            cidade="Cidade Original",
            uf="MG",
            cep="30000-000",
            usuario=None,
        )
        end_id = endereco_repo.inserir(endereco)

        # Alterar
        endereco_alterado = Endereco(
            id=end_id,
            id_usuario=usuario_teste,
            titulo="Alterado",
            logradouro="Rua Alterada",
            numero="200",
            bairro="Bairro Novo",
            cidade="Cidade Nova",
            uf="RJ",
            cep="20000-000",
            complemento="Novo complemento",
            usuario=None,
        )
        resultado = endereco_repo.alterar(endereco_alterado)

        assert resultado is True

        # Verificar alteração
        end_recuperado = endereco_repo.obter_por_id(end_id)
        assert end_recuperado.titulo == "Alterado"
        assert end_recuperado.logradouro == "Rua Alterada"
        assert end_recuperado.uf == "RJ"

    def test_alterar_endereco_inexistente(self, usuario_teste):
        """Testa alteração de endereço que não existe"""
        endereco = Endereco(
            id=99999,
            id_usuario=usuario_teste,
            titulo="Inexistente",
            logradouro="Rua Teste",
            numero="1",
            bairro="Teste",
            cidade="Teste",
            uf="SP",
            cep="00000-000",
            usuario=None,
        )
        resultado = endereco_repo.alterar(endereco)

        assert resultado is False


class TestExcluir:
    """Testes de exclusão de endereços"""

    def test_excluir_endereco_existente(self, usuario_teste):
        """Testa exclusão de endereço existente"""
        endereco = Endereco(
            id=0,
            id_usuario=usuario_teste,
            titulo="ParaExcluir",
            logradouro="Rua Excluir",
            numero="999",
            bairro="Bairro",
            cidade="Cidade",
            uf="SP",
            cep="99999-999",
            usuario=None,
        )
        end_id = endereco_repo.inserir(endereco)

        resultado = endereco_repo.excluir(end_id)
        assert resultado is True

        # Verificar se foi excluído
        end_recuperado = endereco_repo.obter_por_id(end_id)
        assert end_recuperado is None

    def test_excluir_endereco_inexistente(self):
        """Testa exclusão de endereço que não existe"""
        resultado = endereco_repo.excluir(99999)
        assert resultado is False


class TestObterPorId:
    """Testes de busca por ID"""

    def test_obter_endereco_existente(self, usuario_teste):
        """Testa busca de endereço por ID existente"""
        endereco = Endereco(
            id=0,
            id_usuario=usuario_teste,
            titulo="BuscaId",
            logradouro="Rua Busca",
            numero="321",
            bairro="Centro",
            cidade="São Paulo",
            uf="SP",
            cep="01000-000",
            usuario=None,
        )
        end_id = endereco_repo.inserir(endereco)

        end_recuperado = endereco_repo.obter_por_id(end_id)

        assert end_recuperado is not None
        assert end_recuperado.id == end_id
        assert end_recuperado.titulo == "BuscaId"
        assert end_recuperado.id_usuario == usuario_teste

    def test_obter_endereco_inexistente(self):
        """Testa busca de endereço com ID inexistente"""
        end_recuperado = endereco_repo.obter_por_id(99999)
        assert end_recuperado is None


class TestObterPorUsuario:
    """Testes de busca por usuário"""

    def test_obter_enderecos_de_usuario(self, usuario_teste):
        """Testa busca de endereços de um usuário"""
        # Criar múltiplos endereços para o mesmo usuário
        titulos = ["Casa", "Trabalho", "Praia"]
        for titulo in titulos:
            endereco = Endereco(
                id=0,
                id_usuario=usuario_teste,
                titulo=titulo,
                logradouro=f"Rua {titulo}",
                numero="1",
                bairro="Bairro",
                cidade="Cidade",
                uf="SP",
                cep="00000-000",
                usuario=None,
            )
            endereco_repo.inserir(endereco)

        enderecos = endereco_repo.obter_por_usuario(usuario_teste)

        assert len(enderecos) >= 3
        titulos_recuperados = [e.titulo for e in enderecos]
        for titulo in titulos:
            assert titulo in titulos_recuperados

    def test_obter_enderecos_usuario_sem_enderecos(self):
        """Testa busca de endereços para usuário sem endereços"""
        usuario = Usuario(
            id=0,
            nome="Sem Endereços",
            email=f"sem_enderecos_{id(Usuario)}@test.com",
            senha=criar_hash_senha("senha123"),
            perfil="Comprador",
        )
        usuario_id = usuario_repo.inserir(usuario)

        enderecos = endereco_repo.obter_por_usuario(usuario_id)

        assert isinstance(enderecos, list)
        assert len(enderecos) == 0

    def test_obter_enderecos_ordenados_por_titulo(self, usuario_teste):
        """Testa se endereços vêm ordenados por título"""
        # Inserir em ordem não alfabética
        titulos = ["Zebra", "Alpha", "Beta"]
        for titulo in titulos:
            endereco = Endereco(
                id=0,
                id_usuario=usuario_teste,
                titulo=titulo,
                logradouro="Rua",
                numero="1",
                bairro="B",
                cidade="C",
                uf="SP",
                cep="00000-000",
                usuario=None,
            )
            endereco_repo.inserir(endereco)

        enderecos = endereco_repo.obter_por_usuario(usuario_teste)
        titulos_recuperados = [e.titulo for e in enderecos]

        # Verificar se está ordenado
        titulos_do_usuario = [t for t in titulos_recuperados if t in titulos]
        assert titulos_do_usuario == sorted(titulos_do_usuario)


class TestObterTodos:
    """Testes de listagem geral"""

    def test_obter_todos_enderecos(self, usuario_teste):
        """Testa listagem de todos os endereços"""
        # Criar alguns endereços
        for i in range(3):
            endereco = Endereco(
                id=0,
                id_usuario=usuario_teste,
                titulo=f"End{i}",
                logradouro="Rua",
                numero=str(i),
                bairro="B",
                cidade="C",
                uf="SP",
                cep="00000-000",
                usuario=None,
            )
            endereco_repo.inserir(endereco)

        enderecos = endereco_repo.obter_todos()

        assert isinstance(enderecos, list)
        assert len(enderecos) >= 3


class TestCascadeDelete:
    """Testes de deleção em cascata"""

    def test_excluir_usuario_exclui_enderecos(self):
        """Testa se excluir usuário exclui endereços (ON DELETE CASCADE)"""
        # Criar usuário
        usuario = Usuario(
            id=0,
            nome="Usuario Cascade",
            email=f"cascade_{id(Usuario)}@test.com",
            senha=criar_hash_senha("senha123"),
            perfil="Comprador",
        )
        usuario_id = usuario_repo.inserir(usuario)

        # Criar endereço
        endereco = Endereco(
            id=0,
            id_usuario=usuario_id,
            titulo="Cascade Test",
            logradouro="Rua",
            numero="1",
            bairro="B",
            cidade="C",
            uf="SP",
            cep="00000-000",
            usuario=None,
        )
        end_id = endereco_repo.inserir(endereco)

        # Excluir usuário
        usuario_repo.excluir(usuario_id)

        # Verificar se endereço foi excluído automaticamente
        end_recuperado = endereco_repo.obter_por_id(end_id)
        assert end_recuperado is None


class TestModelValidation:
    """Testes de validação do model Endereco"""

    def test_endereco_model_atributos(self):
        """Testa se o model tem os atributos corretos"""
        endereco = Endereco(
            id=1,
            id_usuario=1,
            titulo="Casa",
            logradouro="Rua A",
            numero="1",
            bairro="B",
            cidade="C",
            uf="SP",
            cep="00000-000",
            complemento="Apto 1",
            usuario=None,
        )

        assert hasattr(endereco, "id")
        assert hasattr(endereco, "id_usuario")
        assert hasattr(endereco, "titulo")
        assert hasattr(endereco, "logradouro")
        assert hasattr(endereco, "numero")
        assert hasattr(endereco, "bairro")
        assert hasattr(endereco, "cidade")
        assert hasattr(endereco, "uf")
        assert hasattr(endereco, "cep")
        assert hasattr(endereco, "complemento")
        assert hasattr(endereco, "usuario")


class TestIntegracaoCompleta:
    """Testes de fluxo completo"""

    def test_fluxo_crud_completo(self, usuario_teste):
        """Testa fluxo completo: criar, ler, atualizar, excluir"""
        # CREATE
        endereco = Endereco(
            id=0,
            id_usuario=usuario_teste,
            titulo="FluxoCRUD",
            logradouro="Rua Fluxo",
            numero="100",
            bairro="Bairro Fluxo",
            cidade="Cidade Fluxo",
            uf="SP",
            cep="12345-678",
            usuario=None,
        )
        end_id = endereco_repo.inserir(endereco)
        assert end_id is not None

        # READ
        end_lido = endereco_repo.obter_por_id(end_id)
        assert end_lido is not None
        assert end_lido.titulo == "FluxoCRUD"

        # UPDATE
        end_atualizado = Endereco(
            id=end_id,
            id_usuario=usuario_teste,
            titulo="FluxoCRUD_Atualizado",
            logradouro="Rua Nova",
            numero="200",
            bairro="Novo Bairro",
            cidade="Nova Cidade",
            uf="RJ",
            cep="98765-432",
            complemento="Novo complemento",
            usuario=None,
        )
        resultado = endereco_repo.alterar(end_atualizado)
        assert resultado is True

        end_verificado = endereco_repo.obter_por_id(end_id)
        assert end_verificado.titulo == "FluxoCRUD_Atualizado"
        assert end_verificado.uf == "RJ"

        # DELETE
        resultado = endereco_repo.excluir(end_id)
        assert resultado is True

        end_excluido = endereco_repo.obter_por_id(end_id)
        assert end_excluido is None
