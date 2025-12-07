from datetime import datetime

from sqlalchemy import ForeignKey, Text, CheckConstraint, func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, default=None, nullable=True)
    comment_date: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    grade: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    __table_args__ = (
        CheckConstraint("grade >= 1 AND grade <=5", name="grade_check"),
    )

    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="review")
