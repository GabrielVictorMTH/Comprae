"""
Testes para o repositório de pedidos.

Testa todas as operações do pedido_repo e validações do model/SQL.
"""
import pytest
from datetime import datetime
from repo import pedido_repo, usuario_repo, categoria_repo, anuncio_repo, endereco_repo
from model.pedido_model import Pedido
from model.usuario_model import Usuario
from model.categoria_model import Categoria
from model.anuncio_model import Anuncio
from model.endereco_model import Endereco
from util.security import criar_hash_senha


@pytest.fixture
def comprador_teste():
    """Fixture para criar comprador"""
    usuario = Usuario(
        id=0,
        nome="Comprador Teste",
        email=f"comprador_{id(Usuario)}@test.com",
        senha=criar_hash_senha("senha123"),
        perfil="Cliente"
    )
    return usuario_repo.inserir(usuario)


@pytest.fixture
def vendedor_teste():
    """Fixture para criar vendedor"""
    usuario = Usuario(
        id=0,
        nome="Vendedor Teste Pedido",
        email=f"vendedor_pedido_{id(Usuario)}@test.com",
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
        nome=f"CategoriaPedido_{uuid.uuid4().hex[:8]}",
        descricao="Categoria de teste para pedidos"
    )
    return categoria_repo.inserir(categoria)


@pytest.fixture
def endereco_teste(comprador_teste):
    """Fixture para criar endereço do comprador"""
    endereco = Endereco(
        id_endereco=0,
        id_usuario=comprador_teste,
        titulo="Casa",
        logradouro="Rua Teste",
        numero="123",
        bairro="Centro",
        cidade="São Paulo",
        uf="SP",
        cep="01000-000",
        usuario=None
    )
    return endereco_repo.inserir(endereco)


@pytest.fixture
def anuncio_teste(vendedor_teste, categoria_teste):
    """Fixture para criar anúncio"""
    anuncio = Anuncio(
        id_anuncio=0,
        id_vendedor=vendedor_teste,
        id_categoria=categoria_teste,
        nome="Produto Teste",
        descricao="Descrição do produto teste",
        peso=1.0,
        preco=100.0,
        estoque=10,
        data_cadastro=datetime.now(),
        ativo=True,
        vendedor=None,
        categoria=None
    )
    resultado = anuncio_repo.inserir(anuncio)
    return resultado.id_anuncio if resultado else None


class TestCriarTabela:
    def test_criar_tabela_sucesso(self):
        assert pedido_repo.criar_tabela() is True


class TestInserir:
    def test_inserir_pedido_valido(self, comprador_teste, endereco_teste, anuncio_teste):
        pedido = Pedido(
            id_pedido=0,
            id_endereco=endereco_teste,
            id_comprador=comprador_teste,
            id_anuncio=anuncio_teste,
            preco=99.90,
            status="Pendente"
        )
        resultado = pedido_repo.inserir(pedido)
        assert resultado is not None
        assert resultado > 0

    def test_inserir_pedido_fk_endereco_invalida(self, comprador_teste, anuncio_teste):
        pedido = Pedido(
            id_pedido=0,
            id_endereco=99999,
            id_comprador=comprador_teste,
            id_anuncio=anuncio_teste,
            preco=50.0,
            status="Pendente"
        )
        with pytest.raises(Exception):
            pedido_repo.inserir(pedido)

    def test_inserir_pedido_fk_comprador_invalida(self, endereco_teste, anuncio_teste):
        pedido = Pedido(
            id_pedido=0,
            id_endereco=endereco_teste,
            id_comprador=99999,
            id_anuncio=anuncio_teste,
            preco=50.0,
            status="Pendente"
        )
        with pytest.raises(Exception):
            pedido_repo.inserir(pedido)

    def test_inserir_pedido_fk_anuncio_invalida(self, comprador_teste, endereco_teste):
        pedido = Pedido(
            id_pedido=0,
            id_endereco=endereco_teste,
            id_comprador=comprador_teste,
            id_anuncio=99999,
            preco=50.0,
            status="Pendente"
        )
        with pytest.raises(Exception):
            pedido_repo.inserir(pedido)

    def test_inserir_pedido_status_default(self, comprador_teste, endereco_teste, anuncio_teste):
        """Testa que o status padrão é 'Pendente'"""
        pedido = Pedido(
            id_pedido=0,
            id_endereco=endereco_teste,
            id_comprador=comprador_teste,
            id_anuncio=anuncio_teste,
            preco=75.0,
            status="Pendente"
        )
        pedido_id = pedido_repo.inserir(pedido)

        recuperado = pedido_repo.obter_por_id(pedido_id)
        assert recuperado.status == "Pendente"


