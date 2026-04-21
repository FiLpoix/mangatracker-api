from sqlalchemy import (
    Column, Integer, String, Float, Text,
    DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


# ──────────────────────────────────────────
# STATUS de leitura possíveis
# ──────────────────────────────────────────
# READING   → Lendo
# COMPLETED → Completo
# PAUSED    → Pausado
# PLANNED   → Planejo ler
# DROPPED   → Abandonado


class User(Base):
    __tablename__ = "users"

    id               = Column(Integer, primary_key=True, index=True)
    username         = Column(String(50), unique=True, nullable=False, index=True)
    email            = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password  = Column(String, nullable=False)
    created_at       = Column(DateTime, default=datetime.utcnow)

    # Um usuário tem muitas entradas na lista
    entries = relationship("ListEntry", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"


class ListEntry(Base):
    """
    Representa uma obra na lista de um usuário.
    Os dados da obra em si (título, capa, etc.) são buscados
    na AniList API usando o anilist_id.
    """
    __tablename__ = "list_entries"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)

    # ID da obra na AniList — é com ele que buscamos título, capa, etc.
    anilist_id      = Column(Integer, nullable=False)

    # Tipo da obra — vem do campo countryOfOrigin da AniList:
    # JP → MANGA | KR → MANHWA | CN → MANHUA
    media_type      = Column(String(20), nullable=False)  # MANGA, MANHWA, MANHUA, NOVEL

    # Progresso de leitura
    status          = Column(String(20), nullable=False, default="PLANNED")
    current_chapter = Column(Integer, default=0, nullable=False)

    # Avaliação e notas pessoais
    score           = Column(Float, nullable=True)   # 0.0 a 10.0
    notes           = Column(Text, nullable=True)

    # Datas
    started_at      = Column(DateTime, nullable=True)
    completed_at    = Column(DateTime, nullable=True)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at      = Column(DateTime, default=datetime.utcnow)

    # Relacionamento com o usuário
    user = relationship("User", back_populates="entries")

    # Garante que o mesmo usuário não adicione a mesma obra duas vezes
    __table_args__ = (
        UniqueConstraint("user_id", "anilist_id", name="uq_user_anilist"),
    )

    def __repr__(self):
        return f"<ListEntry user_id={self.user_id} anilist_id={self.anilist_id} status={self.status}>"