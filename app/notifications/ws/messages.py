from typing import Literal, TypedDict


class OrderCreatedMessage(TypedDict):
    type: Literal["order_created"]
    order_id: int
    status: str
    total_amount: str
