from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# ──────────────────────────────────────────
# USER
# ──────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────
# AUTH / TOKEN
# ──────────────────────────────────────────

class LoginData(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ──────────────────────────────────────────
# LIST ENTRY — criar
# ──────────────────────────────────────────

class ListEntryCreate(BaseModel):
    anilist_id: int
    status: str = Field(default="PLANNED", pattern="^(READING|COMPLETED|PAUSED|PLANNED|DROPPED)$")
    current_chapter: int = Field(default=0, ge=0)
    score: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ──────────────────────────────────────────
# LIST ENTRY — atualizar (todos os campos opcionais)
# ──────────────────────────────────────────

class ListEntryUpdate(BaseModel):
    status: Optional[str] = Field(default=None, pattern="^(READING|COMPLETED|PAUSED|PLANNED|DROPPED)$")
    current_chapter: Optional[int] = Field(default=None, ge=0)
    score: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ──────────────────────────────────────────
# LIST ENTRY — resposta ao cliente
# ──────────────────────────────────────────

class ListEntryResponse(BaseModel):
    id: int
    anilist_id: int
    media_type: str
    status: str
    current_chapter: int
    score: Optional[float]
    notes: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True