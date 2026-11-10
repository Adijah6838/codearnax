import json
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.deps import get_current_user, require_role
from app.db.init import connect

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

class ConfigIn(BaseModel):
    visible: bool

@router.get("")
def get_leaderboard() -> list[dict[str, Any]]:
    conn = connect()
    try:
        # Check if leaderboard is globally visible
        config = conn.execute(
            "SELECT payload FROM system_events WHERE event_type = 'leaderboard_config' ORDER BY id DESC LIMIT 1"
        ).fetchone()
        
        # Default to true if no config exists
        is_visible = True
        if config:
            try:
                is_visible = json.loads(config[0]).get("visible", True)
            except:
                pass
                
        if not is_visible:
            raise HTTPException(403, "Leaderboard is currently hidden by the administrator")

        # Aggregate scores
        rows = conn.execute(
            """
            SELECT u.id, u.email, u.full_name, 
                   COALESCE(SUM(l.score), 0) as total_score,
                   COUNT(l.challenge_id) as challenges_completed
            FROM users u
            LEFT JOIN leaderboard l ON l.candidate_id = u.id
            WHERE u.role_id = 3
            GROUP BY u.id
            ORDER BY total_score DESC, challenges_completed DESC
            """
        ).fetchall()
        
        return [
            {
                "candidate_id": r[0],
                "email": r[1],
                "full_name": r[2],
                "total_score": r[3],
                "challenges_completed": r[4]
            }
            for r in rows
        ]
    finally:
        conn.close()

@router.post("/config")
def set_leaderboard_visibility(
    body: ConfigIn,
    user: dict[str, Any] = Depends(require_role("Administrator"))
) -> dict[str, Any]:
    conn = connect()
    try:
        payload = json.dumps({"visible": body.visible})
        conn.execute(
            "INSERT INTO system_events (event_type, payload) VALUES ('leaderboard_config', ?)",
            (payload,)
        )
        return {"status": "success", "visible": body.visible}
    finally:
        conn.close()