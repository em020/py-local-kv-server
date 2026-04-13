class AppBaseException(Exception):
    """Parent for all custom app exceptions."""
    def __init__(self, message: str = "An internal error occurred"):
        self.message = message
        super().__init__(self.message)

class EntityNotFoundError(AppBaseException):
    """Raised when a requested resource doesn't exist."""
    def __init__(self, entity_name: str, entity_id: str):
        self.entity_name = entity_name
        self.entity_id = entity_id
        super().__init__(f"{entity_name} with id {entity_id} not found.")

class PermissionDeniedError(AppBaseException):
    """Raised when a user lacks the required scope/role."""
    pass