from fastapi import APIRouter, Depends, HTTPException

from app.agents.assessment_agent import finalize_assessment, grade_answer
from app.core.auth import get_current_user_id
from app.schemas.learn import QuizSubmission
from app.services.quiz_session_service import get_quiz_session, submit_quiz_session

router = APIRouter(prefix="/assess", tags=["assess"])


@router.get("/{quiz_id}")
def get_quiz(quiz_id: str, user_id: str = Depends(get_current_user_id)):
    session = get_quiz_session(quiz_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Quiz session not found")
    if session["user_id"] != user_id:
        raise HTTPException(
            status_code=403, detail="This quiz belongs to a different user"
        )

    if session["submitted"]:
        results = session["results"]
        correct = sum(r["correct"] for r in results)
        return {
            "submitted": True,
            "correct": correct,
            "total": len(results),
            "results": results,
        }
    return {
        "submitted": False,
        "questions": [{"question": q["question"]} for q in session["questions"]],
    }


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
    if session["submitted"]:
        raise HTTPException(
            status_code=409, detail="This quiz has already been submitted"
        )

    results = []
    for q, submitted_answer in zip(session["questions"], payload.answers):
        grade = grade_answer(q["question"], q["expected_answer"], submitted_answer)
        results.append({**q, "learner_answer": submitted_answer, **grade})

    outcome = finalize_assessment(session["topic"], user_id, results)
    submit_quiz_session(quiz_id, results)
    return outcome
