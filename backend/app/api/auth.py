import re
import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.init import connect


router = APIRouter(prefix="/auth", tags=["auth"])

VALID_ROLES = {"Administrator", "AssessmentManager", "Candidate"}


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=1, max_length=100)
    role: str = "Candidate"


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str


def _validate_password(pw: str) -> None:
    if not re.search(r"[A-Za-z]", pw):
        raise HTTPException(400, "Password must contain at least one letter")
    if not re.search(r"\d", pw):
        raise HTTPException(400, "Password must contain at least one digit")


@router.post("/register", response_model=UserOut, status_code=201)
def register(body: RegisterIn) -> UserOut:
    if body.role not in VALID_ROLES:
        raise HTTPException(400, "Invalid role")
    _validate_password(body.password)

    conn = connect()
    try:
        role_row = conn.execute(
            "SELECT id FROM roles WHERE name = ?", (body.role,)
        ).fetchone()
        if role_row is None:
            raise HTTPException(500, "Role not seeded")

        try:
            cur = conn.execute(
                "INSERT INTO users (email, password_hash, full_name, role_id) "
                "VALUES (?, ?, ?, ?)",
                (body.email.lower(), hash_password(body.password),
                 body.full_name, role_row[0]),
            )
        except sqlite3.IntegrityError:
            raise HTTPException(409, "Email already registered")

        new_id = cur.lastrowid
    finally:
        conn.close()

    return UserOut(
        id=new_id,
        email=body.email.lower(),
        full_name=body.full_name,
        role=body.role,
    )


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn) -> TokenOut:
    conn = connect()
    try:
        row = conn.execute(
            """
            SELECT u.password_hash, u.is_active, r.name
            FROM users u JOIN roles r ON r.id = u.role_id
            WHERE u.email = ?
            """,
            (body.email.lower(),),
        ).fetchone()
    finally:
        conn.close()

    if row is None or not row[1] or not verify_password(body.password, row[0]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

    return TokenOut(
        access_token=create_access_token(subject=body.email.lower(), role=row[2])
    )


@router.get("/me", response_model=UserOut)
def me(user: dict[str, Any] = Depends(get_current_user)) -> UserOut:
    return UserOut(**user)


@router.post("/logout")
def logout(_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, str]:
    return {"status": "logged_out"}