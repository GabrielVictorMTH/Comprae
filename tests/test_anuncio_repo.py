"""
Testes para o repositório de anúncios.
"""
import pytest
from datetime import datetime
from repo import anuncio_repo, usuario_repo, categoria_repo
from model.anuncio_model import Anuncio
from model.usuario_model import Usuario
from model.categoria_model import Categoria
from util.security import criar_hash_senha


@pytest.fixture
def vendedor_teste():
    """Fixture para criar vendedor"""
    usuario = Usuario(
        id=0,
        nome="Vendedor Teste",
        email=f"vendedor_{id(Usuario)}@test.com",
        senha=criar_hash_senha("senha123"),
        perfil="Vendedor"
    )
    return usuario_repo.inserir(usuario)


@pytest.fixture
def categoria_teste():
    """Fixture para criar categoria"""
    import uuid
    categoria = Categoria(
        id=0,
        nome=f"Categoria_{uuid.uuid4().hex[:8]}",
        descricao="Categoria de teste"
    )
    return categoria_repo.inserir(categoria)


class TestCriarTabela:
    def test_criar_tabela_sucesso(self):
        assert anuncio_repo.criar_tabela() is True


class TestInserir:
    def test_inserir_anuncio_valido(self, vendedor_teste, categoria_teste):
        anuncio = Anuncio(
            id_anuncio=0,
            id_vendedor=vendedor_teste,
            id_categoria=categoria_teste,
            nome="Produto Teste",
            descricao="Descrição do produto teste com mais de 10 caracteres",
            peso=1.5,
            preco=99.90,
            estoque=10,
            data_cadastro=datetime.now(),
            ativo=True,
            vendedor=None,
            categoria=None
        )
        resultado = anuncio_repo.inserir(anuncio)
        assert resultado is not None
        assert resultado.id_anuncio > 0

    def test_inserir_anuncio_fk_vendedor_invalida(self, categoria_teste):
        anuncio = Anuncio(
            id_anuncio=0,
            id_vendedor=99999,
            id_categoria=categoria_teste,
            nome="Teste",
            descricao="Descrição teste",
            peso=1.0,
            preco=10.0,
            estoque=1,
            data_cadastro=datetime.now(),
            ativo=True,
            vendedor=None,
            categoria=None
        )
        with pytest.raises(Exception):
            anuncio_repo.inserir(anuncio)

    def test_inserir_anuncio_fk_categoria_invalida(self, vendedor_teste):
        anuncio = Anuncio(
            id_anuncio=0,
            id_vendedor=vendedor_teste,
            id_categoria=99999,
            nome="Teste",
            descricao="Descrição teste",
            peso=1.0,
            preco=10.0,
            estoque=1,
            data_cadastro=datetime.now(),
            ativo=True,
            vendedor=None,
            categoria=None
        )
        with pytest.raises(Exception):
            anuncio_repo.inserir(anuncio)


class TestAlterar:
    def test_alterar_anuncio_existente(self, vendedor_teste, categoria_teste):
        anuncio = Anuncio(
            id_anuncio=0,
            id_vendedor=vendedor_teste,
            id_categoria=categoria_teste,
            nome="Original",
            descricao="Descrição original do produto",
            peso=1.0,
            preco=50.0,
            estoque=5,
            data_cadastro=datetime.now(),
            ativo=True,
            vendedor=None,
            categoria=None
        )
        resultado = anuncio_repo.inserir(anuncio)

        anuncio_alterado = Anuncio(
            id_anuncio=resultado.id_anuncio,
            id_vendedor=vendedor_teste,
            id_categoria=categoria_teste,
            nome="Alterado",
            descricao="Nova descrição do produto",
            peso=2.0,
            preco=100.0,
            estoque=10,
            data_cadastro=datetime.now(),
            ativo=False,
            vendedor=None,
            categoria=None
        )
        assert anuncio_repo.alterar(anuncio_alterado) is True

        recuperado = anuncio_repo.obter_por_id(resultado.id_anuncio)
        assert recuperado.nome == "Alterado"
        assert recuperado.preco == 100.0
        assert recuperado.ativo is False


class TestExcluir:
    def test_excluir_anuncio_existente(self, vendedor_teste, categoria_teste):
        anuncio = Anuncio(
            id_anuncio=0,
            id_vendedor=vendedor_teste,
            id_categoria=categoria_teste,
            nome="ParaExcluir",
            descricao="Será excluído",
            peso=1.0,
            preco=10.0,
            estoque=1,
            data_cadastro=datetime.now(),
            ativo=True,
            vendedor=None,
            categoria=None
        )
        resultado = anuncio_repo.inserir(anuncio)

        assert anuncio_repo.excluir(resultado.id_anuncio) is True
        assert anuncio_repo.obter_por_id(resultado.id_anuncio) is None


class TestObterPorId:
    def test_obter_anuncio_existente(self, vendedor_teste, categoria_teste):
        anuncio = Anuncio(
            id_anuncio=0,
            id_vendedor=vendedor_teste,
            id_categoria=categoria_teste,
            nome="BuscaId",
            descricao="Busca por ID",
            peso=1.0,
            preco=20.0,
            estoque=2,
            data_cadastro=datetime.now(),
            ativo=True,
            vendedor=None,
            categoria=None
        )
        resultado = anuncio_repo.inserir(anuncio)

        recuperado = anuncio_repo.obter_por_id(resultado.id_anuncio)
        assert recuperado is not None
        assert recuperado.nome == "BuscaId"


