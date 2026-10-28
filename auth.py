from pwdlib import PasswordHash
import os
from datetime import UTC, datetime, timedelta

import jwt
from dotenv import load_dotenv
password_hash = PasswordHash.recommended()

load_dotenv()
SECRET_KEY = os.environ["SECRET_KEY"]


def create_token(user_id: int) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=60)
    claims = {"sub": str(user_id), "exp": expires}
    return jwt.encode(claims, SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> int:
    claims = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return int(claims["sub"])
