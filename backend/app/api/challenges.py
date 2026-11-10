import json
import sqlite3
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.deps import get_current_user, require_role
from app.db.init import connect


router = APIRouter(prefix="/challenges", tags=["challenges"])

VALID_DIFFICULTIES = {"Beginner", "Intermediate", "Advanced", "Expert"}
VALID_LANGUAGES = {"python", "javascript", "cpp"}
VALID_CATEGORIES = {
    "Arrays", "Strings", "Sorting", "Searching",
    "Dynamic programming", "Graph algorithms",
    "Data structures", "Mathematics", "Object-oriented programming",
}


class TestCaseIn(BaseModel):
    input: str
    expected_output: str
    is_hidden: bool = False
    weight: int = Field(default=1, ge=1)


class TestCaseOut(BaseModel):
    id: int
    challenge_id: int
    input: str
    expected_output: str
    is_hidden: bool
    weight: int


class ChallengeIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    difficulty: str
    category: str
    languages: list[str] = Field(min_length=1)
    input_spec: Optional[str] = None
    output_spec: Optional[str] = None
    constraints: Optional[str] = None
    examples: list[dict[str, Any]] = []
    time_limit_ms: int = Field(default=2000, ge=100, le=30000)
    memory_limit_mb: int = Field(default=256, ge=32, le=2048)
    test_cases: list[TestCaseIn] = []


class ChallengeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    category: Optional[str] = None
    languages: Optional[list[str]] = None
    input_spec: Optional[str] = None
    output_spec: Optional[str] = None
    constraints: Optional[str] = None
    examples: Optional[list[dict[str, Any]]] = None
    time_limit_ms: Optional[int] = None
    memory_limit_mb: Optional[int] = None


class ChallengeOut(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    category: str
    languages: list[str]
    input_spec: Optional[str]
    output_spec: Optional[str]
    constraints: Optional[str]
    examples: list[dict[str, Any]]
    time_limit_ms: int
    memory_limit_mb: int
    status: str
    created_by: int
    created_at: str


SELECT_COLS = (
    "id,title,description,difficulty,category,languages,input_spec,"
    "output_spec,constraints,examples,time_limit_ms,memory_limit_mb,"
    "status,created_by,created_at"
)


def _row_to_challenge(row: tuple) -> ChallengeOut:
    return ChallengeOut(
        id=row[0], title=row[1], description=row[2], difficulty=row[3],
        category=row[4], languages=json.loads(row[5]),
        input_spec=row[6], output_spec=row[7], constraints=row[8],
        examples=json.loads(row[9]) if row[9] else [],
        time_limit_ms=row[10], memory_limit_mb=row[11],
        status=row[12], created_by=row[13], created_at=row[14],
    )


def _validate(body: ChallengeIn) -> None:
    if body.difficulty not in VALID_DIFFICULTIES:
        raise HTTPException(400, f"difficulty must be one of {VALID_DIFFICULTIES}")
    if body.category not in VALID_CATEGORIES:
        raise HTTPException(400, f"category must be one of {VALID_CATEGORIES}")
    if not all(lang in VALID_LANGUAGES for lang in body.languages):
        raise HTTPException(400, f"languages must be subset of {VALID_LANGUAGES}")


def _get_or_404(conn: sqlite3.Connection, cid: int) -> tuple:
    row = conn.execute(
        f"SELECT {SELECT_COLS} FROM challenges WHERE id = ?", (cid,)
    ).fetchone()
    if row is None:
        raise HTTPException(404, "Challenge not found")
    return row


def _set_status(cid: int, new_status: str) -> ChallengeOut:
    conn = connect()
    try:
        cur = conn.execute(
            "UPDATE challenges SET status = ? WHERE id = ?", (new_status, cid)
        )
        if cur.rowcount == 0:
            raise HTTPException(404, "Challenge not found")
        row = _get_or_404(conn, cid)
    finally:
        conn.close()
    return _row_to_challenge(row)


@router.post("", response_model=ChallengeOut, status_code=201)
def create_challenge(
    body: ChallengeIn,
    user: dict[str, Any] = Depends(require_role("Administrator", "AssessmentManager")),
) -> ChallengeOut:
    _validate(body)
    conn = connect()
    try:
        conn.execute("BEGIN")
        cur = conn.execute(
            "INSERT INTO challenges (title,description,difficulty,category,languages,"
            "input_spec,output_spec,constraints,examples,time_limit_ms,memory_limit_mb,"
            "created_by) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (body.title, body.description, body.difficulty, body.category,
             json.dumps(body.languages), body.input_spec, body.output_spec,
             body.constraints, json.dumps(body.examples),
             body.time_limit_ms, body.memory_limit_mb, user["id"]),
        )
        cid = cur.lastrowid
        if body.test_cases:
            conn.executemany(
                "INSERT INTO test_cases (challenge_id,input,expected_output,is_hidden,weight) "
                "VALUES (?,?,?,?,?)",
                [(cid, tc.input, tc.expected_output, int(tc.is_hidden), tc.weight)
                 for tc in body.test_cases],
            )
        conn.execute("COMMIT")
        row = _get_or_404(conn, cid)
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()
    return _row_to_challenge(row)


