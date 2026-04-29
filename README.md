# Fut Manager - Jogador

API REST responsavel pelo modulo de jogadores do Fut Manager.

## Rodando localmente

```bash
pip install -r requirements.txt
fastapi dev app/main.py
```

A documentacao interativa fica em `http://127.0.0.1:8000/docs`.

## Banco de dados

A API le os jogadores de uma tabela SQL chamada `jogadores`. Ela nao cria
jogadores em codigo; os registros devem existir no banco usado pelo projeto.

Por padrao, a aplicacao usa SQLite em `sqlite:///./jogadores.db`. Para usar
outro banco, defina a variavel `DATABASE_URL` antes de iniciar a API:

```bash
set DATABASE_URL=sqlite:///./jogadores.db
fastapi dev app/main.py
```

O arquivo `schema.sql` mostra a estrutura esperada da tabela.

## Modelo de jogador

```json
{
  "id": 1,
  "nome": "Rafael Nunes",
  "valor": 8500000,
  "rating": 84,
  "posicao": "GOL",
  "status": "DISPONIVEL",
  "clube_id": null
}
```

Posicoes permitidas: `ATA`, `PD`, `PE`, `MC`, `LD`, `LE`, `ZAG`, `GOL`.

## Rotas principais

| Metodo | Rota | Descricao |
| --- | --- | --- |
| `GET` | `/jogadores` | Lista todos os jogadores |
| `GET` | `/jogadores/{id}` | Busca um jogador especifico |
| `POST` | `/jogadores/{id}/buy` | Compra um jogador para um clube |
| `POST` | `/jogadores/{id}/sell` | Vende/libera um jogador |
| `GET` | `/health` | Verifica se a API esta online |

### Comprar jogador

```bash
curl -X POST http://127.0.0.1:8000/jogadores/1/buy \
  -H "Content-Type: application/json" \
  -d "{\"clube_id\": 42}"
```

### Vender jogador

```bash
curl -X POST http://127.0.0.1:8000/jogadores/1/sell \
  -H "Content-Type: application/json" \
  -d "{\"clube_id\": 42}"
```

Tambem existem aliases em ingles com `/players`.
