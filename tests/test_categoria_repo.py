"""
Testes para o repositório de categorias.

Testa todas as operações CRUD do categoria_repo e validações do model/SQL.
"""
import pytest
from repo import categoria_repo
from model.categoria_model import Categoria


class TestCriarTabela:
    """Testes de criação de tabela"""

    def test_criar_tabela_sucesso(self):
        """Testa criação da tabela categoria"""
        resultado = categoria_repo.criar_tabela()
        assert resultado is True


class TestInserir:
    """Testes de inserção de categorias"""

    def test_inserir_categoria_valida(self):
        """Testa inserção de categoria válida"""
        categoria = Categoria(id=0, nome="Eletrônicos", descricao="Produtos eletrônicos")
        categoria_id = categoria_repo.inserir(categoria)

        assert categoria_id is not None
        assert categoria_id > 0

    def test_inserir_categoria_nome_unico(self):
        """Testa constraint UNIQUE no nome da categoria"""
        cat1 = Categoria(id=0, nome="Livros", descricao="Primeira")
        cat2 = Categoria(id=0, nome="Livros", descricao="Segunda")

        id1 = categoria_repo.inserir(cat1)
        assert id1 is not None

        # Segunda inserção deve falhar (UNIQUE constraint)
        with pytest.raises(Exception):
            categoria_repo.inserir(cat2)

    def test_inserir_categoria_com_nome_longo(self):
        """Testa inserção de categoria com nome extenso"""
        nome_longo = "A" * 100  # Limite do DTO é 50, mas SQL aceita TEXT
        categoria = Categoria(id=0, nome=nome_longo, descricao="Teste")
        categoria_id = categoria_repo.inserir(categoria)

        assert categoria_id is not None

    def test_inserir_categoria_com_descricao_longa(self):
        """Testa inserção com descrição extensa"""
        descricao_longa = "B" * 500
        categoria = Categoria(id=0, nome="TesteLongo", descricao=descricao_longa)
        categoria_id = categoria_repo.inserir(categoria)

        assert categoria_id is not None


class TestAlterar:
    """Testes de alteração de categorias"""

    def test_alterar_categoria_existente(self):
        """Testa alteração de categoria existente"""
        # Criar categoria
        cat = Categoria(id=0, nome="Original", descricao="Descrição original")
        cat_id = categoria_repo.inserir(cat)

        # Alterar
        cat_alterada = Categoria(id=cat_id, nome="Alterada", descricao="Nova descrição")
        resultado = categoria_repo.alterar(cat_alterada)

        assert resultado is True

        # Verificar alteração
        cat_recuperada = categoria_repo.obter_por_id(cat_id)
        assert cat_recuperada is not None
        assert cat_recuperada.nome == "Alterada"
        assert cat_recuperada.descricao == "Nova descrição"

    def test_alterar_categoria_inexistente(self):
        """Testa alteração de categoria que não existe"""
        cat = Categoria(id=99999, nome="Inexistente", descricao="Teste")
        resultado = categoria_repo.alterar(cat)

        assert resultado is False

    def test_alterar_categoria_nome_duplicado(self):
        """Testa alteração para nome já existente (UNIQUE)"""
        cat1 = Categoria(id=0, nome="Categoria1", descricao="Desc1")
        cat2 = Categoria(id=0, nome="Categoria2", descricao="Desc2")

        id1 = categoria_repo.inserir(cat1)
        id2 = categoria_repo.inserir(cat2)

        # Tentar alterar cat2 para ter o mesmo nome de cat1
        cat2_alterada = Categoria(id=id2, nome="Categoria1", descricao="Nova desc")

        with pytest.raises(Exception):
            categoria_repo.alterar(cat2_alterada)


class TestExcluir:
    """Testes de exclusão de categorias"""

    def test_excluir_categoria_existente(self):
        """Testa exclusão de categoria existente"""
        cat = Categoria(id=0, nome="ParaExcluir", descricao="Será removida")
        cat_id = categoria_repo.inserir(cat)

        resultado = categoria_repo.excluir(cat_id)
        assert resultado is True

        # Verificar se foi excluída
        cat_recuperada = categoria_repo.obter_por_id(cat_id)
        assert cat_recuperada is None

    def test_excluir_categoria_inexistente(self):
        """Testa exclusão de categoria que não existe"""
        resultado = categoria_repo.excluir(99999)
        assert resultado is False

    def test_excluir_categoria_com_anuncios_vinculados(self):
        """Testa exclusão de categoria com anúncios (deve falhar por FK RESTRICT)"""
        from repo import anuncio_repo, usuario_repo
        from model.anuncio_model import Anuncio
        from model.usuario_model import Usuario
        from util.security import criar_hash_senha
        from datetime import datetime

        # Criar usuário vendedor
        usuario = Usuario(
            id=0,
            nome="Vendedor Teste",
            email="vendedor_cat_test@test.com",
            senha=criar_hash_senha("senha123"),
            perfil="Vendedor"
        )
        usuario_id = usuario_repo.inserir(usuario)

        # Criar categoria
        cat = Categoria(id=0, nome="CategoriaComAnuncio", descricao="Tem anúncios")
        cat_id = categoria_repo.inserir(cat)

        # Criar anúncio vinculado
        anuncio = Anuncio(
            id_anuncio=0,
            id_vendedor=usuario_id,
            id_categoria=cat_id,
            nome="Produto Teste",
            descricao="Descrição do produto teste",
            peso=1.5,
            preco=100.0,
            estoque=10,
            data_cadastro=datetime.now(),
            ativo=True,
            vendedor=None,
            categoria=None
        )
        anuncio_repo.inserir(anuncio)

        # Tentar excluir categoria (deve falhar por FK RESTRICT)
        with pytest.raises(Exception):
            categoria_repo.excluir(cat_id)