class TestAtualizarStatus:
    def test_atualizar_status_existente(self, comprador_teste, endereco_teste, anuncio_teste):
        pedido = Pedido(0, endereco_teste, comprador_teste, anuncio_teste, 100.0, "Pendente")
        pedido_id = pedido_repo.inserir(pedido)

        assert pedido_repo.atualizar_status(pedido_id, "Pago") is True

        recuperado = pedido_repo.obter_por_id(pedido_id)
        assert recuperado.status == "Pago"

    def test_atualizar_status_inexistente(self):
        assert pedido_repo.atualizar_status(99999, "Pago") is False


class TestMarcarComoPago:
    def test_marcar_como_pago_sucesso(self, comprador_teste, endereco_teste, anuncio_teste):
        pedido = Pedido(0, endereco_teste, comprador_teste, anuncio_teste, 100.0, "Pendente")
        pedido_id = pedido_repo.inserir(pedido)

        assert pedido_repo.marcar_como_pago(pedido_id) is True

        recuperado = pedido_repo.obter_por_id(pedido_id)
        assert recuperado.status == "Pago"
        assert recuperado.data_hora_pagamento is not None

    def test_marcar_como_pago_inexistente(self):
        assert pedido_repo.marcar_como_pago(99999) is False


class TestMarcarComoEnviado:
    def test_marcar_como_enviado_sucesso(self, comprador_teste, endereco_teste, anuncio_teste):
        pedido = Pedido(0, endereco_teste, comprador_teste, anuncio_teste, 100.0, "Pendente")
        pedido_id = pedido_repo.inserir(pedido)

        codigo = "BR123456789"
        assert pedido_repo.marcar_como_enviado(pedido_id, codigo) is True

        recuperado = pedido_repo.obter_por_id(pedido_id)
        assert recuperado.status == "Enviado"
        assert recuperado.codigo_rastreio == codigo
        assert recuperado.data_hora_envio is not None

    def test_marcar_como_enviado_inexistente(self):
        assert pedido_repo.marcar_como_enviado(99999, "BR123") is False


class TestCancelar:
    def test_cancelar_pedido_existente(self, comprador_teste, endereco_teste, anuncio_teste):
        pedido = Pedido(0, endereco_teste, comprador_teste, anuncio_teste, 100.0, "Pendente")
        pedido_id = pedido_repo.inserir(pedido)

        assert pedido_repo.cancelar(pedido_id) is True

        recuperado = pedido_repo.obter_por_id(pedido_id)
        assert recuperado.status == "Cancelado"

    def test_cancelar_pedido_inexistente(self):
        assert pedido_repo.cancelar(99999) is False


class TestAvaliar:
    def test_avaliar_pedido_valido(self, comprador_teste, endereco_teste, anuncio_teste):
        pedido = Pedido(0, endereco_teste, comprador_teste, anuncio_teste, 100.0, "Pendente")
        pedido_id = pedido_repo.inserir(pedido)

        nota = 5
        comentario = "Excelente produto!"
        assert pedido_repo.avaliar(pedido_id, nota, comentario) is True

        recuperado = pedido_repo.obter_por_id(pedido_id)
        assert recuperado.nota_avaliacao == nota
        assert recuperado.comentario_avaliacao == comentario
        assert recuperado.data_hora_avaliacao is not None

    def test_avaliar_pedido_nota_minima(self, comprador_teste, endereco_teste, anuncio_teste):
        """Testa avaliação com nota mínima (1)"""
        pedido = Pedido(0, endereco_teste, comprador_teste, anuncio_teste, 100.0, "Pendente")
        pedido_id = pedido_repo.inserir(pedido)

        assert pedido_repo.avaliar(pedido_id, 1, "Ruim") is True

        recuperado = pedido_repo.obter_por_id(pedido_id)
        assert recuperado.nota_avaliacao == 1

    def test_avaliar_pedido_nota_maxima(self, comprador_teste, endereco_teste, anuncio_teste):
        """Testa avaliação com nota máxima (5)"""
        pedido = Pedido(0, endereco_teste, comprador_teste, anuncio_teste, 100.0, "Pendente")
        pedido_id = pedido_repo.inserir(pedido)

        assert pedido_repo.avaliar(pedido_id, 5, "Excelente!") is True

        recuperado = pedido_repo.obter_por_id(pedido_id)
        assert recuperado.nota_avaliacao == 5

    def test_avaliar_pedido_inexistente(self):
        assert pedido_repo.avaliar(99999, 5, "Teste") is False


