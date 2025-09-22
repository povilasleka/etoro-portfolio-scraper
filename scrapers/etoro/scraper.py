from decimal import Decimal
from typing import List, Optional, Dict, Any
import requests
from database import Position
from .config import (
    PROFILE_DATA_REQUEST_URL,
    INSTRUMENTS_REQUEST_URL,
    AGGREGATED_POSITIONS_URL_TEMPLATE,
    PUBLIC_POSITIONS_URL_TEMPLATE,
    DIRECTION_BUY,
    DIRECTION_SELL
)
from .models import Instrument, AggregatedPosition


_instrument_cache: Optional[Dict[int, Instrument]] = None


def _load_all_instruments() -> Dict[int, Instrument]:
    response = requests.get(INSTRUMENTS_REQUEST_URL)
    response.raise_for_status()
    data = response.json()

    if 'InstrumentDisplayDatas' not in data:
        raise KeyError("InstrumentDisplayDatas not found in response")

    return {
        instrument['InstrumentID']: Instrument(
            display_name=instrument['InstrumentDisplayName'],
            symbol=instrument['SymbolFull']
        )
        for instrument in data['InstrumentDisplayDatas']
    }


def _get_instrument(instrument_id: int) -> Optional[Instrument]:
    global _instrument_cache
    if _instrument_cache is None:
        _instrument_cache = _load_all_instruments()
    return _instrument_cache.get(instrument_id)


def _create_aggregated_position(position_data: Dict[str, Any]) -> AggregatedPosition:
    return AggregatedPosition(
        instrument_id=position_data['InstrumentID'],
        direction=position_data['Direction'],
        invested=Decimal(str(position_data['Invested'])),
        net_profit=Decimal(str(position_data['NetProfit'])),
        value=Decimal(str(position_data['Value']))
    )


def _create_position(position_data: Dict[str, Any], portfolio) -> Position:
    instrument = _get_instrument(position_data['InstrumentID'])
    if not instrument:
        raise ValueError(f"Instrument not found for ID: {position_data['InstrumentID']}")

    return Position(
        portfolio=portfolio,
        position_id=position_data['PositionID'],
        cid=position_data['CID'],
        instrument_id=position_data['InstrumentID'],
        open_datetime=position_data['OpenDateTime'],
        open_rate=position_data['OpenRate'],
        amount=position_data['Amount'],
        direction=DIRECTION_BUY if bool(position_data['IsBuy']) else DIRECTION_SELL,
        take_profit_rate=position_data['TakeProfitRate'],
        stop_loss_rate=position_data['StopLossRate'],
        display_name=instrument.display_name,
        symbol=instrument.symbol,
        leverage=position_data['Leverage']
    )


def _fetch_positions_for_instrument(cid: int, instrument_id: int, portfolio) -> List[Position]:
    url = PUBLIC_POSITIONS_URL_TEMPLATE.format(cid=cid, instrument_id=instrument_id)
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    if 'PublicPositions' not in data:
        return []

    return [_create_position(pos, portfolio) for pos in data['PublicPositions']]


def scrape_profile_cid(username: str) -> int:
    if not username:
        raise ValueError("Username cannot be empty")

    response = requests.get(f"{PROFILE_DATA_REQUEST_URL}/{username}")
    response.raise_for_status()
    data = response.json()

    if 'realCID' not in data:
        raise KeyError(f"realCID not found in response for username: {username}")

    return data['realCID']


def scrape_aggregated_positions(cid: int) -> List[AggregatedPosition]:
    if not isinstance(cid, int) or cid <= 0:
        raise ValueError("CID must be a positive integer")

    response = requests.get(AGGREGATED_POSITIONS_URL_TEMPLATE.format(cid=cid))
    response.raise_for_status()
    data = response.json()

    if 'AggregatedPositions' not in data:
        raise KeyError("AggregatedPositions not found in response")

    return [_create_aggregated_position(pos) for pos in data['AggregatedPositions']]


def scrape_public_positions(portfolio) -> List[Position]:
    if not portfolio or not hasattr(portfolio, 'display_name'):
        raise ValueError("Portfolio must have a display_name attribute")

    cid = scrape_profile_cid(portfolio.display_name)
    aggregated_positions = scrape_aggregated_positions(cid)

    all_positions = []
    for aggregated_position in aggregated_positions:
        positions = _fetch_positions_for_instrument(
            cid, aggregated_position.instrument_id, portfolio
        )
        all_positions.extend(positions)

    return all_positions