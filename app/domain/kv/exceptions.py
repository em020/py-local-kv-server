from app.core.exceptions import AppBaseException


class KVBaseException(AppBaseException):
    """Base for all KV-related errors"""
    code = "KV_ERROR"


# class KVStorageLimitReachedError(KVBaseException):
#     code = "KV_LIMIT_EXCEEDED"
#
#     def __init__(self, limit: int):
#         self.limit = limit
#         self.message = f"You have reached your limit of {limit} keys."
#         super().__init__(self.message)
#
#
# class InvalidKeyFormatError(KVBaseException):
#     code = "KV_INVALID_FORMAT"
#
#     def __init__(self, key: str):
#         self.key = key
#         self.message = f"The key '{key}' contains illegal characters."
#         super().__init__(self.message)
