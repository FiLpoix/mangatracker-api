from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import User, ListEntry
from schemas import ListEntryCreate, ListEntryUpdate, ListEntryResponse
from auth import get_current_user
from services.anilist import search_media, get_media_by_id, get_media_type

router = APIRouter(prefix="/mangas", tags=["Mangás"])


# ──────────────────────────────────────────
# BUSCAR NA ANILIST
# ──────────────────────────────────────────

@router.get("/search")
async def search(
    title: str = Query(..., min_length=1, description="Título para buscar"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=25),
):
    """Busca obras na AniList por título"""
    data = await search_media(title, page, per_page)
    return data["Page"]


@router.get("/anilist/{anilist_id}")
async def get_anilist_detail(anilist_id: int):
    """Retorna os detalhes de uma obra específica da AniList"""
    data = await get_media_by_id(anilist_id)
    return data["Media"]


# ──────────────────────────────────────────
# LISTA DO USUÁRIO — CRUD
# ──────────────────────────────────────────

@router.get("/list", response_model=list[ListEntryResponse])
def get_my_list(
    status: Optional[str] = Query(default=None, description="Filtrar por status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna a lista completa do usuário logado, com filtro opcional por status"""
    query = db.query(ListEntry).filter(ListEntry.user_id == current_user.id)

    if status:
        query = query.filter(ListEntry.status == status.upper())

    return query.order_by(ListEntry.updated_at.desc()).all()


@router.post("/list", response_model=ListEntryResponse, status_code=status.HTTP_201_CREATED)
async def add_to_list(
    entry_data: ListEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adiciona uma obra à lista do usuário"""

    # Verifica se já está na lista
    existing = db.query(ListEntry).filter(
        ListEntry.user_id == current_user.id,
        ListEntry.anilist_id == entry_data.anilist_id,
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Essa obra já está na sua lista"
        )

    # Busca os dados da obra na AniList para pegar o media_type
    anilist_data = await get_media_by_id(entry_data.anilist_id)
    media = anilist_data["Media"]
    media_type = get_media_type(media["countryOfOrigin"])

    new_entry = ListEntry(
        user_id=current_user.id,
        anilist_id=entry_data.anilist_id,
        media_type=media_type,
        status=entry_data.status,
        current_chapter=entry_data.current_chapter,
        score=entry_data.score,
        notes=entry_data.notes,
        started_at=entry_data.started_at,
        completed_at=entry_data.completed_at,
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    return new_entry


@router.patch("/list/{entry_id}", response_model=ListEntryResponse)
def update_entry(
    entry_id: int,
    update_data: ListEntryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza uma entrada da lista (capítulo, status, nota, etc.)"""
    entry = db.query(ListEntry).filter(
        ListEntry.id == entry_id,
        ListEntry.user_id == current_user.id,
    ).first()

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrada não encontrada")

    # Atualiza apenas os campos enviados
    update_fields = update_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(entry, field, value)

    db.commit()
    db.refresh(entry)

    return entry


@router.delete("/list/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_list(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove uma obra da lista do usuário"""
    entry = db.query(ListEntry).filter(
        ListEntry.id == entry_id,
        ListEntry.user_id == current_user.id,
    ).first()

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrada não encontrada")

    db.delete(entry)
    db.commit()


@router.get("/list/{entry_id}", response_model=ListEntryResponse)
def get_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna os detalhes de uma entrada específica da lista"""
    entry = db.query(ListEntry).filter(
        ListEntry.id == entry_id,
        ListEntry.user_id == current_user.id,
    ).first()

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrada não encontrada")

    return entry