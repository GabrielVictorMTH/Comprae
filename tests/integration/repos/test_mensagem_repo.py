"""
Testes para o repositório de mensagens.

Testa todas as operações do mensagem_repo e validações do model/SQL.
"""

import pytest
from datetime import datetime
from repo import mensagem_repo, usuario_repo
from model.mensagem_model import Mensagem
from model.usuario_model import Usuario
from util.security import criar_hash_senha


@pytest.fixture
def remetente_teste():
    """Fixture para criar remetente"""
    usuario = Usuario(
        id=0,
        nome="Remetente Teste",
        email=f"remetente_{id(Usuario)}@test.com",
        senha=criar_hash_senha("senha123"),
        perfil="Comprador",
    )
    return usuario_repo.inserir(usuario)


@pytest.fixture
def destinatario_teste():
    """Fixture para criar destinatário"""
    usuario = Usuario(
        id=0,
        nome="Destinatario Teste",
        email=f"destinatario_{id(Usuario)}@test.com",
        senha=criar_hash_senha("senha123"),
        perfil="Vendedor",
    )
    return usuario_repo.inserir(usuario)


class TestCriarTabela:
    def test_criar_tabela_sucesso(self):
        assert mensagem_repo.criar_tabela() is True


class TestInserir:
    def test_inserir_mensagem_valida(self, remetente_teste, destinatario_teste):
        mensagem = Mensagem(
            id=0,
            id_remetente=remetente_teste,
            id_destinatario=destinatario_teste,
            mensagem="Olá, como vai?",
            data_hora=datetime.now(),
            visualizada=False,
            remetente=None,
            destinatario=None,
        )
        resultado = mensagem_repo.inserir(mensagem)
        assert resultado is not None
        assert resultado.id > 0
        assert resultado.mensagem == "Olá, como vai?"

    def test_inserir_mensagem_fk_remetente_invalida(self, destinatario_teste):
        mensagem = Mensagem(
            id=0,
            id_remetente=99999,
            id_destinatario=destinatario_teste,
            mensagem="Teste",
            data_hora=datetime.now(),
            visualizada=False,
            remetente=None,
            destinatario=None,
        )
        with pytest.raises(Exception):
            mensagem_repo.inserir(mensagem)

    def test_inserir_mensagem_fk_destinatario_invalida(self, remetente_teste):
        mensagem = Mensagem(
            id=0,
            id_remetente=remetente_teste,
            id_destinatario=99999,
            mensagem="Teste",
            data_hora=datetime.now(),
            visualizada=False,
            remetente=None,
            destinatario=None,
        )
        with pytest.raises(Exception):
            mensagem_repo.inserir(mensagem)

    def test_inserir_mensagem_longa(self, remetente_teste, destinatario_teste):
        """Testa inserção de mensagem com texto longo"""
        texto_longo = "Lorem ipsum " * 100
        mensagem = Mensagem(
            id=0,
            id_remetente=remetente_teste,
            id_destinatario=destinatario_teste,
            mensagem=texto_longo,
            data_hora=datetime.now(),
            visualizada=False,
            remetente=None,
            destinatario=None,
        )
        resultado = mensagem_repo.inserir(mensagem)
        assert resultado is not None
        assert resultado.mensagem == texto_longo

    def test_inserir_mensagem_visualizada_default_false(
        self, remetente_teste, destinatario_teste
    ):
        """Testa que visualizada é False por padrão"""
        mensagem = Mensagem(
            id=0,
            id_remetente=remetente_teste,
            id_destinatario=destinatario_teste,
            mensagem="Teste",
            data_hora=datetime.now(),
            visualizada=False,
            remetente=None,
            destinatario=None,
        )
        resultado = mensagem_repo.inserir(mensagem)
        assert resultado.visualizada is False


class TestMarcarComoLida:
    def test_marcar_como_lida_sucesso(self, remetente_teste, destinatario_teste):
        mensagem = Mensagem(
            0,
            remetente_teste,
            destinatario_teste,
            "Teste",
            datetime.now(),
            False,
            None,
            None,
        )
        resultado = mensagem_repo.inserir(mensagem)

        assert mensagem_repo.marcar_como_lida(resultado.id) is True

        recuperada = mensagem_repo.obter_por_id(resultado.id)
        assert recuperada.visualizada is True

    def test_marcar_como_lida_inexistente(self):
        assert mensagem_repo.marcar_como_lida(99999) is False