class TestObterTodos:
    def test_obter_todos_anuncios(self, vendedor_teste, categoria_teste):
        for i in range(3):
            anuncio = Anuncio(
                id_anuncio=0,
                id_vendedor=vendedor_teste,
                id_categoria=categoria_teste,
                nome=f"Anuncio{i}",
                descricao="Descrição",
                peso=1.0,
                preco=10.0,
                estoque=1,
                data_cadastro=datetime.now(),
                ativo=True,
                vendedor=None,
                categoria=None
            )
            anuncio_repo.inserir(anuncio)

        anuncios = anuncio_repo.obter_todos()
        assert len(anuncios) >= 3


class TestObterTodosAtivos:
    def test_obter_apenas_ativos(self, vendedor_teste, categoria_teste):
        # Criar ativo
        ativo = Anuncio(
            id_anuncio=0,
            id_vendedor=vendedor_teste,
            id_categoria=categoria_teste,
            nome="Ativo",
            descricao="Anúncio ativo",
            peso=1.0,
            preco=10.0,
            estoque=5,
            data_cadastro=datetime.now(),
            ativo=True,
            vendedor=None,
            categoria=None
        )
        anuncio_repo.inserir(ativo)

        # Criar inativo
        inativo = Anuncio(
            id_anuncio=0,
            id_vendedor=vendedor_teste,
            id_categoria=categoria_teste,
            nome="Inativo",
            descricao="Anúncio inativo",
            peso=1.0,
            preco=10.0,
            estoque=0,
            data_cadastro=datetime.now(),
            ativo=False,
            vendedor=None,
            categoria=None
        )
        resultado_inativo = anuncio_repo.inserir(inativo)

        ativos = anuncio_repo.obter_todos_ativos()
        ids_ativos = [a.id_anuncio for a in ativos]
        assert resultado_inativo.id_anuncio not in ids_ativos


class TestObterPorVendedor:
    def test_obter_anuncios_do_vendedor(self, categoria_teste):
        v1 = usuario_repo.inserir(Usuario(0, "V1", "v1@test.com", criar_hash_senha("123"), "Vendedor"))
        v2 = usuario_repo.inserir(Usuario(0, "V2", "v2@test.com", criar_hash_senha("123"), "Vendedor"))

        anuncio_v1 = Anuncio(0, v1, categoria_teste, "ProdV1", "Desc", 1.0, 10.0, 1, datetime.now(), True, None, None)
        anuncio_repo.inserir(anuncio_v1)

        anuncios = anuncio_repo.obter_por_vendedor(v1)
        assert len(anuncios) >= 1
        assert all(a.id_vendedor == v1 for a in anuncios)


class TestObterPorCategoria:
    def test_obter_anuncios_da_categoria(self, vendedor_teste):
        cat1 = categoria_repo.inserir(Categoria(0, "Cat1", "Categoria 1"))
        cat2 = categoria_repo.inserir(Categoria(0, "Cat2", "Categoria 2"))

        anuncio1 = Anuncio(0, vendedor_teste, cat1, "P1", "Desc", 1.0, 10.0, 1, datetime.now(), True, None, None)
        anuncio_repo.inserir(anuncio1)

        anuncios = anuncio_repo.obter_por_categoria(cat1)
        assert len(anuncios) >= 1
        assert all(a.id_categoria == cat1 for a in anuncios)


class TestBuscarPorNome:
    def test_buscar_por_termo(self, vendedor_teste, categoria_teste):
        anuncio = Anuncio(0, vendedor_teste, categoria_teste, "Notebook Dell", "Desc", 1.0, 100.0, 1, datetime.now(), True, None, None)
        anuncio_repo.inserir(anuncio)

        resultados = anuncio_repo.buscar_por_nome("Notebook")
        nomes = [a.nome for a in resultados]
        assert "Notebook Dell" in nomes


class TestAtualizarEstoque:
    def test_atualizar_estoque_suficiente(self, vendedor_teste, categoria_teste):
        anuncio = Anuncio(0, vendedor_teste, categoria_teste, "Estoque", "Desc", 1.0, 10.0, 10, datetime.now(), True, None, None)
        resultado = anuncio_repo.inserir(anuncio)

        assert anuncio_repo.atualizar_estoque(resultado.id_anuncio, 3) is True

        recuperado = anuncio_repo.obter_por_id(resultado.id_anuncio)
        assert recuperado.estoque == 7

    def test_atualizar_estoque_insuficiente(self, vendedor_teste, categoria_teste):
        anuncio = Anuncio(0, vendedor_teste, categoria_teste, "Estoque", "Desc", 1.0, 10.0, 2, datetime.now(), True, None, None)
        resultado = anuncio_repo.inserir(anuncio)

        assert anuncio_repo.atualizar_estoque(resultado.id_anuncio, 5) is False


class TestCascadeDelete:
    def test_excluir_vendedor_exclui_anuncios(self, categoria_teste):
        vendedor = usuario_repo.inserir(Usuario(0, "V", "v@t.com", criar_hash_senha("123"), "Vendedor"))
        anuncio = Anuncio(0, vendedor, categoria_teste, "P", "D", 1.0, 10.0, 1, datetime.now(), True, None, None)
        resultado = anuncio_repo.inserir(anuncio)

        usuario_repo.excluir(vendedor)
        assert anuncio_repo.obter_por_id(resultado.id_anuncio) is None