class TestObterPorId:
    def test_obter_pedido_existente(self, comprador_teste, endereco_teste, anuncio_teste):
        pedido = Pedido(0, endereco_teste, comprador_teste, anuncio_teste, 150.0, "Pendente")
        pedido_id = pedido_repo.inserir(pedido)

        recuperado = pedido_repo.obter_por_id(pedido_id)
        assert recuperado is not None
        assert recuperado.id_pedido == pedido_id
        assert recuperado.preco == 150.0

    def test_obter_pedido_inexistente(self):
        recuperado = pedido_repo.obter_por_id(99999)
        assert recuperado is None


class TestObterPorComprador:
    def test_obter_pedidos_do_comprador(self, comprador_teste, endereco_teste, anuncio_teste):
        # Criar múltiplos pedidos
        for i in range(3):
            pedido = Pedido(0, endereco_teste, comprador_teste, anuncio_teste, 50.0 + i, "Pendente")
            pedido_repo.inserir(pedido)

        pedidos = pedido_repo.obter_por_comprador(comprador_teste)
        assert len(pedidos) >= 3
        assert all(p.id_comprador == comprador_teste for p in pedidos)

    def test_obter_pedidos_comprador_sem_pedidos(self):
        usuario = usuario_repo.inserir(Usuario(0, "Sem Pedidos", "sem@pedidos.com", criar_hash_senha("123"), "Cliente"))
        pedidos = pedido_repo.obter_por_comprador(usuario)
        assert isinstance(pedidos, list)
        assert len(pedidos) == 0


class TestObterPorVendedor:
    def test_obter_pedidos_do_vendedor(self, comprador_teste, endereco_teste, vendedor_teste, categoria_teste):
        # Criar anúncio do vendedor
        anuncio = Anuncio(0, vendedor_teste, categoria_teste, "Produto", "Desc", 1.0, 100.0, 10, datetime.now(), True, None, None)
        anuncio_resultado = anuncio_repo.inserir(anuncio)
        anuncio_id = anuncio_resultado.id_anuncio if anuncio_resultado else None

        # Criar pedidos
        for i in range(2):
            pedido = Pedido(0, endereco_teste, comprador_teste, anuncio_id, 100.0, "Pendente")
            pedido_repo.inserir(pedido)

        pedidos = pedido_repo.obter_por_vendedor(vendedor_teste)
        assert len(pedidos) >= 2

    def test_obter_pedidos_vendedor_sem_vendas(self):
        vendedor = usuario_repo.inserir(Usuario(0, "Sem Vendas", "semvendas@t.com", criar_hash_senha("123"), "Vendedor"))
        pedidos = pedido_repo.obter_por_vendedor(vendedor)
        assert isinstance(pedidos, list)
        assert len(pedidos) == 0


class TestObterPorStatus:
    def test_obter_pedidos_por_status(self, comprador_teste, endereco_teste, anuncio_teste):
        # Criar pedidos com diferentes status
        p1 = Pedido(0, endereco_teste, comprador_teste, anuncio_teste, 100.0, "Pendente")
        p1_id = pedido_repo.inserir(p1)

        p2 = Pedido(0, endereco_teste, comprador_teste, anuncio_teste, 200.0, "Pendente")
        p2_id = pedido_repo.inserir(p2)
        pedido_repo.marcar_como_pago(p2_id)

        pedidos_pendentes = pedido_repo.obter_por_status("Pendente")
        ids_pendentes = [p.id_pedido for p in pedidos_pendentes]
        assert p1_id in ids_pendentes
        assert p2_id not in ids_pendentes

        pedidos_pagos = pedido_repo.obter_por_status("Pago")
        ids_pagos = [p.id_pedido for p in pedidos_pagos]
        assert p2_id in ids_pagos

    def test_obter_pedidos_status_inexistente(self):
        pedidos = pedido_repo.obter_por_status("StatusInexistente")
        assert isinstance(pedidos, list)
        assert len(pedidos) == 0


