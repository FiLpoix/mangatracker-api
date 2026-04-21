from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Troca para a URL do seu banco em produção (ex: PostgreSQL no Supabase/Railway)
# Exemplo PostgreSQL: "postgresql://usuario:senha@host:5432/nome_do_banco"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./manga_tracker.db")

# O connect_args é necessário apenas para o SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency — usar nas rotas do FastAPI com Depends(get_db)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()