class TestObterPorId:
    """Testes de busca por ID"""

    def test_obter_categoria_existente(self):
        """Testa busca de categoria por ID existente"""
        cat = Categoria(id=0, nome="BuscaPorId", descricao="Teste de busca")
        cat_id = categoria_repo.inserir(cat)

        cat_recuperada = categoria_repo.obter_por_id(cat_id)

        assert cat_recuperada is not None
        assert cat_recuperada.id == cat_id
        assert cat_recuperada.nome == "BuscaPorId"
        assert cat_recuperada.descricao == "Teste de busca"

    def test_obter_categoria_inexistente(self):
        """Testa busca de categoria com ID inexistente"""
        cat_recuperada = categoria_repo.obter_por_id(99999)
        assert cat_recuperada is None


class TestObterTodos:
    """Testes de listagem de categorias"""

    def test_obter_todos_vazio(self):
        """Testa listagem quando não há categorias"""
        # Limpar todas as categorias primeiro
        todas = categoria_repo.obter_todos()
        for cat in todas:
            categoria_repo.excluir(cat.id)

        categorias = categoria_repo.obter_todos()
        assert isinstance(categorias, list)
        assert len(categorias) == 0

    def test_obter_todos_com_categorias(self):
        """Testa listagem com múltiplas categorias"""
        # Criar algumas categorias
        nomes = ["Cat1", "Cat2", "Cat3"]
        for nome in nomes:
            cat = Categoria(id=0, nome=nome, descricao=f"Descrição {nome}")
            categoria_repo.inserir(cat)

        categorias = categoria_repo.obter_todos()

        assert len(categorias) >= 3
        nomes_recuperados = [c.nome for c in categorias]
        for nome in nomes:
            assert nome in nomes_recuperados

    def test_obter_todos_ordenacao_por_nome(self):
        """Testa se a listagem retorna ordenada por nome"""
        # Limpar categorias
        todas = categoria_repo.obter_todos()
        for cat in todas:
            categoria_repo.excluir(cat.id)

        # Inserir em ordem não alfabética
        nomes = ["Zebra", "Alpha", "Mickey"]
        for nome in nomes:
            cat = Categoria(id=0, nome=nome, descricao=f"Desc {nome}")
            categoria_repo.inserir(cat)

        categorias = categoria_repo.obter_todos()
        nomes_recuperados = [c.nome for c in categorias]

        # Verificar se está ordenado
        assert nomes_recuperados == sorted(nomes_recuperados)


class TestModelValidation:
    """Testes de validação do model Categoria"""

    def test_categoria_model_atributos(self):
        """Testa se o model tem os atributos corretos"""
        cat = Categoria(id=1, nome="Teste", descricao="Descrição")

        assert hasattr(cat, 'id')
        assert hasattr(cat, 'nome')
        assert hasattr(cat, 'descricao')

    def test_categoria_model_tipos(self):
        """Testa tipos dos atributos"""
        cat = Categoria(id=1, nome="Teste", descricao="Descrição")

        assert isinstance(cat.id, int)
        assert isinstance(cat.nome, str)
        assert isinstance(cat.descricao, str)


class TestIntegracaoCompleta:
    """Testes de fluxo completo"""

    def test_fluxo_crud_completo(self):
        """Testa fluxo completo: criar, ler, atualizar, excluir"""
        # CREATE
        cat = Categoria(id=0, nome="FluxoCRUD", descricao="Teste completo")
        cat_id = categoria_repo.inserir(cat)
        assert cat_id is not None

        # READ
        cat_lida = categoria_repo.obter_por_id(cat_id)
        assert cat_lida is not None
        assert cat_lida.nome == "FluxoCRUD"

        # UPDATE
        cat_atualizada = Categoria(id=cat_id, nome="FluxoCRUD_Atualizado", descricao="Atualizada")
        resultado = categoria_repo.alterar(cat_atualizada)
        assert resultado is True

        cat_verificada = categoria_repo.obter_por_id(cat_id)
        assert cat_verificada.nome == "FluxoCRUD_Atualizado"

        # DELETE
        resultado = categoria_repo.excluir(cat_id)
        assert resultado is True

        cat_excluida = categoria_repo.obter_por_id(cat_id)
        assert cat_excluida is None
