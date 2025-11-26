from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.products import Product


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="category"
    )

    parent: Mapped[Optional["Category"]] = relationship(
        "Category", back_populates="children", remote_side="Category.id"
    )

    children: Mapped[list["Category"]] = relationship(
        "Category", back_populates="parent"
    )


# class Customer(Base):
#     __tablename__ = "customers"
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(100), nullable=False)
#     email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
#     orders: Mapped[List['Order']] = relationship(
#         'Order',
#         back_populates='customer',
#     )
#
#
# class Order(Base):
#     __tablename__ = 'orders'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     order_number: Mapped[str] = mapped_column(String(20),unique=True, nullable=False)
#     total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
#     customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'), nullable=False)
#     category: Mapped['Customer'] = relationship(
#         'Customer',
#         back_populates='orders',
#     )
