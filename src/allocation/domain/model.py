from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Set, NewType

from src.allocation.domain import events, commands


Quantity = NewType("Quantity", int)
Sku = NewType("Sku", str)
Reference = NewType("Reference", str)


class OutOfStock(Exception):
    pass


class Product:
    def __init__(self, sku: str, batches: list[Batch], version_number: int = 0):
        from src.allocation.service_layer.messagebus import Message

        self.sku = sku
        self.batches = batches
        self.version_number = version_number
        self.events: list[Message] = []

    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
            self.version_number += 1
            self.events.append(
                events.Allocated(
                    orderid=line.orderid,
                    sku=line.sku,
                    qty=line.qty,
                    batchref=batch.reference,
                )
            )
            return batch.reference
        except StopIteration:
            self.events.append(events.OutOfStock(line.sku))
            return None

    def change_batch_quantity(self, ref: str, qty: int):
        batch = next(b for b in self.batches if b.reference == ref)
        batch.purchased_quantity = qty
        while batch.available_quantity < 0:
            line = batch.deallocate_one()
            self.events.append(events.Deallocated(line.orderid, line.sku, line.qty))


@dataclass(unsafe_hash=True)
class OrderLine:
    orderid: Reference
    sku: Sku
    qty: Quantity


@dataclass
class Batch:
    reference: str
    sku: str
    qty: int
    eta: Optional[date]
    purchased_quantity: int = field(init=False)
    allocations: Set[OrderLine] = field(default_factory=set)

    def __post_init__(self):
        self.purchased_quantity = self.qty

    def __repr__(self):
        return f"<Batch {self.reference}>"

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def __hash__(self):
        return hash(self.reference)

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self.allocations.add(line)

    def deallocate_one(self) -> OrderLine:
        return self.allocations.pop()

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self.allocations)

    @property
    def available_quantity(self) -> int:
        return self.purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
