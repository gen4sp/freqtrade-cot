# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement

# --- Do not remove these libs ---
import math
import numpy as np  # noqa
import pandas as pd  # noqa
import json
from pandas import DataFrame
from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy, merge_informative_pair
# from freqtrade.exchange import timeframe_to_minutes
# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
# from freqtrade.strategy.strategy_helper import merge_informative_pair
import os

def readTimeline():
    cwd = os.getcwd()
    
    with open('user_data/data/pump/timeline.json') as json_file:
        data = json.load(json_file)
        # for p in data:
            # print(p['t'])
            # print('')
        return data    

timeline = readTimeline()
class Pump(IStrategy):
    """
    This is a strategy template to get you started.
    More information in https://github.com/freqtrade/freqtrade/blob/develop/docs/bot-optimization.md

    You can:
        :return: a Dataframe with all mandatory indicators for the strategies
    - Rename the class name (Do not forget to update class_name)
    - Add any methods you want to build your strategy
    - Add any lib you need to build your strategy

    You must keep:
    - the lib in the section "Do not remove these libs"
    - the prototype for the methods: minimal_roi, stoploss, populate_indicators, populate_buy_trend,
    populate_sell_trend, hyperopt_space, buy_strategy_generator
    """
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 2

    custom_stops = {}
    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    # minimal_roi = {
    #     "180":  0.05, # 5% after 240 min
    #     "200":  0.03,
    #     "240":  0.00,
    #     "0":  0.08 # 8% imidietly
    # }
    # ROI table:
    minimal_roi = {
        "0": 0.15,
        "180": 0.1,
        "360": 0.05,
        "512": 0
        # "0": 100
    }

    # Stoploss:
    stoploss = -0.05

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.05
    trailing_stop_positive_offset = 0.8
    trailing_only_offset_is_reached = False
    # minimal_roi = {
    #     "180":  0.2, # 5% after 240 min
    #     "200":  0.1,
    #     "240":  0.00,
    #     "0":  0.3 # 8% imidietly
    # }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    # stoploss = -0.4
    # stoploss = -0.03

    # Trailing stoploss
    # trailing_stop = True
    # trailing_stop_positive = 0.02
    # trailing_stop_positive_offset = 0.03
    # trailing_only_offset_is_reached = True
    # trailing_stop_positive = 0.02
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured
    # trailing_stop = True
    # trailing_stop_positive = 0.02
    # trailing_stop_positive_offset = 0.06
    # trailing_only_offset_is_reached = True

    # Optimal timeframe for the strategy.
    timeframe = '5m'
    inf_tf = '5m' #timeframe of second line


    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = False

    # These values can be overridden in the "ask_strategy" section in the config.
    use_sell_signal = False
    sell_profit_only = False
    ignore_roi_if_buy_signal = True

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 0
    
    
    # Optional order type mapping.
    order_types = {
        'buy': 'market',
        'sell': 'market',
        'stoploss': 'market',
        'stoploss_on_exchange': True
    }

    # Optional order time in force.
    order_time_in_force = {
        'buy': 'gtc',
        'sell': 'gtc'
    }
    

    
    plot_config = {
        # Main plot indicators (Moving averages, ...)
        'main_plot': {
            'tema': {},
            'sar': {'color': 'white'},
        },
        'subplots': {
            # Subplots - each dict defines one additional plot
            "MACD": {
                'macd': {'color': 'blue'},
                'macdsignal': {'color': 'orange'},
            },
            "RSI": {
                'rsi': {'color': 'red'},
            }
        }
    }
    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        
        # return [(metadata['pair'], "15m")]
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        :param dataframe: Dataframe with data from the exchange
        :param metadata: Additional information, like the currently traded pair
        :return: a Dataframe with all mandatory indicators for the strategies
        """
        # pairs = self.dp.current_whitelist()
        
        # self.custom_stops = {pair: False for pair in pairs}
        # for pair in pairs:
        #     vals = {}
        #     vals[pair]=False
        #     arr.append(vals)
        #     self.stopsByPair = [{pair: False} for pair in pairs]
        # print('TT', metadata['pair'])    
        # Momentum Indicators
        # ------------------------------------

        # ADX
        # dataframe['adx'] = ta.ADX(dataframe)
        sym = metadata['pair'].split('/')[0]
        data = [True if (item['symbols'] and sym in item['symbols']) else False for item in timeline] 
        dataframe['pump'] = pd.DataFrame(data) 
        
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame populated with indicators
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with buy column
        """
        # params = {
        #     'c-ratio': 0.37954,
        #     'c-k': 0.1,
        #     'v-ratio': 1.94154,
        #     'v-k': 0.5,
        #     'avg-ratio': 5
        # }
    
        dataframe.loc[(
            dataframe['pump'] &
            (dataframe['volume'] > 0)),'buy'] = 1
        return dataframe

    

    # def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
    #                         time_in_force: str, **kwargs) -> bool:
    #     print('z', metadata["pair"], self.custom_stops[metadata["pair"]])                    
    #     if self.custom_stops[metadata["pair"]] == False:
    #         self.custom_stops[metadata["pair"]] = True
    #         return True
    #     else:
    #         return False

    # def confirm_trade_exit(self, pair: str, trade, order_type: str, amount: float,
    #                        rate: float, time_in_force: str, sell_reason: str, **kwargs) -> bool:
    #     self.custom_stops[metadata["pair"]] = True
    #     return True

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        :param dataframe: DataFrame populated with indicators
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                # False
                # (dataframe['tema'] < dataframe['tema'].shift(1)) &  # Guard: tema is falling
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'sell'] = 0
        return dataframe
    
    # def merge_informative_pair(dataframe, informative, minutes, inf_tf, ffill):
    #     print('>>', inf_tf,ffill)
    #     # Shift date by 1 candle
    #     # This is necessary since the data is always the "open date"
    #     # and a 15m candle starting at 12:15 should not know the close of the 1h candle from 12:00 to 13:00
    #     minutes = timeframe_to_minutes(inf_tf)
    #     # Only do this if the timeframes are different:
    #     informative['date_merge'] = informative["date"] + pd.to_timedelta(minutes, 'm')

    #     # Rename columns to be unique
    #     informative.columns = [f"{col}_{inf_tf}" for col in informative.columns]
    #     # Assuming inf_tf = '1d' - then the columns will now be:
    #     # date_1d, open_1d, high_1d, low_1d, close_1d, rsi_1d

    #     # Combine the 2 dataframes
    #     # all indicators on the informative sample MUST be calculated before this point
    #     dataframe = pd.merge(dataframe, informative, left_on='date', right_on=f'date_merge_{inf_tf}', how='left')
    #     # FFill to have the 1d value available in every row throughout the day.
    #     # Without this, comparisons would only work once per day.
    #     dataframe = dataframe.ffill()
    #     return dataframe    