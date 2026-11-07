import os
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from db import get_db
from models import UserRow

load_dotenv()
SECRET_KEY = os.environ["SECRET_KEY"]
password_hash = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)


def create_token(user_id: int) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=60)
    claims = {"sub": str(user_id), "exp": expires}
    return jwt.encode(claims, SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> int:
    claims = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return int(claims["sub"])


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> UserRow:
    not_authenticated = HTTPException(status_code=401, detail="not authenticated")
    if creds is None:
        raise not_authenticated
    try:
        user_id = decode_token(creds.credentials)
    except jwt.InvalidTokenError:
        raise not_authenticated
    user = db.get(UserRow, user_id)
    if user is None:
        raise not_authenticated
    return user


CurrentUser = Annotated[UserRow, Depends(get_current_user)]