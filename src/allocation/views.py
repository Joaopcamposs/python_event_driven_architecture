from sqlalchemy import text

from src.allocation.service_layer import unit_of_work


async def allocations(orderid: str, uow: unit_of_work.SqlAlchemyUnitOfWork):
    async with uow:
        results = await uow.session.execute(
            text(
                """
                SELECT sku, batchref FROM allocations_view WHERE orderid = :orderid
                """
            ),
            {"orderid": orderid},
        )

    return results.mappings().all()