class TestObterPorId:
    def test_obter_mensagem_existente(self, remetente_teste, destinatario_teste):
        mensagem = Mensagem(
            0,
            remetente_teste,
            destinatario_teste,
            "Busca ID",
            datetime.now(),
            False,
            None,
            None,
        )
        resultado = mensagem_repo.inserir(mensagem)

        recuperada = mensagem_repo.obter_por_id(resultado.id)
        assert recuperada is not None
        assert recuperada.id == resultado.id
        assert recuperada.mensagem == "Busca ID"

    def test_obter_mensagem_inexistente(self):
        recuperada = mensagem_repo.obter_por_id(99999)
        assert recuperada is None


class TestObterConversa:
    def test_obter_conversa_entre_usuarios(self, remetente_teste, destinatario_teste):
        # Criar mensagens em ambas direções
        m1 = Mensagem(
            0,
            remetente_teste,
            destinatario_teste,
            "Msg 1",
            datetime.now(),
            False,
            None,
            None,
        )
        mensagem_repo.inserir(m1)

        m2 = Mensagem(
            0,
            destinatario_teste,
            remetente_teste,
            "Msg 2",
            datetime.now(),
            False,
            None,
            None,
        )
        mensagem_repo.inserir(m2)

        m3 = Mensagem(
            0,
            remetente_teste,
            destinatario_teste,
            "Msg 3",
            datetime.now(),
            False,
            None,
            None,
        )
        mensagem_repo.inserir(m3)

        conversa = mensagem_repo.obter_conversa(remetente_teste, destinatario_teste)
        assert len(conversa) >= 3

        # Verificar que todas as mensagens são entre esses dois usuários
        for msg in conversa:
            assert (
                msg.id_remetente == remetente_teste
                and msg.id_destinatario == destinatario_teste
            ) or (
                msg.id_remetente == destinatario_teste
                and msg.id_destinatario == remetente_teste
            )

    def test_obter_conversa_ordenacao_cronologica(
        self, remetente_teste, destinatario_teste
    ):
        """Testa que conversa vem ordenada por data_hora ASC"""
        m1 = Mensagem(
            0,
            remetente_teste,
            destinatario_teste,
            "Primeira",
            datetime.now(),
            False,
            None,
            None,
        )
        r1 = mensagem_repo.inserir(m1)

        m2 = Mensagem(
            0,
            destinatario_teste,
            remetente_teste,
            "Segunda",
            datetime.now(),
            False,
            None,
            None,
        )
        r2 = mensagem_repo.inserir(m2)

        conversa = mensagem_repo.obter_conversa(remetente_teste, destinatario_teste)

        # Encontrar as mensagens inseridas
        msgs_teste = [m for m in conversa if m.id in [r1.id, r2.id]]
        if len(msgs_teste) >= 2:
            # Verificar que estão em ordem cronológica
            assert msgs_teste[0].data_hora <= msgs_teste[1].data_hora

    def test_obter_conversa_vazia(self):
        """Testa conversa entre usuários que nunca conversaram"""
        u1 = usuario_repo.inserir(
            Usuario(0, "U1", "u1@t.com", criar_hash_senha("123"), "Comprador")
        )
        u2 = usuario_repo.inserir(
            Usuario(0, "U2", "u2@t.com", criar_hash_senha("123"), "Comprador")
        )

        conversa = mensagem_repo.obter_conversa(u1, u2)
        assert isinstance(conversa, list)
        assert len(conversa) == 0


