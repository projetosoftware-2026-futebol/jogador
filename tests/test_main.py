from sqlalchemy.orm import Session

from app.database import get_db


# -- Sistema ------------------------------------------------------------------

def test_raiz(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"servico": "jogador", "status": "online"}


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_db_entrega_sessao():
    generator = get_db()
    db = next(generator)

    assert isinstance(db, Session)

    generator.close()


# -- Jogadores ----------------------------------------------------------------

def test_lista_todos_os_jogadores(client):
    response = client.get("/jogadores")

    assert response.status_code == 200
    jogadores = response.json()
    assert len(jogadores) == 19
    assert jogadores[0]["id"] == 1
    assert jogadores[0]["status"] == "DISPONIVEL"
    assert {jogador["posicao"] for jogador in jogadores} == {
        "ATA",
        "PD",
        "PE",
        "MC",
        "LD",
        "LE",
        "ZAG",
        "GOL",
    }


def test_get_alias_players(client):
    response = client.get("/players")

    assert response.status_code == 200
    assert len(response.json()) == 19


def test_obtem_jogador_por_id(client):
    response = client.get("/jogadores/10")

    assert response.status_code == 200
    jogador = response.json()
    assert jogador["id"] == 10
    assert jogador["nome"] == "Felipe Duarte"
    assert jogador["valor"] == 12_500_000
    assert jogador["rating"] == 90


def test_get_alias_player_por_id(client):
    response = client.get("/players/2")

    assert response.status_code == 200
    assert response.json()["nome"] == "Caio Martins"


def test_jogador_inexistente_retorna_404(client):
    response = client.get("/jogadores/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Jogador nao encontrado."


# -- Transferencias -----------------------------------------------------------

def test_compra_e_venda_de_jogador(client):
    compra = client.post("/jogadores/1/buy", json={"clube_id": 42})

    assert compra.status_code == 200
    comprado = compra.json()
    assert comprado["status"] == "COMPRADO"
    assert comprado["clube_id"] == 42

    venda = client.post("/jogadores/1/sell", json={"clube_id": 42})

    assert venda.status_code == 200
    vendido = venda.json()
    assert vendido["status"] == "DISPONIVEL"
    assert vendido["clube_id"] is None


def test_compra_e_venda_por_alias_players(client):
    compra = client.post("/players/2/buy", json={"clube_id": 7})

    assert compra.status_code == 200
    assert compra.json()["clube_id"] == 7

    venda = client.post("/players/2/sell", json={"clube_id": 7})

    assert venda.status_code == 200
    assert venda.json()["status"] == "DISPONIVEL"


def test_vende_jogador_sem_body(client):
    client.post("/jogadores/3/buy", json={"clube_id": 11})

    response = client.post("/jogadores/3/sell")

    assert response.status_code == 200
    assert response.json()["status"] == "DISPONIVEL"
    assert response.json()["clube_id"] is None


def test_nao_compra_jogador_ja_comprado(client):
    client.post("/jogadores/4/buy", json={"clube_id": 7})

    response = client.post("/jogadores/4/buy", json={"clube_id": 8})

    assert response.status_code == 409
    assert response.json()["detail"] == "Jogador ja pertence ao clube 7."


def test_nao_compra_jogador_inexistente(client):
    response = client.post("/jogadores/999/buy", json={"clube_id": 1})

    assert response.status_code == 404
    assert response.json()["detail"] == "Jogador nao encontrado."


def test_nao_compra_com_clube_id_invalido(client):
    response = client.post("/jogadores/5/buy", json={"clube_id": 0})

    assert response.status_code == 422


def test_nao_vende_jogador_disponivel(client):
    response = client.post("/jogadores/6/sell", json={"clube_id": 1})

    assert response.status_code == 409
    assert response.json()["detail"] == "Jogador ja esta disponivel para compra."


def test_nao_vende_jogador_de_outro_clube(client):
    client.post("/jogadores/7/buy", json={"clube_id": 7})

    response = client.post("/jogadores/7/sell", json={"clube_id": 8})

    assert response.status_code == 409
    assert response.json()["detail"] == "Jogador pertence a outro clube."


def test_nao_vende_jogador_inexistente(client):
    response = client.post("/jogadores/999/sell", json={"clube_id": 1})

    assert response.status_code == 404
    assert response.json()["detail"] == "Jogador nao encontrado."
