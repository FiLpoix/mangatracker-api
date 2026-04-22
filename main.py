from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models
from routers import routers_auth, mangas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Manga Tracker API",
    description="API para rastrear mangás, manhwas e manhuas",
    version="1.0.0"
)

# ──────────────────────────────────────────
# CORS
# ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://mangatracker-frontend.vercel.app'],  # Em produção, troque pelo domínio do seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────
# ROTAS
# ──────────────────────────────────────────
app.include_router(routers_auth.router)
app.include_router(mangas.router)


@app.get("/")
def root():
    return {"status": "online", "docs": "/docs"}