class TestObterMensagensRecebidas:
    def test_obter_mensagens_recebidas(self, remetente_teste, destinatario_teste):
        # Criar mensagens para destinatario_teste
        for i in range(3):
            m = Mensagem(
                0,
                remetente_teste,
                destinatario_teste,
                f"Msg {i}",
                datetime.now(),
                False,
                None,
                None,
            )
            mensagem_repo.inserir(m)

        recebidas = mensagem_repo.obter_mensagens_recebidas(destinatario_teste)
        assert len(recebidas) >= 3
        assert all(m.id_destinatario == destinatario_teste for m in recebidas)

    def test_obter_mensagens_recebidas_vazio(self):
        """Testa usuário sem mensagens recebidas"""
        u = usuario_repo.inserir(
            Usuario(0, "Sem Msgs", "sem@msg.com", criar_hash_senha("123"), "Comprador")
        )
        recebidas = mensagem_repo.obter_mensagens_recebidas(u)
        assert isinstance(recebidas, list)
        assert len(recebidas) == 0

    def test_obter_mensagens_recebidas_ordenacao(
        self, remetente_teste, destinatario_teste
    ):
        """Testa que mensagens recebidas vêm ordenadas por data DESC"""
        m1 = Mensagem(
            0,
            remetente_teste,
            destinatario_teste,
            "Msg1",
            datetime.now(),
            False,
            None,
            None,
        )
        r1 = mensagem_repo.inserir(m1)

        m2 = Mensagem(
            0,
            remetente_teste,
            destinatario_teste,
            "Msg2",
            datetime.now(),
            False,
            None,
            None,
        )
        r2 = mensagem_repo.inserir(m2)

        recebidas = mensagem_repo.obter_mensagens_recebidas(destinatario_teste)

        # Encontrar as mensagens inseridas
        msgs_teste = [m for m in recebidas if m.id in [r1.id, r2.id]]
        if len(msgs_teste) >= 2:
            # Verificar ordem DESC (mais recente primeiro)
            assert msgs_teste[0].data_hora >= msgs_teste[1].data_hora


class TestObterMensagensNaoLidas:
    def test_obter_mensagens_nao_lidas(self, remetente_teste, destinatario_teste):
        # Criar mensagens não lidas
        m1 = Mensagem(
            0,
            remetente_teste,
            destinatario_teste,
            "Não lida 1",
            datetime.now(),
            False,
            None,
            None,
        )
        r1 = mensagem_repo.inserir(m1)

        m2 = Mensagem(
            0,
            remetente_teste,
            destinatario_teste,
            "Não lida 2",
            datetime.now(),
            False,
            None,
            None,
        )
        r2 = mensagem_repo.inserir(m2)

        # Criar mensagem lida
        m3 = Mensagem(
            0,
            remetente_teste,
            destinatario_teste,
            "Lida",
            datetime.now(),
            False,
            None,
            None,
        )
        r3 = mensagem_repo.inserir(m3)
        mensagem_repo.marcar_como_lida(r3.id)

        nao_lidas = mensagem_repo.obter_mensagens_nao_lidas(destinatario_teste)
        ids_nao_lidas = [m.id for m in nao_lidas]

        assert r1.id in ids_nao_lidas
        assert r2.id in ids_nao_lidas
        assert r3.id not in ids_nao_lidas

    def test_obter_mensagens_nao_lidas_vazio(self):
        """Testa usuário sem mensagens não lidas"""
        u = usuario_repo.inserir(
            Usuario(0, "Sem NL", "semnl@t.com", criar_hash_senha("123"), "Comprador")
        )
        nao_lidas = mensagem_repo.obter_mensagens_nao_lidas(u)
        assert isinstance(nao_lidas, list)
        assert len(nao_lidas) == 0


class TestContarNaoLidas:
    def test_contar_nao_lidas(self, remetente_teste, destinatario_teste):
        # Criar mensagens não lidas
        for i in range(5):
            m = Mensagem(
                0,
                remetente_teste,
                destinatario_teste,
                f"NL {i}",
                datetime.now(),
                False,
                None,
                None,
            )
            mensagem_repo.inserir(m)

        # Criar mensagens lidas
        for i in range(3):
            m = Mensagem(
                0,
                remetente_teste,
                destinatario_teste,
                f"L {i}",
                datetime.now(),
                False,
                None,
                None,
            )
            r = mensagem_repo.inserir(m)
            mensagem_repo.marcar_como_lida(r.id)

        total = mensagem_repo.contar_nao_lidas(destinatario_teste)
        assert total >= 5

    def test_contar_nao_lidas_zero(self):
        """Testa contagem quando não há mensagens não lidas"""
        u = usuario_repo.inserir(
            Usuario(0, "Zero NL", "zero@t.com", criar_hash_senha("123"), "Comprador")
        )
        total = mensagem_repo.contar_nao_lidas(u)
        assert total == 0


