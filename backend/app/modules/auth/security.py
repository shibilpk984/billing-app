from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

# Change this in production
SECRET_KEY = "super-secret-key-change-this-later"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Password hashing
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Password verification
def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


# JWT creation
def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt