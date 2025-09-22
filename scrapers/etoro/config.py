BASE_URL = "https://www.etoro.com"
STATIC_API_URL = "https://api.etorostatic.com"

PROFILE_DATA_REQUEST_URL = f"{BASE_URL}/api/logininfo/v1.1/users"
INSTRUMENTS_REQUEST_URL = f"{STATIC_API_URL}/sapi/instrumentsmetadata/V1.1/instruments/bulk?bulkNumber=1&totalBulks=1"
AGGREGATED_POSITIONS_URL_TEMPLATE = f"{BASE_URL}/sapi/trade-data-real/live/public/portfolios?cid={{cid}}"
PUBLIC_POSITIONS_URL_TEMPLATE = f"{BASE_URL}/sapi/trade-data-real/live/public/positions?cid={{cid}}&InstrumentID={{instrument_id}}"

DIRECTION_BUY = "Buy"
DIRECTION_SELL = "Sell"