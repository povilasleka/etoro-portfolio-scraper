from decimal import Decimal

import requests
from dataclasses import dataclass
from typing import List, Optional, Dict

from models import Position

PROFILE_DATA_REQUEST_URL = 'https://www.etoro.com/api/logininfo/v1.1/users'
INSTRUMENTS_REQUEST_URL = 'https://api.etorostatic.com/sapi/instrumentsmetadata/V1.1/instruments/bulk?bulkNumber=1&totalBulks=1'

def get_aggregated_positions_request_url(cid: int):
    return f"https://www.etoro.com/sapi/trade-data-real/live/public/portfolios?cid={cid}"

def get_public_positions_request_url(cid: int, instrument_id: int):
    return f"https://www.etoro.com/sapi/trade-data-real/live/public/positions?cid={cid}&InstrumentID={instrument_id}"


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


class InstrumentRepository:
    def __init__(self):
        response = requests.get(INSTRUMENTS_REQUEST_URL)
        data = response.json()

        self.instruments = {
            instrument['InstrumentID']: Instrument(
                display_name=instrument['InstrumentDisplayName'],
                symbol=instrument['SymbolFull']
            )
            for instrument in data['InstrumentDisplayDatas']
        }

    def get_instrument(self, instrument_id: int) -> Optional[Instrument]:
        return self.instruments.get(instrument_id)


def scrape_profile_cid(username: str):
    response = requests.get(f"{PROFILE_DATA_REQUEST_URL}/{username}")
    data = response.json()

    return data['realCID']


def scrape_aggregated_positions(cid: int) -> List[AggregatedPosition]:
    response = requests.get(get_aggregated_positions_request_url(cid))
    data = response.json()

    aggregated_positions = list(map(
        lambda position: AggregatedPosition(
            instrument_id=position['InstrumentID'],
            direction=position['Direction'],
            invested=Decimal(position['Invested']),
            net_profit=Decimal(position['NetProfit']),
            value=Decimal(position['Value']),
        ),
        data['AggregatedPositions']
    ))

    return aggregated_positions


def scrape_public_positions(portfolio):
    ir = InstrumentRepository()
    cid = scrape_profile_cid(portfolio.display_name)
    aggregated_positions = scrape_aggregated_positions(cid)

    all_positions = []
    for aggregated_position in aggregated_positions:
        url = get_public_positions_request_url(cid, aggregated_position.instrument_id)
        response = requests.get(url)
        data = response.json()

        positions = list(map(
            lambda position: Position(
                portfolio=portfolio,
                position_id=position['PositionID'],
                cid=position['CID'],
                instrument_id=position['InstrumentID'],
                open_datetime=position['OpenDateTime'],
                open_rate=position['OpenRate'],
                amount=position['Amount'],
                direction="Buy" if bool(position['IsBuy']) else "Sell",
                take_profit_rate=position['TakeProfitRate'],
                stop_loss_rate=position['StopLossRate'],
                display_name=ir.get_instrument(position['InstrumentID']).display_name,
                symbol=ir.get_instrument(position['InstrumentID']).symbol,
                leverage=position['Leverage']
            ),
            data['PublicPositions']
        ))

        all_positions.extend(positions)

    return all_positions