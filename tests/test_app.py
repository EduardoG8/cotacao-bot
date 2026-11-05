import pytest
import requests

from bot import app as bot_app


@pytest.fixture
def client():
    return bot_app.create_app().test_client()


def test_formatar_mensagem():
    assert bot_app.formatar_mensagem("USD", "BRL", 5.4321) == "1 USD = 9.99 BRL"


def test_codigo_valido():
    assert bot_app.codigo_valido("USD")
    assert not bot_app.codigo_valido("US")
    assert not bot_app.codigo_valido("U5D")


def test_health(client):
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.get_json() == {"status": "ok"}


def test_buscar_cotacao_le_a_resposta_da_api(monkeypatch):
    class RespostaFalsa:
        def raise_for_status(self):
            pass

        def json(self):
            return {"rates": {"BRL": 5.5}}

    monkeypatch.setattr(bot_app.requests, "get", lambda *a, **k: RespostaFalsa())
    assert bot_app.buscar_cotacao("USD", "BRL") == 5.5


def test_rota_cotacao_sucesso(client, monkeypatch):
    monkeypatch.setattr(bot_app, "buscar_cotacao", lambda o, d: 5.0)
    resposta = client.get("/cotacao/usd/brl")
    dados = resposta.get_json()
    assert resposta.status_code == 200
    assert dados["valor"] == 5.0
    assert dados["mensagem"] == "1 USD = 5.00 BRL"


def test_rota_cotacao_moeda_invalida(client):
    resposta = client.get("/cotacao/US/brl")
    assert resposta.status_code == 400


def test_rota_cotacao_api_fora_do_ar(client, monkeypatch):
    def falha(origem, destino):
        raise requests.ConnectionError("sem rede")

    monkeypatch.setattr(bot_app, "buscar_cotacao", falha)
    resposta = client.get("/cotacao")
    assert resposta.status_code == 502
