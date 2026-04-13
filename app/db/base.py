# The "Master List" / "Alembic Manifest" where you import all models for Alembic

# Import the Base for Alembic
# from app.core.models import Base  # Your SQLAlchemy DeclarativeBase
# from app.domain.kv.models import KVModel
# from app.domain.users.models import User
# from app.domain.common.models import SharedTag


# Import every model in the app so Alembic "sees" them

# Then, In your alembic/env.py, you simply point to this file:
# target_metadata = app.db.base.Base.metadata
