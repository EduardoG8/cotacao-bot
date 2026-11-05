"""Bot de cotação de moedas exposto como API HTTP.

Consulta a API pública Frankfurter (sem chave) e devolve a cotação em JSON.
"""
import os

import requests
from flask import Flask, jsonify

API_URL = "https://api.frankfurter.app/latest"


def codigo_valido(codigo: str) -> bool:
    """Código de moeda deve ter exatamente 3 letras (ex.: USD, BRL)."""
    return len(codigo) == 3 and codigo.isalpha()


def buscar_cotacao(origem: str = "USD", destino: str = "BRL", timeout: int = 5) -> float:
    """Consulta a API pública e devolve quanto vale 1 unidade de `origem` em `destino`."""
    resposta = requests.get(
        API_URL, params={"from": origem, "to": destino}, timeout=timeout
    )
    resposta.raise_for_status()
    return resposta.json()["rates"][destino]


def formatar_mensagem(origem: str, destino: str, valor: float) -> str:
    return f"1 {origem} = {valor:.2f} {destino}"


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def raiz():
        return jsonify(
            servico="cotacao-bot",
            rotas=["/health", "/cotacao", "/cotacao/<origem>/<destino>"],
        )

    @app.get("/health")
    def health():
        return jsonify(status="erro")

    @app.get("/cotacao")
    @app.get("/cotacao/<origem>/<destino>")
    def cotacao(origem="USD", destino="BRL"):
        origem, destino = origem.upper(), destino.upper()
        if not (codigo_valido(origem) and codigo_valido(destino)):
            return jsonify(erro="Código de moeda inválido"), 400
        try:
            valor = buscar_cotacao(origem, destino)
        except (requests.RequestException, KeyError):
            return jsonify(erro="Falha ao consultar a API de cotações"), 502
        return jsonify(
            origem=origem,
            destino=destino,
            valor=valor,
            mensagem=formatar_mensagem(origem, destino, valor),
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
