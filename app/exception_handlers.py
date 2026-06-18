from fastapi.responses import JSONResponse

from app import exceptions

def register_exception_handlers(app):
     @app.exception_handler(exceptions.InvalidTokenError)
     def invalid_token(_, exc: exceptions.InvalidTokenError):
         return JSONResponse(status_code=401, content={"detail": str(exc)})

     @app.exception_handler(exceptions.UserNotFoundError)
     def user_not_found(_, exc: exceptions.UserNotFoundError):
         return JSONResponse(status_code=404, content={"detail": str(exc)})

     @app.exception_handler(exceptions.EmailAlreadyRegisteredError)
     def email_already_registered(_, exc: exceptions.EmailAlreadyRegisteredError):
         return JSONResponse(status_code=409, content={"detail": str(exc)})

     @app.exception_handler(exceptions.InvalidCredentialsError)
     def invalid_credentials(_, exc: exceptions.InvalidCredentialsError):
         return JSONResponse(status_code=401, content={"detail": str(exc)})

     @app.exception_handler(exceptions.InsufficientPermissions)
     def insufficient_permissions(_, exc: exceptions.InsufficientPermissions):
         return JSONResponse(status_code=403, content={"detail": str(exc)})

     @app.exception_handler(exceptions.CategoryNotFoundError)
     def category_not_found(_, exc:exceptions.CategoryNotFoundError):
         return JSONResponse(status_code=404, content={"detail": str(exc)})

     @app.exception_handler(exceptions.ProductNotFoundError)
     def product_not_found(_, exc:exceptions.ProductNotFoundError):
         return JSONResponse(status_code=404, content={"detail": str(exc)})

     @app.exception_handler(exceptions.CategoryAlreadyExistsError)
     def category_already_exists(_, exc:exceptions.CategoryAlreadyExistsError):
         return JSONResponse(status_code=409, content={"detail": str(exc)})

     @app.exception_handler(exceptions.InsufficientStockError)
     def insufficient_stock(_, exc:exceptions.InsufficientStockError):
         return JSONResponse(status_code=409, content={"detail": str(exc)})

     @app.exception_handler(exceptions.CartItemNotFoundError)
     def cart_item_not_found(_, exc: exceptions.CartItemNotFoundError):
         return JSONResponse(status_code=404, content={"detail": str(exc)})