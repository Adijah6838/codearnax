import json
import sqlite3
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.deps import get_current_user, require_role
from app.db.init import connect
from app.services.queue import queue


router = APIRouter(prefix="/submissions", tags=["submissions"])

VALID_LANGUAGES = {"python", "javascript", "cpp"}


class SubmitIn(BaseModel):
    challenge_id: int
    language: str
    source_code: str = Field(min_length=1, max_length=200_000)


class SubmissionOut(BaseModel):
    id: int
    user_id: int
    challenge_id: int
    language: str
    status: str
    submitted_at: str


class SubmissionDetailOut(SubmissionOut):
    source_code: str


def _to_out(row: tuple) -> SubmissionOut:
    return SubmissionOut(
        id=row[0], user_id=row[1], challenge_id=row[2],
        language=row[3], status=row[4], submitted_at=row[5],
    )


@router.post("", response_model=SubmissionOut, status_code=201)
def submit(
    body: SubmitIn,
    user: dict[str, Any] = Depends(require_role("Candidate")),
) -> SubmissionOut:
    if body.language not in VALID_LANGUAGES:
        raise HTTPException(400, f"language must be one of {VALID_LANGUAGES}")

    conn = connect()
    try:
        ch = conn.execute(
            "SELECT status, languages FROM challenges WHERE id = ?",
            (body.challenge_id,),
        ).fetchone()
        if ch is None:
            raise HTTPException(404, "Challenge not found")
        if ch[0] != "Published":
            raise HTTPException(400, "Challenge is not published")
        if body.language not in json.loads(ch[1]):
            raise HTTPException(400, "Language not allowed for this challenge")

        cur = conn.execute(
            "INSERT INTO submissions (user_id,challenge_id,language,source_code) "
            "VALUES (?,?,?,?)",
            (user["id"], body.challenge_id, body.language, body.source_code),
        )
        sid = cur.lastrowid
        row = conn.execute(
            "SELECT id,user_id,challenge_id,language,status,submitted_at "
            "FROM submissions WHERE id = ?",
            (sid,),
        ).fetchone()
    finally:
        conn.close()

    queue.enqueue(sid)
    return _to_out(row)


@router.get("", response_model=list[SubmissionOut])
def list_my(
    user: dict[str, Any] = Depends(get_current_user),
    challenge_id: Optional[int] = Query(default=None),
) -> list[SubmissionOut]:
    sql = ("SELECT id,user_id,challenge_id,language,status,submitted_at "
           "FROM submissions WHERE user_id = ?")
    params: list[Any] = [user["id"]]
    if challenge_id is not None:
        sql += " AND challenge_id = ?"
        params.append(challenge_id)
    sql += " ORDER BY id DESC"
    conn = connect()
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()
    return [_to_out(r) for r in rows]


@router.get("/{sid}", response_model=SubmissionDetailOut)
def get_submission(
    sid: int,
    user: dict[str, Any] = Depends(get_current_user),
) -> SubmissionDetailOut:
    conn = connect()
    try:
        row = conn.execute(
            "SELECT id,user_id,challenge_id,language,status,submitted_at,source_code "
            "FROM submissions WHERE id = ?",
            (sid,),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise HTTPException(404, "Submission not found")
    if user["role"] == "Candidate" and row[1] != user["id"]:
        raise HTTPException(403, "Not your submission")
    return SubmissionDetailOut(
        id=row[0], user_id=row[1], challenge_id=row[2], language=row[3],
        status=row[4], submitted_at=row[5], source_code=row[6],
    )


@router.get("/{sid}/logs")
def get_logs(
    sid: int,
    user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    conn = connect()
    try:
        row = conn.execute(
            "SELECT user_id FROM submissions WHERE id = ?", (sid,)
        ).fetchone()
        if row is None:
            raise HTTPException(404, "Submission not found")
        if user["role"] == "Candidate" and row[0] != user["id"]:
            raise HTTPException(403, "Not your submission")
        logs = conn.execute(
            "SELECT id,level,message,created_at FROM execution_logs "
            "WHERE submission_id = ? ORDER BY id",
            (sid,),
        ).fetchall()
    finally:
        conn.close()
    return [
        {"id": r[0], "level": r[1], "message": r[2], "created_at": r[3]}
        for r in logs
    ]


@router.get("/{sid}/results")
def get_results(
    sid: int,
    user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    conn = connect()
    try:
        row = conn.execute(
            "SELECT user_id FROM submissions WHERE id = ?", (sid,)
        ).fetchone()
        if row is None:
            raise HTTPException(404, "Submission not found")
        if user["role"] == "Candidate" and row[0] != user["id"]:
            raise HTTPException(403, "Not your submission")
            
        rows = conn.execute(
            """SELECT r.id, r.test_case_id, r.passed, r.duration_ms, r.memory_kb, r.exit_code, r.stderr 
               FROM execution_results r
               JOIN test_cases t ON t.id = r.test_case_id
               WHERE r.submission_id = ? ORDER BY r.id""",
            (sid,),
        ).fetchall()
    finally:
        conn.close()
        
    results = []
    for r in rows:
        res = {
            "id": r[0], "test_case_id": r[1], "passed": bool(r[2]),
            "duration_ms": r[3], "memory_kb": r[4], "exit_code": r[5]
        }
        # Only expose stderr and actual output to Admins/Managers. 
        # Candidates only get pass/fail to prevent reverse-engineering hidden tests.
        if user["role"] in ("Administrator", "AssessmentManager"):
            res["stderr"] = r[6]
            
        results.append(res)
    return results