from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.reports import AIAssistantQuery, AIAssistantResponse
from backend.app.services.ai_assistant import ManufacturingAIAssistant
from backend.app.dependencies import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/assistant", tags=["AI Analytics Assistant"])

@router.post("/query", response_model=AIAssistantResponse)
def query_assistant(
    request: AIAssistantQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Answers manufacturing performance, downtime, and OEE questions
    using live database telemetry and deterministic root-cause analysis.
    """
    result = ManufacturingAIAssistant.answer_query(db, request.question)
    return result
