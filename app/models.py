from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class JogadorModel(Base):
    __tablename__ = "jogadores"
    __table_args__ = (
        CheckConstraint("valor > 0", name="ck_jogadores_valor_positivo"),
        CheckConstraint("rating >= 1 AND rating <= 100", name="ck_jogadores_rating"),
        CheckConstraint(
            "posicao IN ('ATA', 'PD', 'PE', 'MC', 'LD', 'LE', 'ZAG', 'GOL')",
            name="ck_jogadores_posicao",
        ),
        CheckConstraint(
            "status IN ('DISPONIVEL', 'COMPRADO')",
            name="ck_jogadores_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    valor: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    posicao: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="DISPONIVEL",
    )
    clube_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
