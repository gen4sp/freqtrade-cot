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

    @staticmethod
    def buy_strategy_generator(params: Dict[str, Any]) -> Callable:
        """
        Define the buy strategy parameters to be used by Hyperopt.
        """
        def compareFields(dt, fieldname, shift, ratio=1.034):
            return dt[fieldname]/dt[fieldname].shift(shift) > ratio
    
        def compareFieldsRev(dt, fieldname, shift, ratio=1.034):
            return dt[fieldname]/dt[fieldname].shift(shift) < ratio

        def populate_buy_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            """
            Based on TA indicators, populates the buy signal for the given dataframe
            :param dataframe: DataFrame populated with indicators
            :param metadata: Additional information, like the currently traded pair
            :return: DataFrame with buy column
            """
        
            dataframe.loc[(
                compareFields(dataframe, 'tema', 1, params['k1']) &
                compareFieldsRev(dataframe, 'ema50', 3, params['k2']) &
                (dataframe['volume'] > 0)),'buy'] = 1
            return dataframe

        return populate_buy_trend

    

    @staticmethod
    def indicator_space() -> List[Dimension]:
        """
        Define your Hyperopt space for searching buy strategy parameters.
        """
        return [
            Real(1, 1.1, name='k1'),
            Real(-1.1, -1, name='k2'),
            # Real(0, 2, name='e-ы'),
            # Real(-2, 2, name='a-r'),
            # Categorical([1.001, 1.01, 1.03, 1.07, 1.1, 1.24, 1.5], name='c-ratio'),
            # Categorical([1.001, 1.01, 1.03, 1.07, 1.1, 1.24 1.5], name='v-ratio')
            # Categorical([True, False], name='mfi-enabled'),
            # Categorical([True, False], name='fastd-enabled'),
            # Categorical([True, False], name='adx-enabled'),
            # Categorical(['ema10', 'ema5', 'tema'], name='avg'),
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