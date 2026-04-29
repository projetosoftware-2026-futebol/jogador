import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app import main
from app.models import JogadorModel


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


main.app.dependency_overrides[get_db] = override_get_db


client = TestClient(main.app)


def jogadores_para_teste() -> list[JogadorModel]:
    return [
        JogadorModel(id=1, nome="Rafael Nunes", valor=8500000, rating=84, posicao="GOL"),
        JogadorModel(id=2, nome="Caio Martins", valor=7400000, rating=81, posicao="LD"),
        JogadorModel(id=3, nome="Bruno Reis", valor=7800000, rating=82, posicao="LE"),
        JogadorModel(id=4, nome="Victor Rocha", valor=9000000, rating=85, posicao="ZAG"),
        JogadorModel(id=5, nome="Andre Torres", valor=8300000, rating=83, posicao="ZAG"),
        JogadorModel(id=6, nome="Lucas Menezes", valor=10000000, rating=87, posicao="MC"),
        JogadorModel(id=7, nome="Mateus Castro", valor=9200000, rating=85, posicao="MC"),
        JogadorModel(id=8, nome="Diego Ramos", valor=7900000, rating=82, posicao="MC"),
        JogadorModel(id=9, nome="Igor Almeida", valor=11000000, rating=88, posicao="PE"),
        JogadorModel(id=10, nome="Felipe Duarte", valor=12500000, rating=90, posicao="ATA"),
        JogadorModel(id=11, nome="Thiago Lima", valor=10800000, rating=87, posicao="PD"),
        JogadorModel(id=12, nome="Henrique Costa", valor=4100000, rating=73, posicao="GOL"),
        JogadorModel(id=13, nome="Renan Lopes", valor=5200000, rating=76, posicao="LD"),
        JogadorModel(id=14, nome="Pedro Vieira", valor=5600000, rating=77, posicao="LE"),
        JogadorModel(id=15, nome="Gustavo Barros", valor=6400000, rating=79, posicao="ZAG"),
        JogadorModel(id=16, nome="Marcos Freitas", valor=6900000, rating=80, posicao="MC"),
        JogadorModel(id=17, nome="Samuel Pires", valor=7600000, rating=81, posicao="PE"),
        JogadorModel(id=18, nome="Enzo Cardoso", valor=7100000, rating=80, posicao="PD"),
        JogadorModel(id=19, nome="Daniel Moreira", valor=8800000, rating=84, posicao="ATA"),
    ]


@pytest.fixture(autouse=True)
def resetar_banco():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add_all(jogadores_para_teste())
    db.commit()
    db.close()


def test_lista_todos_os_jogadores():
    resposta = client.get("/jogadores")

    assert resposta.status_code == 200
    jogadores = resposta.json()
    assert len(jogadores) == 19
    assert jogadores[0]["id"] == 1
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


def test_obtem_jogador_por_id():
    resposta = client.get("/jogadores/10")

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Felipe Duarte"


def test_jogador_inexistente_retorna_404():
    resposta = client.get("/jogadores/999")

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Jogador nao encontrado."


def test_compra_e_venda_de_jogador():
    compra = client.post("/jogadores/1/buy", json={"clube_id": 42})

    assert compra.status_code == 200
    assert compra.json()["status"] == "COMPRADO"
    assert compra.json()["clube_id"] == 42

    venda = client.post("/jogadores/1/sell", json={"clube_id": 42})

    assert venda.status_code == 200
    assert venda.json()["status"] == "DISPONIVEL"
    assert venda.json()["clube_id"] is None


def test_nao_compra_jogador_ja_comprado():
    client.post("/jogadores/2/buy", json={"clube_id": 7})

    resposta = client.post("/jogadores/2/buy", json={"clube_id": 8})

    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "Jogador ja pertence ao clube 7."


def test_nao_vende_jogador_de_outro_clube():
    client.post("/jogadores/3/buy", json={"clube_id": 7})

    resposta = client.post("/jogadores/3/sell", json={"clube_id": 8})

    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "Jogador pertence a outro clube."
