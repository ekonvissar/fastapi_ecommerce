from fastapi import status


class CatalogError(Exception):
    def __init__(
        self,
        detail: str,
        *,
        status_code: int = status.HTTP_404_NOT_FOUND,
    ) -> None:
        self.detail = detail
        self.status_code = status_code


class CategoryNotFoundError(CatalogError):
    def __init__(self) -> None:
        super().__init__("Category not found", status_code=status.HTTP_404_NOT_FOUND)


class ParentCategoryNotFoundError(CatalogError):
    def __init__(self) -> None:
        super().__init__(
            "Parent category not found",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class CategorySelfParentError(CatalogError):
    def __init__(self) -> None:
        super().__init__(
            "Category cannot be its own parent",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class CatalogProductNotFoundError(CatalogError):
    def __init__(self, detail: str = "Product not found") -> None:
        super().__init__(detail, status_code=status.HTTP_404_NOT_FOUND)


class InactiveCategoryError(CatalogError):
    def __init__(self, detail: str = "Category not found or inactive") -> None:
        super().__init__(detail, status_code=status.HTTP_400_BAD_REQUEST)


class InvalidPriceRangeError(CatalogError):
    def __init__(self) -> None:
        super().__init__(
            "min_price не может быть больше max_price",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ProductAccessDeniedError(CatalogError):
    def __init__(self, detail: str) -> None:
        super().__init__(detail, status_code=status.HTTP_403_FORBIDDEN)


class ReviewNotFoundError(CatalogError):
    def __init__(self) -> None:
        super().__init__("Review not found", status_code=status.HTTP_404_NOT_FOUND)


class InvalidImageTypeError(CatalogError):
    def __init__(self) -> None:
        super().__init__(
            "Only JPG, PNG or WebP images are allowed",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ImageTooLargeError(CatalogError):
    def __init__(self) -> None:
        super().__init__(
            "Image is too large",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
