import pytest

from src.allocation.domain import model
from src.allocation.adapters import repository


@pytest.mark.asyncio
async def test_get_by_batchref(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.SqlAlchemyRepository(session)
    b1 = model.Batch(reference="b1", sku="sku1", qty=100, eta=None)
    b2 = model.Batch(reference="b2", sku="sku1", qty=100, eta=None)
    b3 = model.Batch(reference="b3", sku="sku2", qty=100, eta=None)
    p1 = model.Product(sku="sku1", batches=[b1, b2])
    p2 = model.Product(sku="sku2", batches=[b3])
    await repo.add(p1)
    await repo.add(p2)
    assert await repo.get_by_batchref("b2") == p1
    assert await repo.get_by_batchref("b3") == p2
