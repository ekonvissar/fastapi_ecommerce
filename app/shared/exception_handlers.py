from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.catalog.exceptions import CatalogError
from app.identity.exceptions import IdentityError
from app.shared.exceptions import (
    CartEmptyError,
    CartItemNotFoundError,
    NotEnoughStockError,
    OrderLoadError,
    OrderNotFoundError,
    ProductNotFoundError,
    ProductPriceMissingError,
    ProductUnavailableError,
)


def _json_error(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


async def cart_empty_handler(_request: Request, _exc: CartEmptyError) -> JSONResponse:
    return _json_error(status.HTTP_404_NOT_FOUND, "Cart is empty")


async def product_not_found_handler(
    _request: Request, exc: ProductNotFoundError
) -> JSONResponse:
    return _json_error(
        status.HTTP_404_NOT_FOUND,
        f"Product with id {exc.product_id} not found",
    )


async def cart_item_not_found_handler(
    _request: Request, exc: CartItemNotFoundError
) -> JSONResponse:
    return _json_error(status.HTTP_404_NOT_FOUND, exc.detail)


async def product_unavailable_handler(
    _request: Request, exc: ProductUnavailableError
) -> JSONResponse:
    return _json_error(
        status.HTTP_400_BAD_REQUEST,
        f"Product {exc.product_id} is unavailable",
    )


async def not_enough_stock_handler(
    _request: Request, exc: NotEnoughStockError
) -> JSONResponse:
    return _json_error(
        status.HTTP_400_BAD_REQUEST,
        f"Not enough stock for product {exc.product_name}",
    )


async def product_price_missing_handler(
    _request: Request, exc: ProductPriceMissingError
) -> JSONResponse:
    return _json_error(
        status.HTTP_400_BAD_REQUEST,
        f"Product {exc.product_name} has no price set",
    )


async def order_not_found_handler(
    _request: Request, _exc: OrderNotFoundError
) -> JSONResponse:
    return _json_error(status.HTTP_404_NOT_FOUND, "Order not found")


async def order_load_handler(_request: Request, _exc: OrderLoadError) -> JSONResponse:
    return _json_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to load order")


async def identity_error_handler(_request: Request, exc: IdentityError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


async def catalog_error_handler(_request: Request, exc: CatalogError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(CartEmptyError, cart_empty_handler)
    app.add_exception_handler(ProductNotFoundError, product_not_found_handler)
    app.add_exception_handler(CartItemNotFoundError, cart_item_not_found_handler)
    app.add_exception_handler(ProductUnavailableError, product_unavailable_handler)
    app.add_exception_handler(NotEnoughStockError, not_enough_stock_handler)
    app.add_exception_handler(ProductPriceMissingError, product_price_missing_handler)
    app.add_exception_handler(OrderNotFoundError, order_not_found_handler)
    app.add_exception_handler(OrderLoadError, order_load_handler)
    app.add_exception_handler(IdentityError, identity_error_handler)
    app.add_exception_handler(CatalogError, catalog_error_handler)
