from fastapi import APIRouter, Depends
from app.schemas.ai import AISuggestRequest, AISuggestResponse
from app.services.ai_service import generate_suggestion
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/suggest", response_model=AISuggestResponse)
async def ai_suggest(
    body: AISuggestRequest,
    current_user: User = Depends(get_current_user),
):
    result = await generate_suggestion(body.title)
    return AISuggestResponse(**result)