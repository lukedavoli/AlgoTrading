import requests
import json

class Bittrex:
    def __init__(self):
        self.API_BASE_URL = 'https://api.bittrex.com/v3'

    ############################################################################
    #                               MARKETS                                    #
    ############################################################################
    """List markets available on the Bittrex exchange
    Returns: List of dictionaries of the format
    [
        {
            "symbol": "string",
            "baseCurrencySymbol": "string",
            "quoteCurrencySymbol": "string",
            "minTradeSize": "number (double)",
            "precision": "integer (int32)",
            "status": "string",
            "createdAt": "string (date-time)",
            "notice": "string",
            "prohibitedIn": [
            "string"
            ],
            "associatedTermsOfService": [
            "string"
            ],
            "tags": [
            "string"
            ]
        }
    ]
    Parameters:
    quote_currency - specify only markets bought with a particular quote currency
    """    
    def get_markets(self, quote_currency=None):
        request_url = '{base_url}/markets'.format(
            base_url=self.API_BASE_URL
        )
        response = requests.get(request_url)
        all_markets = json.loads(response.content)

        if quote_currency:
            desired_markets = self.specify_quote_currency(all_markets=all_markets, desired_qc=quote_currency)
            return desired_markets
        else:
            return all_markets
    

    """Retrieve information for a specific market.
    Returns: Dictionary of the format
    {
        "symbol": "string",
        "baseCurrencySymbol": "string",
        "quoteCurrencySymbol": "string",
        "minTradeSize": "number (double)",
        "precision": "integer (int32)",
        "status": "string",
        "createdAt": "string (date-time)",
        "notice": "string",
        "prohibitedIn": [
            "string"
        ],
        "associatedTermsOfService": [
            "string"
        ],
        "tags": [
            "string"
        ]
    }
    Parameters:
    symbol - the symbol for the desired market, usually of the format 'BTC-USDT'
    """
    def get_market(self, symbol):
        request_url = '{base_url}/markets/{marketSymbol}'.format(
            base_url=self.API_BASE_URL,
            marketSymbol=symbol
        )
        response = requests.get(request_url)
        market = json.loads(response.content)
        return market


    """List summaries of the last 24 hours of activity for all markets.
    Returns: List of dictionaries of the format
    [
        {
            "symbol": "string",
            "high": "number (double)",
            "low": "number (double)",
            "volume": "number (double)",
            "quoteVolume": "number (double)",
            "percentChange": "number (double)",
            "updatedAt": "string (date-time)"
        }
    ]
    Parameters:
    quote_currency - specify only markets bought with a particular currency
    """
    def get_markets_summaries(self, quote_currency=None):
        request_url = '{base_url}/markets/summaries'.format(
            base_url=self.API_BASE_URL
        )
        response = requests.get(request_url)
        all_markets = json.loads(response.content)

        if quote_currency:
            desired_markets = self.specify_quote_currency(all_markets=all_markets, desired_qc=quote_currency)
            return desired_markets
        else:
            return all_markets

    
    """Retrieve summary of the last 24 hours of activity for a specific market.
    Returns: Dictionary of the format
    {
        "symbol": "string",
        "high": "number (double)",
        "low": "number (double)",
        "volume": "number (double)",
        "quoteVolume": "number (double)",
        "percentChange": "number (double)",
        "updatedAt": "string (date-time)"
    }
    Parameters:
    symbol - the symbol for the desired market, usually of the format 'BTC-USDT'
    """
    def get_market_summary(self, symbol):
        request_url = '{base_url}/markets/{marketSymbol}/summary'.format(
            base_url=self.API_BASE_URL,
            marketSymbol=symbol
        )
        response = requests.get(request_url)
        summary = json.loads(response.content)
        return summary


    """List tickers for all markets.
    Returns: List of dictionaries of the format
    [
        {
            "symbol": "string",
            "lastTradeRate": "number (double)",
            "bidRate": "number (double)",
            "askRate": "number (double)"
        }
    ]
    Parameters:
    quote_currency - specify only markets bought with a particular currency
    """
    def get_markets_tickers(self, quote_currency=None):
        request_url = '{base_url}/markets/tickers'.format(
            base_url=self.API_BASE_URL
        )
        response = requests.get(request_url)
        all_markets = json.loads(response.content)

        if quote_currency:
            desired_markets = self.specify_quote_currency(all_markets=all_markets, desired_qc=quote_currency)
            return desired_markets
        else:
            return all_markets


    """Retrieve the ticker for a specific market.
    Returns: Dictionary of the format
    {
        "symbol": "string",
        "lastTradeRate": "number (double)",
        "bidRate": "number (double)",
        "askRate": "number (double)"
    }
    Parameters:
    symbol - the symbol for the desired market, usually of the format 'BTC-USDT'
    """
    def get_market_ticker(self, symbol):
        request_url = '{base_url}/markets/{marketSymbol}/ticker'.format(
            base_url=self.API_BASE_URL,
            marketSymbol=symbol
        )
        response = requests.get(request_url)
        ticker = json.loads(response.content)
        return ticker


    """Get recent candle data for a given market
    Returns: List of dictionaries of the format
    [
        {
            "startsAt": "string (date-time)",
            "open": "number (double)",
            "high": "number (double)",
            "low": "number (double)",
            "close": "number (double)",
            "volume": "number (double)",
            "quoteVolume": "number (double)"
        }
    ]
    Parameters:
    symbol - market symbol, usually of the form 'BTC-USDT'
    candle_type - can be either 'TRADE' or 'MIDPOINT'
    candle_interval - the amount of time encompassing each candle, may be either 'MINUTE_1', 'MINUTE_5', 'HOUR_1' or 'DAY_1'
    """  
    def get_recent_candles(self, symbol, candle_type, candle_interval):
        request_url = '{base_url}/markets/{marketSymbol}/candles/{candleType}/{candleInterval}/recent'.format(
            base_url=self.API_BASE_URL,
            marketSymbol=symbol,
            candleType=candle_type,
            candleInterval=candle_interval
        )
        response = requests.get(request_url)
        candles = json.loads(response.content)
        return candles


    """Get historical candle data for a given market
    Returns: List of dictionaries of the format
    [
        {
            "startsAt": "string (date-time)",
            "open": "number (double)",
            "high": "number (double)",
            "low": "number (double)",
            "close": "number (double)",
            "volume": "number (double)",
            "quoteVolume": "number (double)"
        }
    ]
    Parameters:
    symbol - market symbol, usually of the form 'BTC-USDT'
    candle_type - can be either 'TRADE' or 'MIDPOINT'
    candle_interval - the amount of time encompassing each candle, may be either 'MINUTE_1', 'MINUTE_5', 'HOUR_1' or 'DAY_1'
    """  
    def get_historical_candles(self, symbol, candle_type, candle_interval, year, month, day):
        request_url = '{base_url}/markets/{marketSymbol}/candles/{candleType}/{candleInterval}/historical/{year}/{month}/{day}'.format(
            base_url=self.API_BASE_URL,
            marketSymbol=symbol,
            candleType=candle_type,
            candleInterval=candle_interval,
            year=year, month=month, day=day
        )
        response = requests.get(request_url)
        candles = json.loads(response.content)
        return candles


    def specify_quote_currency(self, all_markets, desired_qc):
        desired_markets = []
        for market in all_markets:
            found_qc = market['symbol'].split('-')[1]
            if found_qc == desired_qc:
                desired_markets.append(market)
        return desired_markets



