from app.core.exceptions import AppBaseException


class KVBaseException(AppBaseException):
    """Base for all KV-related errors"""
    code = "KV_ERROR"
    status_code = 400


class KVInvalidTTLError(KVBaseException):
    code = "KV_INVALID_TTL"

    def __init__(self):
        super().__init__("ttl_seconds must be positive")


class KVKeyNotFoundError(KVBaseException):
    code = "KV_KEY_NOT_FOUND"
    status_code = 404

    def __init__(self, key: str):
        super().__init__(f"Key '{key}' not found")


class KVKeyGenerationError(KVBaseException):
    code = "KV_KEY_GENERATION_FAILED"
    status_code = 503

    def __init__(self):
        super().__init__("Could not generate a unique key")


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
