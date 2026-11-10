from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_token
from app.db.init import connect


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing token")
    try:
        payload = decode_token(creds.credentials)
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token payload")

    conn = connect()
    try:
        row = conn.execute(
            """
            SELECT u.id, u.email, u.full_name, u.is_active, r.name
            FROM users u JOIN roles r ON r.id = u.role_id
            WHERE u.email = ?
            """,
            (email,),
        ).fetchone()
    finally:
        conn.close()

    if row is None or not row[3]:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")

    return {"id": row[0], "email": row[1], "full_name": row[2], "role": row[4]}


def require_role(*roles: str):
    def checker(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        if user["role"] not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user
    return checker