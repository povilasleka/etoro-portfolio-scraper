from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Instrument:
    display_name: str
    symbol: str


@dataclass
class AggregatedPosition:
    instrument_id: int
    direction: str
    invested: Decimal
    net_profit: Decimal
    value: Decimal