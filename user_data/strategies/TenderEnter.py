# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement

# --- Do not remove these libs ---
import math
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy, merge_informative_pair
# from freqtrade.exchange import timeframe_to_minutes
# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
# from freqtrade.strategy.strategy_helper import merge_informative_pair

class TenderEnter(IStrategy):
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
    # minimal_roi = {
    #     "0": 0.21,
    #     "90": 0.14,
    #     "134": 0.05,
    #     "374": 0
    # }
    # minimal_roi = {
    #     "180":  0.2, # 5% after 240 min
    #     "200":  0.1,
    #     "240":  0.00,
    #     "0":  0.3 # 8% imidietly
    # }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    # stoploss = -0.4
    # stoploss = -0.32

    # Trailing stoploss
    # trailing_stop = True
    # trailing_stop_positive = 0.02
    # trailing_stop_positive_offset = 0.03
    # trailing_only_offset_is_reached = True
    # trailing_stop_positive = 0.02
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured
    
    # trailing_stop = True
    # trailing_stop_positive = 0.051
    # trailing_stop_positive_offset = 0.13
    # trailing_only_offset_is_reached = False

    # stoploss = -0.12
    stoploss = -0.31
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.022
    trailing_only_offset_is_reached = True

    # minimal_roi = {
    #     "0": 0.08,
    #     "90": 0.06,
    #     "120": 0.02,
    #     "360": 0
    # }
    minimal_roi = {
        "0": 0.34154,
        "53": 0.07596,
        "224": 0.02112,
        "382": 0
    }

    # Optimal timeframe for the strategy.
    timeframe = '15m'
    inf_tf = '15m' #timeframe of second line


    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = False

    # These values can be overridden in the "ask_strategy" section in the config.
    use_sell_signal = False
    sell_profit_only = False
    ignore_roi_if_buy_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 5
    
    
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
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
         return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame populated with indicators
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with buy column
        """
    
        dataframe.loc[(
            self.compareFields(dataframe, 'close', 1, 741, 68) &
            self.compareFields(dataframe, 'close', 5, 94, 103) &
            self.compareFields(dataframe, 'volume', 1, 52, 22) &
            self.compareFields(dataframe, 'volume', 5, 45, 157) &
            (dataframe['volume'] > 0)),'buy'] = 1
        return dataframe

    def compareFields(self, dt, fieldname, shift, ratio, w):
            shift2 = 0 if False else (shift-1)
            base_candle = dt[fieldname].shift(shift2) 
            trg_candle = dt[fieldname].shift(shift)
            aspect = trg_candle/base_candle
            weight_k = 1 - (w/100)
            return aspect*(w/100) >= (ratio/1000)

    # def calcAngle(self, p1, p2, delta_x) -> bool:
    #     delta_y = p2 - p1
    #     theta_radians = np.arctan2(delta_y, delta_x)
    #     return theta_radians < -0.900275

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