from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AISuggestRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)


class AISuggestResponse(BaseModel):
    suggestion: str
    model: str
    generated_at: datetime