class CartEmptyError(Exception):
    """Корзина пользователя пуста — checkout невозможен."""


class ProductNotFoundError(Exception):
    def __init__(self, product_id: int) -> None:
        self.product_id = product_id
        super().__init__(f"Product with id {product_id} not found")


class CartItemNotFoundError(Exception):
    def __init__(self, product_id: int, *, detail: str | None = None) -> None:
        self.product_id = product_id
        self.detail = detail or "Cart item not found"
        super().__init__(self.detail)


class ProductUnavailableError(Exception):
    def __init__(self, product_id: int) -> None:
        self.product_id = product_id
        super().__init__(f"Product {product_id} is unavailable")


class NotEnoughStockError(Exception):
    def __init__(self, product_name: str) -> None:
        self.product_name = product_name
        super().__init__(f"Not enough stock for product {product_name}")


class ProductPriceMissingError(Exception):
    def __init__(self, product_name: str) -> None:
        self.product_name = product_name
        super().__init__(f"Product {product_name} has no price set")


class OrderNotFoundError(Exception):
    pass


class OrderLoadError(Exception):
    """Заказ создан, но не удалось перечитать из БД."""
