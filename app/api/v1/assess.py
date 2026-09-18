from fastapi import APIRouter, Depends, HTTPException

from app.agents.assessment_agent import finalize_assessment, grade_answer
from app.core.auth import get_current_user_id
from app.schemas.learn import QuizSubmission
from app.services.quiz_session_service import delete_quiz_session, get_quiz_session

router = APIRouter(prefix="/assess", tags=["assess"])


@router.post("/{quiz_id}/submit")
def submit_quiz(
    quiz_id: str, payload: QuizSubmission, user_id: str = Depends(get_current_user_id)
):
    session = get_quiz_session(quiz_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Quiz session not found or expired")
    if session["user_id"] != user_id:
        raise HTTPException(
            status_code=403, detail="This quiz belongs to a different user"
        )

    results = []
    for q, submitted in zip(session["questions"], payload.answers):
        grade = grade_answer(q["question"], q["expected_answer"], submitted)
        results.append({**q, "learner_answer": submitted, **grade})

    outcome = finalize_assessment(session["topic"], user_id, results)
    delete_quiz_session(quiz_id)
    return outcome
