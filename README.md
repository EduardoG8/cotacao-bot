# cotacao-bot

Bot de cotação de moedas exposto como API HTTP, usado como projeto do trabalho **CI/CD na prática** (DevOps Tools) com **CircleCI**.

O bot consulta a API pública [Frankfurter](https://www.frankfurter.app/) (sem chave) e devolve a cotação em JSON.

## Rotas

| Rota | Descrição |
|---|---|
| `GET /` | Informações do serviço |
| `GET /health` | Verificação de saúde (`{"status": "ok"}`) |
| `GET /cotacao` | Cotação padrão USD → BRL |
| `GET /cotacao/<origem>/<destino>` | Ex.: `/cotacao/eur/brl` |

## Pipeline

```
git push → build-test (ruff + pytest) → docker-publish (Docker Hub) → deploy
```

- Todo **push** e todo **pull request** rodam o job `build-test`.
- Apenas a branch **main** executa `docker-publish` e `deploy`.
- Configuração em `.circleci/config.yml`.

## Como rodar localmente

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m bot.app
```

Abra http://localhost:8000/cotacao.

## Como testar

```bash
ruff check .
pytest -v
```

Os testes usam *mocks*, então não dependem de internet.

## Como rodar com Docker

```bash
docker build -t cotacao-bot .
docker run -p 8000:8000 cotacao-bot
```

## Como configurar o CircleCI

1. Crie uma conta em https://circleci.com e conecte ao GitHub.
2. Em **Projects**, clique em **Set Up Project** no repositório e escolha a opção de usar o arquivo de configuração já existente na branch `main`.
3. Em **Project Settings → Environment Variables**, cadastre os segredos (nunca no código):

| Variável | Valor |
|---|---|
| `DOCKERHUB_USER` | seu usuário do Docker Hub |
| `DOCKERHUB_TOKEN` | token de acesso criado no Docker Hub (Account Settings → Security) |
| `DEPLOY_HOOK_URL` | URL do deploy hook do serviço de hospedagem |

## Como fazer o deploy

1. No serviço de hospedagem escolhido (ex.: Render), crie um **Web Service** a partir de uma imagem existente: `docker.io/<seu-usuario>/cotacao-bot:latest`.
2. Copie o **Deploy Hook** do serviço e cadastre como `DEPLOY_HOOK_URL` no CircleCI.
3. A cada push na `main`, o pipeline publica a imagem e chama o hook, que atualiza o container.

**URL da aplicação publicada:** _(preencher após o deploy)_

## Demonstração (falha provocada e correção)

1. Em `tests/test_app.py`, altere o valor esperado em `test_formatar_mensagem` (ex.: `"1 USD = 9.99 BRL"`).
2. Faça commit e push: o pipeline fica **vermelho** no `build-test`.
3. Reverta a alteração, faça commit e push: o pipeline fica **verde** e o deploy acontece.

## Equipe

_(nomes dos integrantes)_