@router.get("", response_model=list[ChallengeOut])
def list_challenges(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    difficulty: Optional[str] = None,
    category: Optional[str] = None,
    user: dict[str, Any] = Depends(get_current_user),
) -> list[ChallengeOut]:
    clauses: list[str] = []
    params: list[Any] = []
    if user["role"] == "Candidate":
        clauses.append("status = 'Published'")
    elif status_filter:
        clauses.append("status = ?")
        params.append(status_filter)
    if difficulty:
        clauses.append("difficulty = ?")
        params.append(difficulty)
    if category:
        clauses.append("category = ?")
        params.append(category)
    sql = f"SELECT {SELECT_COLS} FROM challenges"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY id DESC"
    conn = connect()
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()
    return [_row_to_challenge(r) for r in rows]


@router.get("/{cid}", response_model=ChallengeOut)
def get_challenge(
    cid: int,
    user: dict[str, Any] = Depends(get_current_user),
) -> ChallengeOut:
    conn = connect()
    try:
        row = _get_or_404(conn, cid)
    finally:
        conn.close()
    if user["role"] == "Candidate" and row[12] != "Published":
        raise HTTPException(403, "Challenge not available")
    return _row_to_challenge(row)


@router.patch("/{cid}", response_model=ChallengeOut)
def update_challenge(
    cid: int,
    body: ChallengeUpdate,
    user: dict[str, Any] = Depends(require_role("Administrator", "AssessmentManager")),
) -> ChallengeOut:
    updates = body.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(400, "No fields to update")
    if "languages" in updates:
        if not all(lang in VALID_LANGUAGES for lang in updates["languages"]):
            raise HTTPException(400, "Invalid language")
        updates["languages"] = json.dumps(updates["languages"])
    if "examples" in updates:
        updates["examples"] = json.dumps(updates["examples"])
    if "difficulty" in updates and updates["difficulty"] not in VALID_DIFFICULTIES:
        raise HTTPException(400, "Invalid difficulty")
    if "category" in updates and updates["category"] not in VALID_CATEGORIES:
        raise HTTPException(400, "Invalid category")
    set_sql = ", ".join(f"{k} = ?" for k in updates)
    params = list(updates.values()) + [cid]
    conn = connect()
    try:
        cur = conn.execute(f"UPDATE challenges SET {set_sql} WHERE id = ?", params)
        if cur.rowcount == 0:
            raise HTTPException(404, "Challenge not found")
        row = _get_or_404(conn, cid)
    finally:
        conn.close()
    return _row_to_challenge(row)


@router.delete("/{cid}", status_code=204)
def delete_challenge(
    cid: int,
    user: dict[str, Any] = Depends(require_role("Administrator")),
) -> None:
    conn = connect()
    try:
        cur = conn.execute("DELETE FROM challenges WHERE id = ?", (cid,))
        if cur.rowcount == 0:
            raise HTTPException(404, "Challenge not found")
    finally:
        conn.close()


@router.post("/{cid}/publish", response_model=ChallengeOut)
def publish_challenge(
    cid: int,
    user: dict[str, Any] = Depends(require_role("Administrator", "AssessmentManager")),
) -> ChallengeOut:
    return _set_status(cid, "Published")


@router.post("/{cid}/archive", response_model=ChallengeOut)
def archive_challenge(
    cid: int,
    user: dict[str, Any] = Depends(require_role("Administrator", "AssessmentManager")),
) -> ChallengeOut:
    return _set_status(cid, "Archived")


@router.post("/{cid}/test-cases", response_model=TestCaseOut, status_code=201)
def add_test_case(
    cid: int,
    body: TestCaseIn,
    user: dict[str, Any] = Depends(require_role("Administrator", "AssessmentManager")),
) -> TestCaseOut:
    conn = connect()
    try:
        _get_or_404(conn, cid)
        cur = conn.execute(
            "INSERT INTO test_cases (challenge_id,input,expected_output,is_hidden,weight) "
            "VALUES (?,?,?,?,?)",
            (cid, body.input, body.expected_output, int(body.is_hidden), body.weight),
        )
        tc_id = cur.lastrowid
    finally:
        conn.close()
    return TestCaseOut(id=tc_id, challenge_id=cid, **body.model_dump())


@router.get("/{cid}/test-cases", response_model=list[TestCaseOut])
def list_test_cases(
    cid: int,
    user: dict[str, Any] = Depends(require_role("Administrator", "AssessmentManager")),
) -> list[TestCaseOut]:
    conn = connect()
    try:
        _get_or_404(conn, cid)
        rows = conn.execute(
            "SELECT id, challenge_id, input, expected_output, is_hidden, weight "
            "FROM test_cases WHERE challenge_id = ? ORDER BY id",
            (cid,),
        ).fetchall()
    finally:
        conn.close()
    return [
        TestCaseOut(
            id=r[0], challenge_id=r[1], input=r[2], expected_output=r[3],
            is_hidden=bool(r[4]), weight=r[5],
        ) for r in rows
    ]


@router.delete("/{cid}/test-cases/{tc_id}", status_code=204)
def delete_test_case(
    cid: int,
    tc_id: int,
    user: dict[str, Any] = Depends(require_role("Administrator", "AssessmentManager")),
) -> None:
    conn = connect()
    try:
        cur = conn.execute(
            "DELETE FROM test_cases WHERE id = ? AND challenge_id = ?", (tc_id, cid)
        )
        if cur.rowcount == 0:
            raise HTTPException(404, "Test case not found")
    finally:
        conn.close()