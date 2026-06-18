class InvalidTokenError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class EmailAlreadyRegisteredError(Exception):
    pass

class InvalidCredentialsError(Exception):
    pass

class InsufficientPermissions(Exception):
    pass

class CategoryNotFoundError(Exception):
    pass

class ProductNotFoundError(Exception):
    pass

class CategoryAlreadyExistsError(Exception):
    pass

class InsufficientStockError(Exception):
    pass