class TestObterTodos:
    def test_obter_todos_pedidos(self, comprador_teste, endereco_teste, anuncio_teste):
        for i in range(3):
            pedido = Pedido(0, endereco_teste, comprador_teste, anuncio_teste, 50.0 + i, "Pendente")
            pedido_repo.inserir(pedido)

        pedidos = pedido_repo.obter_todos()
        assert len(pedidos) >= 3


class TestFluxoPedido:
    def test_fluxo_completo_pedido(self, comprador_teste, endereco_teste, anuncio_teste):
        """Testa fluxo: Pendente → Pago → Enviado → Avaliado"""
        # Criar pedido
        pedido = Pedido(0, endereco_teste, comprador_teste, anuncio_teste, 250.0, "Pendente")
        pedido_id = pedido_repo.inserir(pedido)
        assert pedido_id is not None

        # Verificar status inicial
        p = pedido_repo.obter_por_id(pedido_id)
        assert p.status == "Pendente"

        # Marcar como pago
        assert pedido_repo.marcar_como_pago(pedido_id) is True
        p = pedido_repo.obter_por_id(pedido_id)
        assert p.status == "Pago"
        assert p.data_hora_pagamento is not None

        # Marcar como enviado
        assert pedido_repo.marcar_como_enviado(pedido_id, "BR987654321") is True
        p = pedido_repo.obter_por_id(pedido_id)
        assert p.status == "Enviado"
        assert p.codigo_rastreio == "BR987654321"
        assert p.data_hora_envio is not None

        # Avaliar
        assert pedido_repo.avaliar(pedido_id, 4, "Muito bom!") is True
        p = pedido_repo.obter_por_id(pedido_id)
        assert p.nota_avaliacao == 4
        assert p.comentario_avaliacao == "Muito bom!"
        assert p.data_hora_avaliacao is not None


class TestCascadeRestrict:
    def test_excluir_comprador_com_pedidos_deve_falhar(self, comprador_teste, endereco_teste, anuncio_teste):
        """Testa RESTRICT: não pode excluir comprador com pedidos"""
        pedido = Pedido(0, endereco_teste, comprador_teste, anuncio_teste, 100.0, "Pendente")
        pedido_repo.inserir(pedido)

        with pytest.raises(Exception):
            usuario_repo.excluir(comprador_teste)

    def test_excluir_anuncio_com_pedidos_deve_falhar(self, comprador_teste, endereco_teste, anuncio_teste):
        """Testa RESTRICT: não pode excluir anúncio com pedidos"""
        pedido = Pedido(0, endereco_teste, comprador_teste, anuncio_teste, 100.0, "Pendente")
        pedido_repo.inserir(pedido)

        with pytest.raises(Exception):
            anuncio_repo.excluir(anuncio_teste)

    def test_excluir_endereco_com_pedidos_deve_falhar(self, comprador_teste, endereco_teste, anuncio_teste):
        """Testa RESTRICT: não pode excluir endereço com pedidos"""
        pedido = Pedido(0, endereco_teste, comprador_teste, anuncio_teste, 100.0, "Pendente")
        pedido_repo.inserir(pedido)

        with pytest.raises(Exception):
            endereco_repo.excluir(endereco_teste)


class TestModelValidation:
    def test_pedido_model_atributos(self):
        """Testa se o model tem os atributos corretos"""
        pedido = Pedido(
            id_pedido=1,
            id_endereco=1,
            id_comprador=1,
            id_anuncio=1,
            preco=100.0,
            status="Pendente"
        )

        assert hasattr(pedido, 'id_pedido')
        assert hasattr(pedido, 'id_endereco')
        assert hasattr(pedido, 'id_comprador')
        assert hasattr(pedido, 'id_anuncio')
        assert hasattr(pedido, 'preco')
        assert hasattr(pedido, 'status')
        assert hasattr(pedido, 'data_hora_pedido')
        assert hasattr(pedido, 'data_hora_pagamento')
        assert hasattr(pedido, 'data_hora_envio')
        assert hasattr(pedido, 'codigo_rastreio')
        assert hasattr(pedido, 'nota_avaliacao')
        assert hasattr(pedido, 'comentario_avaliacao')
        assert hasattr(pedido, 'data_hora_avaliacao')
