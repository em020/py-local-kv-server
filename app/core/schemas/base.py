from pydantic import BaseModel


class User(BaseModel):
    """Represents the current authenticated user."""

    id: str
    username: str
