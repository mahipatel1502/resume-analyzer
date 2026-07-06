from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.models.ats import ATSScoreRequest, ATSScoreResponse
from app.services.ats_score_service import ATSScoreService


router = APIRouter(tags=["ATS"], dependencies=[Depends(get_current_user)])
ats_score_service = ATSScoreService()


@router.post("/ats-score", response_model=ATSScoreResponse)
def score_resume(request: ATSScoreRequest, current_user: dict[str, object] = Depends(get_current_user)) -> ATSScoreResponse:
    return ats_score_service.score_resume(request, int(current_user["id"]))