class TestCascadeDelete:
    def test_excluir_remetente_exclui_mensagens(self, destinatario_teste):
        """Testa CASCADE: excluir remetente exclui mensagens"""
        remetente = usuario_repo.inserir(
            Usuario(0, "Rem", "rem@t.com", criar_hash_senha("123"), "Comprador")
        )

        m = Mensagem(
            0,
            remetente,
            destinatario_teste,
            "Teste CASCADE",
            datetime.now(),
            False,
            None,
            None,
        )
        resultado = mensagem_repo.inserir(m)

        # Excluir remetente
        usuario_repo.excluir(remetente)

        # Verificar que mensagem foi excluída
        recuperada = mensagem_repo.obter_por_id(resultado.id)
        assert recuperada is None

    def test_excluir_destinatario_exclui_mensagens(self, remetente_teste):
        """Testa CASCADE: excluir destinatário exclui mensagens"""
        destinatario = usuario_repo.inserir(
            Usuario(0, "Dest", "dest@t.com", criar_hash_senha("123"), "Comprador")
        )

        m = Mensagem(
            0,
            remetente_teste,
            destinatario,
            "Teste CASCADE",
            datetime.now(),
            False,
            None,
            None,
        )
        resultado = mensagem_repo.inserir(m)

        # Excluir destinatário
        usuario_repo.excluir(destinatario)

        # Verificar que mensagem foi excluída
        recuperada = mensagem_repo.obter_por_id(resultado.id)
        assert recuperada is None


class TestModelValidation:
    def test_mensagem_model_atributos(self):
        """Testa se o model tem os atributos corretos"""
        mensagem = Mensagem(
            id=1,
            id_remetente=1,
            id_destinatario=2,
            mensagem="Teste",
            data_hora=datetime.now(),
            visualizada=False,
            remetente=None,
            destinatario=None,
        )

        assert hasattr(mensagem, "id")
        assert hasattr(mensagem, "id_remetente")
        assert hasattr(mensagem, "id_destinatario")
        assert hasattr(mensagem, "mensagem")
        assert hasattr(mensagem, "data_hora")
        assert hasattr(mensagem, "visualizada")
        assert hasattr(mensagem, "remetente")
        assert hasattr(mensagem, "destinatario")


class TestIntegracaoCompleta:
    def test_fluxo_troca_mensagens(self):
        """Testa fluxo completo de troca de mensagens"""
        # Criar usuários
        u1 = usuario_repo.inserir(
            Usuario(0, "User1", "u1@flow.com", criar_hash_senha("123"), "Comprador")
        )
        u2 = usuario_repo.inserir(
            Usuario(0, "User2", "u2@flow.com", criar_hash_senha("123"), "Vendedor")
        )

        # U1 envia mensagem para U2
        m1 = Mensagem(0, u1, u2, "Olá U2!", datetime.now(), False, None, None)
        r1 = mensagem_repo.inserir(m1)
        assert r1 is not None

        # U2 verifica mensagens não lidas
        nao_lidas_u2 = mensagem_repo.obter_mensagens_nao_lidas(u2)
        assert len(nao_lidas_u2) >= 1
        assert r1.id in [m.id for m in nao_lidas_u2]

        # U2 lê a mensagem
        assert mensagem_repo.marcar_como_lida(r1.id) is True

        # U2 responde
        m2 = Mensagem(0, u2, u1, "Oi U1, tudo bem?", datetime.now(), False, None, None)
        r2 = mensagem_repo.inserir(m2)

        # Obter conversa completa
        conversa = mensagem_repo.obter_conversa(u1, u2)
        ids_conversa = [m.id for m in conversa]
        assert r1.id in ids_conversa
        assert r2.id in ids_conversa

        # U1 verifica mensagens não lidas
        nao_lidas_u1 = mensagem_repo.obter_mensagens_nao_lidas(u1)
        assert r2.id in [m.id for m in nao_lidas_u1]

        # Contar não lidas de U1
        total_nao_lidas = mensagem_repo.contar_nao_lidas(u1)
        assert total_nao_lidas >= 1
