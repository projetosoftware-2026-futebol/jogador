import json
import os
from enum import Enum

from fastapi import Body, Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import JogadorModel


class Posicao(str, Enum):
    ATA = "ATA"
    PD = "PD"
    PE = "PE"
    MC = "MC"
    LD = "LD"
    LE = "LE"
    ZAG = "ZAG"
    GOL = "GOL"


class StatusJogador(str, Enum):
    DISPONIVEL = "DISPONIVEL"
    COMPRADO = "COMPRADO"


class Jogador(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    valor: int = Field(gt=0)
    rating: int = Field(ge=1, le=100)
    posicao: Posicao
    status: StatusJogador = StatusJogador.DISPONIVEL
    clube_id: int | None = None


class CompraJogadorRequest(BaseModel):
    clube_id: int = Field(gt=0)


class VendaJogadorRequest(BaseModel):
    clube_id: int | None = Field(default=None, gt=0)


REDIS_URL = os.getenv("REDIS_URL")
CACHE_KEY_JOGADORES = "jogadores:list"
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "60"))
redis_client = Redis.from_url(REDIS_URL, decode_responses=True) if REDIS_URL else None


app = FastAPI(
    title="Fut Manager - Jogador API",
    description="Servico responsavel pelo catalogo, compra e venda de jogadores.",
    version="0.1.0",
)


def buscar_jogador_ou_404(jogador_id: int, db: Session) -> JogadorModel:
    jogador = db.get(JogadorModel, jogador_id)
    if jogador is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jogador nao encontrado.",
        )

    return jogador


def _serialize_jogador(jogador: JogadorModel) -> dict[str, object]:
    return {
        "id": jogador.id,
        "nome": jogador.nome,
        "valor": jogador.valor,
        "rating": jogador.rating,
        "posicao": jogador.posicao,
        "status": jogador.status,
        "clube_id": jogador.clube_id,
    }


def get_cached_jogadores() -> list[dict[str, object]] | None:
    if redis_client is None:
        return None
    try:
        cached = redis_client.get(CACHE_KEY_JOGADORES)
        return json.loads(cached) if cached else None
    except RedisError:
        return None


def set_cached_jogadores(jogadores: list[dict[str, object]]) -> None:
    if redis_client is None:
        return
    try:
        redis_client.set(CACHE_KEY_JOGADORES, json.dumps(jogadores), ex=CACHE_TTL_SECONDS)
    except RedisError:
        pass


def invalidate_jogadores_cache() -> None:
    if redis_client is None:
        return
    try:
        redis_client.delete(CACHE_KEY_JOGADORES)
    except RedisError:
        pass


@app.get("/", tags=["sistema"])
def raiz() -> dict[str, str]:
    return {"servico": "jogador", "status": "online"}


@app.get("/health", tags=["sistema"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/jogadores", response_model=list[Jogador], tags=["jogadores"])
@app.get("/players", response_model=list[Jogador], tags=["jogadores"], include_in_schema=False)
def listar_jogadores(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    cached = get_cached_jogadores()
    if cached is not None:
        return cached

    jogadores = list(db.scalars(select(JogadorModel).order_by(JogadorModel.id)))
    result = [_serialize_jogador(jogador) for jogador in jogadores]
    set_cached_jogadores(result)
    return result


@app.get("/jogadores/{jogador_id}", response_model=Jogador, tags=["jogadores"])
@app.get(
    "/players/{jogador_id}",
    response_model=Jogador,
    tags=["jogadores"],
    include_in_schema=False,
)
def obter_jogador(jogador_id: int, db: Session = Depends(get_db)) -> JogadorModel:
    return buscar_jogador_ou_404(jogador_id, db)


@app.post(
    "/jogadores/{jogador_id}/buy",
    response_model=Jogador,
    tags=["transferencias"],
)
@app.post(
    "/players/{jogador_id}/buy",
    response_model=Jogador,
    tags=["transferencias"],
    include_in_schema=False,
)
def comprar_jogador(
    jogador_id: int,
    compra: CompraJogadorRequest,
    db: Session = Depends(get_db),
) -> JogadorModel:
    jogador = buscar_jogador_ou_404(jogador_id, db)
    if jogador.status == StatusJogador.COMPRADO.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Jogador ja pertence ao clube {jogador.clube_id}.",
        )

    jogador.status = StatusJogador.COMPRADO.value
    jogador.clube_id = compra.clube_id
    db.commit()
    db.refresh(jogador)
    invalidate_jogadores_cache()
    return jogador


@app.post(
    "/jogadores/{jogador_id}/sell",
    response_model=Jogador,
    tags=["transferencias"],
)
@app.post(
    "/players/{jogador_id}/sell",
    response_model=Jogador,
    tags=["transferencias"],
    include_in_schema=False,
)
def vender_jogador(
    jogador_id: int,
    venda: VendaJogadorRequest | None = Body(default=None),
    db: Session = Depends(get_db),
) -> JogadorModel:
    jogador = buscar_jogador_ou_404(jogador_id, db)
    if jogador.status == StatusJogador.DISPONIVEL.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Jogador ja esta disponivel para compra.",
        )

    if venda is not None and venda.clube_id is not None and venda.clube_id != jogador.clube_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Jogador pertence a outro clube.",
        )

    jogador.status = StatusJogador.DISPONIVEL.value
    jogador.clube_id = None
    db.commit()
    db.refresh(jogador)
    invalidate_jogadores_cache()
    return jogador
