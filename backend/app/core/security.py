from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt

class Security:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = secret_key
        self.algorithm = algorithm

    # Password hashing
    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        return self.pwd_context.verify(password, hashed)

    # JWT
    def create_access_token(self, data: dict, expires_delta: timedelta):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
