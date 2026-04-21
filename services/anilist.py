import httpx
from fastapi import HTTPException

ANILIST_URL = "https://graphql.anilist.co"


# ──────────────────────────────────────────
# BUSCAR OBRAS POR TÍTULO
# ──────────────────────────────────────────

async def search_media(title: str, page: int = 1, per_page: int = 10) -> dict:
    """Busca obras na AniList por título"""
    query = """
    query ($title: String, $page: Int, $perPage: Int) {
        Page(page: $page, perPage: $perPage) {
            pageInfo {
                total
                currentPage
                lastPage
                hasNextPage
            }
            media(search: $title, type: MANGA, sort: POPULARITY_DESC) {
                id
                title {
                    romaji
                    english
                    native
                }
                coverImage {
                    large
                    medium
                }
                status
                chapters
                volumes
                description(asHtml: false)
                averageScore
                genres
                countryOfOrigin
                startDate { year month day }
                endDate   { year month day }
            }
        }
    }
    """
    variables = {"title": title, "page": page, "perPage": per_page}
    return await _request(query, variables)


# ──────────────────────────────────────────
# BUSCAR OBRA PELO ID
# ──────────────────────────────────────────

async def get_media_by_id(anilist_id: int) -> dict:
    """Busca os detalhes de uma obra específica pelo ID da AniList"""
    query = """
    query ($id: Int) {
        Media(id: $id, type: MANGA) {
            id
            title {
                romaji
                english
                native
            }
            coverImage {
                large
                medium
            }
            status
            chapters
            volumes
            description(asHtml: false)
            averageScore
            genres
            countryOfOrigin
            startDate { year month day }
            endDate   { year month day }
        }
    }
    """
    return await _request(query, {"id": anilist_id})


# ──────────────────────────────────────────
# HELPER — faz a request para a AniList
# ──────────────────────────────────────────

async def _request(query: str, variables: dict) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                ANILIST_URL,
                json={"query": query, "variables": variables},
                timeout=10.0
            )
            response.raise_for_status()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="AniList API demorou demais para responder")
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=502, detail="Erro ao se comunicar com a AniList API")

    data = response.json()

    if "errors" in data:
        raise HTTPException(status_code=404, detail="Obra não encontrada na AniList")

    return data["data"]


# ──────────────────────────────────────────
# HELPER — determina o tipo da obra pelo país
# ──────────────────────────────────────────

def get_media_type(country_of_origin: str) -> str:
    mapping = {
        "JP": "MANGA",
        "KR": "MANHWA",
        "CN": "MANHUA",
    }
    return mapping.get(country_of_origin, "MANGA")