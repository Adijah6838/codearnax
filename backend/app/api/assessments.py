from datetime import datetime, timezone
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.deps import get_current_user, require_role
from app.db.init import connect

router = APIRouter(prefix="/assessments", tags=["assessments"])

class AssessmentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    starts_at: str  # ISO 8601 string
    ends_at: str    # ISO 8601 string
    challenge_ids: list[int]
    candidate_ids: list[int]

class AssessmentOut(BaseModel):
    id: int
    title: str
    status: str
    starts_at: str
    ends_at: str

@router.post("", response_model=AssessmentOut, status_code=201)
def create_assessment(
    body: AssessmentCreate,
    user: dict[str, Any] = Depends(require_role("Administrator", "AssessmentManager"))
) -> AssessmentOut:
    conn = connect()
    try:
        conn.execute("BEGIN")
        cur = conn.execute(
            "INSERT INTO assessments (title, manager_id, starts_at, ends_at, status) VALUES (?,?,?,?,?)",
            (body.title, user["id"], body.starts_at, body.ends_at, "Draft")
        )
        aid = cur.lastrowid
        
        for cid in body.challenge_ids:
            conn.execute("INSERT INTO assessment_challenges (assessment_id, challenge_id) VALUES (?,?)", (aid, cid))
            
        for cand_id in body.candidate_ids:
            conn.execute("INSERT INTO assessment_candidates (assessment_id, candidate_id) VALUES (?,?)", (aid, cand_id))
            
        conn.execute("COMMIT")
        row = conn.execute("SELECT id,title,status,starts_at,ends_at FROM assessments WHERE id=?", (aid,)).fetchone()
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()
    return AssessmentOut(id=row[0], title=row[1], status=row[2], starts_at=row[3], ends_at=row[4])

@router.get("", response_model=list[AssessmentOut])
def list_assessments(user: dict[str, Any] = Depends(get_current_user)) -> list[AssessmentOut]:
    conn = connect()
    try:
        if user["role"] == "Candidate":
            # Candidates only see assessments they are assigned to
            rows = conn.execute(
                """SELECT a.id, a.title, a.status, a.starts_at, a.ends_at 
                   FROM assessments a
                   JOIN assessment_candidates ac ON ac.assessment_id = a.id
                   WHERE ac.candidate_id = ? AND a.status != 'Draft'""", (user["id"],)
            ).fetchall()
        else:
            rows = conn.execute("SELECT id,title,status,starts_at,ends_at FROM assessments ORDER BY id DESC").fetchall()
    finally:
        conn.close()
    return [AssessmentOut(id=r[0], title=r[1], status=r[2], starts_at=r[3], ends_at=r[4]) for r in rows]

@router.post("/{aid}/start")
def start_assessment(aid: int, user: dict[str, Any] = Depends(require_role("Candidate"))) -> dict:
    conn = connect()
    try:
        row = conn.execute(
            "SELECT status, starts_at, ends_at FROM assessments WHERE id = ?", (aid,)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Assessment not found")
            
        now = datetime.now(timezone.utc)
        ends_at = datetime.fromisoformat(row[2].replace("Z", "+00:00"))
        if now > ends_at:
            raise HTTPException(400, "Assessment window has closed")

        conn.execute(
            "UPDATE assessment_candidates SET status = 'InProgress', started_at = ? WHERE assessment_id = ? AND candidate_id = ?",
            (now.isoformat(), aid, user["id"])
        )
        
        # Get assigned challenges
        challenges = conn.execute(
            """SELECT c.id, c.title, c.description, c.difficulty 
               FROM challenges c JOIN assessment_challenges ac ON ac.challenge_id = c.id 
               WHERE ac.assessment_id = ?""", (aid,)
        ).fetchall()
        
        return {
            "status": "Started",
            "time_remaining_seconds": (ends_at - now).total_seconds(),
            "challenges": [{"id": c[0], "title": c[1], "description": c[2], "difficulty": c[3]} for c in challenges]
        }
    finally:
        conn.close()