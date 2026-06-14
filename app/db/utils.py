from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.interfaces import LoaderOption

from app.db.session import Base


async def get_by_id[M: Base](
    db: AsyncSession,
    model: type[M],
    entity_id: int,
    *,
    extra_filters: tuple = (),
    options: tuple[LoaderOption, ...] = (),
) -> M | None:
    stmt = select(model).where(model.id == entity_id, *extra_filters)
    if options:
        stmt = stmt.options(*options)
    result = await db.scalars(stmt)
    return result.first()
