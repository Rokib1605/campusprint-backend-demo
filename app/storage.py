from dataclasses import dataclass, field

from fastapi import Request

from app.models import PrintOption, PrintOrder


@dataclass
class MemoryStore:
    """Temporary demo database: a new instance is used for each integration test."""

    options: dict[int, PrintOption] = field(default_factory=dict)
    orders: dict[int, PrintOrder] = field(default_factory=dict)
    next_option_id: int = 3
    next_order_id: int = 1

    @classmethod
    def seeded(cls) -> "MemoryStore":
        store = cls()
        store.options[1] = PrintOption(
            id=1, code="BW_A4", name="Black and white A4", category="PRINT",
            unit_price_bdt=2, available=True,
        )
        store.options[2] = PrintOption(
            id=2, code="SPIRAL", name="Spiral binding", category="BINDING",
            unit_price_bdt=35, available=True,
        )
        return store


def get_store(request: Request) -> MemoryStore:
    return request.app.state.store
