# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement

# --- Do not remove these libs ---
from functools import reduce
from typing import Any, Callable, Dict, List

import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from skopt.space import Categorical, Dimension, Integer, Real  # noqa

from freqtrade.optimize.hyperopt_interface import IHyperOpt

# --------------------------------
# Add your lib to import here
import talib.abstract as ta  # noqa
import freqtrade.vendor.qtpylib.indicators as qtpylib


class AllPairs(IHyperOpt):
    """
    This is a Hyperopt template to get you started.

    More information in the documentation: https://www.freqtrade.io/en/latest/hyperopt/

    You should:
    - Add any lib you need to build your hyperopt.

    You must keep:
    - The prototypes for the methods: populate_indicators, indicator_space, buy_strategy_generator.

    The methods roi_space, generate_roi_table and stoploss_space are not required
    and are provided by default.
    However, you may override them if you need 'roi' and 'stoploss' spaces that
    differ from the defaults offered by Freqtrade.
    Sample implementation of these methods will be copied to `user_data/hyperopts` when
    creating the user-data directory using `freqtrade create-userdir --userdir user_data`,
    or is available online under the following URL:
    https://github.com/freqtrade/freqtrade/blob/develop/freqtrade/templates/sample_hyperopt_advanced.py.
    """
    stoploss = -0.12
    trailing_stop = True
    trailing_stop_positive = 0.051
    trailing_stop_positive_offset = 0.13
    trailing_only_offset_is_reached = False

    minimal_roi = {
        "0": 0.21,
        "90": 0.14,
        "120": 0.05,
        "360": 0
    }
    @staticmethod
    def buy_strategy_generator(params: Dict[str, Any]) -> Callable:
        """
        Define the buy strategy parameters to be used by Hyperopt.
        """
        def compareFields(dt, fieldname, size, ratio, w):
            res = 0
            for shift in range(1, size+1):
                base_candle = dt[fieldname].shift(shift-1) 
                trg_candle = dt[fieldname].shift(shift)
                aspect = trg_candle/base_candle
                res += aspect
            res = res/size    
            weight_k = 1 - (w/100)
            return res*(w/100) >= (ratio/1000)

        def populate_buy_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            """
            Based on TA indicators, populates the buy signal for the given dataframe
            :param dataframe: DataFrame populated with indicators
            :param metadata: Additional information, like the currently traded pair
            :return: DataFrame with buy column
            """
        
            dataframe.loc[(
                compareFields(dataframe, 'close', 1,  params['c-ratio1'], params['c-weight']) &
                compareFields(dataframe, 'close', params['c-size'], params['c-ratio2'], params['c-weight2']) &
                compareFields(dataframe, 'volume', 1, params['v-ratio1'], params['v-weight']) &
                compareFields(dataframe, 'volume', params['v-size'], params['v-ratio2'], params['v-weight2']) &
                (dataframe['volume'] > 0)),'buy'] = 1
            return dataframe

        return populate_buy_trend

    

    @staticmethod
    def indicator_space() -> List[Dimension]:
        """
        Define your Hyperopt space for searching buy strategy parameters.
        """
        return [
            Integer(1, 1000, name='c-ratio1'),
            Integer(1, 1000, name='c-ratio2'),
            Integer(0, 200, name='c-weight'),
            Integer(0, 200, name='c-weight2'),
            Categorical([2, 3,4,5,6], name='c-size'),
            
            Integer(1, 100, name='v-ratio1'),
            Integer(1, 1000, name='v-ratio2'),
            Integer(0, 200, name='v-weight'),
            Integer(0, 200, name='v-weight2'),
            Categorical([2, 3,4,5,6], name='v-size'),
            
            # Categorical([True, False], name='prevent-shift-base'),
            # Categorical([True, False], name='fastd-enabled'),
            # Categorical([True, False], name='adx-enabled'),
            # Categorical([True, False], name='rsi-enabled'),
            # Categorical(['bb_lower', 'macd_cross_signal', 'sar_reversal'], name='trigger')
        ]

    # @staticmethod
    # def sell_strategy_generator(params: Dict[str, Any]) -> Callable:
    #     """
    #     Define the sell strategy parameters to be used by Hyperopt.
    #     """
    #     def populate_sell_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
    #         """
    #         Sell strategy Hyperopt will build and use.
    #         """
    #         conditions = []

    #         # GUARDS AND TRENDS
    #         if params.get('sell-mfi-enabled'):
    #             conditions.append(dataframe['mfi'] > params['sell-mfi-value'])
    #         if params.get('sell-fastd-enabled'):
    #             conditions.append(dataframe['fastd'] > params['sell-fastd-value'])
    #         if params.get('sell-adx-enabled'):
    #             conditions.append(dataframe['adx'] < params['sell-adx-value'])
    #         if params.get('sell-rsi-enabled'):
    #             conditions.append(dataframe['rsi'] > params['sell-rsi-value'])

    #         # TRIGGERS
    #         if 'sell-trigger' in params:
    #             if params['sell-trigger'] == 'sell-bb_upper':
    #                 conditions.append(dataframe['close'] > dataframe['bb_upperband'])
    #             if params['sell-trigger'] == 'sell-macd_cross_signal':
    #                 conditions.append(qtpylib.crossed_above(
    #                     dataframe['macdsignal'], dataframe['macd']
    #                 ))
    #             if params['sell-trigger'] == 'sell-sar_reversal':
    #                 conditions.append(qtpylib.crossed_above(
    #                     dataframe['sar'], dataframe['close']
    #                 ))

    #         # Check that the candle had volume
    #         conditions.append(dataframe['volume'] > 0)

    #         if conditions:
    #             dataframe.loc[
    #                 reduce(lambda x, y: x & y, conditions),
    #                 'sell'] = 1

    #         return dataframe

    #     return populate_sell_trend

    # @staticmethod
    # def sell_indicator_space() -> List[Dimension]:
    #     """
    #     Define your Hyperopt space for searching sell strategy parameters.
    #     """
    #     return [
    #         Integer(75, 100, name='sell-mfi-value'),
    #         Integer(50, 100, name='sell-fastd-value'),
    #         Integer(50, 100, name='sell-adx-value'),
    #         Integer(60, 100, name='sell-rsi-value'),
    #         Categorical([True, False], name='sell-mfi-enabled'),
    #         Categorical([True, False], name='sell-fastd-enabled'),
    #         Categorical([True, False], name='sell-adx-enabled'),
    #         Categorical([True, False], name='sell-rsi-enabled'),
    #         Categorical(['sell-bb_upper',
    #                      'sell-macd_cross_signal',
    #                      'sell-sar_reversal'], name='sell-trigger')
    #     ]