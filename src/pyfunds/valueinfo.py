import pandas as pd
import numpy as np


def _roi(x):
    return x[-1] / x[0]


class ValueInfo:
    df_values = None
    df_roi = None
    df_var = None

    def __init__(self, df_values):
        self.df_values = df_values
        pass

    def save_to_disk(self, filename):
        return self.df_values.to_parquet(filename)

    def read_from_dist(self, filename):
        self.df_values = pd.read_parquet(filename)

    def __calc_window_function(self, df, num_days, func):
        df_fund = df.sort_values(by='date', axis='index', ascending=True)
        cols = df_fund.columns[df_fund.columns != 'date']

        df_w = pd.concat([df_fund[col].rolling(window=num_days).apply(func, raw=True) for col in cols], axis=1)
        df_w = df_w.replace([np.inf, -np.inf], np.nan).dropna(how='all')
        return df_w

    def calc_roi_var(self, num_days=365):
        self.df_roi = self.__calc_window_function(self.df_values, num_days, _roi)
        self.df_var = self.__calc_window_function(self.df_roi, num_days, np.nanvar)
        return self.df_roi, self.df_var

    def calc_annual_return(self):
        df_roi = self.__calc_window_function(self.df_values, 365, _roi)
        df_annual_roi = df_roi.groupby(df_roi.index.year).last()
        return df_annual_roi

    def calc_annual_var(self, period_days=2):
        df_roi = self.__calc_window_function(self.df_values, period_days, _roi)
        df_annual_roi = df_roi.groupby(df_roi.index.year).var()
        return df_annual_roi
