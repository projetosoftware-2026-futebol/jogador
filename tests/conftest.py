import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import main
from app.database import Base, get_db
from app.models import JogadorModel


def jogadores_para_teste() -> list[JogadorModel]:
    return [
        JogadorModel(id=1, nome="Rafael Nunes", valor=8_500_000, rating=84, posicao="GOL"),
        JogadorModel(id=2, nome="Caio Martins", valor=7_400_000, rating=81, posicao="LD"),
        JogadorModel(id=3, nome="Bruno Reis", valor=7_800_000, rating=82, posicao="LE"),
        JogadorModel(id=4, nome="Victor Rocha", valor=9_000_000, rating=85, posicao="ZAG"),
        JogadorModel(id=5, nome="Andre Torres", valor=8_300_000, rating=83, posicao="ZAG"),
        JogadorModel(id=6, nome="Lucas Menezes", valor=10_000_000, rating=87, posicao="MC"),
        JogadorModel(id=7, nome="Mateus Castro", valor=9_200_000, rating=85, posicao="MC"),
        JogadorModel(id=8, nome="Diego Ramos", valor=7_900_000, rating=82, posicao="MC"),
        JogadorModel(id=9, nome="Igor Almeida", valor=11_000_000, rating=88, posicao="PE"),
        JogadorModel(id=10, nome="Felipe Duarte", valor=12_500_000, rating=90, posicao="ATA"),
        JogadorModel(id=11, nome="Thiago Lima", valor=10_800_000, rating=87, posicao="PD"),
        JogadorModel(id=12, nome="Henrique Costa", valor=4_100_000, rating=73, posicao="GOL"),
        JogadorModel(id=13, nome="Renan Lopes", valor=5_200_000, rating=76, posicao="LD"),
        JogadorModel(id=14, nome="Pedro Vieira", valor=5_600_000, rating=77, posicao="LE"),
        JogadorModel(id=15, nome="Gustavo Barros", valor=6_400_000, rating=79, posicao="ZAG"),
        JogadorModel(id=16, nome="Marcos Freitas", valor=6_900_000, rating=80, posicao="MC"),
        JogadorModel(id=17, nome="Samuel Pires", valor=7_600_000, rating=81, posicao="PE"),
        JogadorModel(id=18, nome="Enzo Cardoso", valor=7_100_000, rating=80, posicao="PD"),
        JogadorModel(id=19, nome="Daniel Moreira", valor=8_800_000, rating=84, posicao="ATA"),
    ]


@pytest.fixture
def app():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    Base.metadata.create_all(bind=engine)
    with testing_session_local() as db:
        db.add_all(jogadores_para_teste())
        db.commit()

    main.app.dependency_overrides[get_db] = override_get_db
    yield main.app
    main.app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client
