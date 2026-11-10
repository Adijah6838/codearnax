from typing import Any
from fastapi import APIRouter, Depends

from app.core.deps import require_role
from app.db.init import connect

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/overview")
def get_overview(user: dict[str, Any] = Depends(require_role("Administrator", "AssessmentManager"))) -> dict[str, Any]:
    conn = connect()
    try:
        total_challenges = conn.execute("SELECT COUNT(*) FROM challenges").fetchone()[0]
        total_submissions = conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
        accepted = conn.execute("SELECT COUNT(*) FROM submissions WHERE status = 'Accepted'").fetchone()[0]
        failed = total_submissions - accepted
        
        avg_time_row = conn.execute("SELECT AVG(duration_ms) FROM execution_results").fetchone()
        avg_time = round(avg_time_row[0], 2) if avg_time_row[0] else 0.0
        
        return {
            "total_challenges": total_challenges,
            "total_submissions": total_submissions,
            "accepted_submissions": accepted,
            "failed_submissions": failed,
            "average_execution_ms": avg_time
        }
    finally:
        conn.close()

@router.get("/languages")
def get_languages(user: dict[str, Any] = Depends(require_role("Administrator", "AssessmentManager"))) -> dict[str, int]:
    conn = connect()
    try:
        rows = conn.execute("SELECT language, COUNT(*) FROM submissions GROUP BY language").fetchall()
        return {row[0]: row[1] for row in rows}
    finally:
        conn.close()

@router.get("/failures")
def get_failures(user: dict[str, Any] = Depends(require_role("Administrator", "AssessmentManager"))) -> dict[str, int]:
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT status, COUNT(*) FROM submissions WHERE status != 'Accepted' GROUP BY status"
        ).fetchall()
        return {row[0]: row[1] for row in rows}
    finally:
        conn.close()

@router.get("/completion")
def get_completion(user: dict[str, Any] = Depends(require_role("Administrator", "AssessmentManager"))) -> list[dict[str, Any]]:
    conn = connect()
    try:
        # Get completion rate per challenge (percentage of submissions that were accepted)
        rows = conn.execute(
            """
            SELECT c.id, c.title,
                   COUNT(s.id) as total_submissions,
                   SUM(CASE WHEN s.status = 'Accepted' THEN 1 ELSE 0 END) as accepted
            FROM challenges c
            LEFT JOIN submissions s ON s.challenge_id = c.id
            GROUP BY c.id
            ORDER BY total_submissions DESC
            """
        ).fetchall()
        
        results = []
        for r in rows:
            total = r[2]
            acc = r[3] or 0
            rate = (acc / total * 100) if total > 0 else 0
            results.append({
                "challenge_id": r[0],
                "title": r[1],
                "total_submissions": total,
                "accepted": acc,
                "completion_rate": round(rate, 1)
            })
        return results
    finally:
        conn.close()