from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.schemas.base import User

# from jose import jwt, JWTError

# from app.db.session import SessionLocal
# from app.core.config import settings
# from app.core.security import oauth2_scheme
# from app.core.exceptions import PermissionDeniedError
# from app.domain.users.models import User


# 1. Database Dependency
# def get_db() -> Generator:
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# 2. Auth Dependency
async def get_current_user(
        # db=Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> User:
    # try:
    #     payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    #     user_id: str = payload.get("sub")
    #     if user_id is None:
    #         raise PermissionDeniedError("Invalid token")
    # except JWTError:
    #     raise PermissionDeniedError("Could not validate credentials")

    # Logic to fetch user from DB goes here
    # user = user_service.get_by_id(db, user_id)
    # return user
    return User(id="5aae142fe4b0093640689914", username="dev_user")  # Placeholder
